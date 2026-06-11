"""Hybrid search pipeline for PandaSearch.

Implements the fixed search strategy:
  Query → Preprocess → Parallel (Vector + Fulltext + SQL filter)
  → RRF fusion → Pagination → Result assembly → Highlight → Response
"""

import time
from typing import Any, Optional

from pandasearch.api_models import (
    FilterOption,
    FiltersResponse,
    SearchRequest,
    SearchResponse,
    SearchResultItem,
    SuggestResponse,
    SuggestionItem,
)
from pandasearch.config import FieldConfig, SearchPluginConfig
from pandasearch.database import get_connection
from pandasearch.embedding import EmbeddingService


class SearchPipeline:
    """Hybrid search pipeline combining vector, fulltext and SQL filtering."""

    def __init__(
        self,
        config: SearchPluginConfig,
        embedding_service: EmbeddingService,
    ):
        self.config = config
        self.embedding_service = embedding_service
        self.table = config.data_source.table
        self.pk = config.data_source.primary_key or "id"
        self.fields: dict[str, FieldConfig] = config.fields or {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def search(self, request: SearchRequest) -> SearchResponse:
        """Execute a hybrid search and return a structured response."""
        start_time = time.perf_counter()
        query = request.query.strip()

        # 1. Query preprocessing
        vector_query, fulltext_query = self._preprocess_query(query)

        # 2. Build SQL filter clause (shared by both searches)
        # $1 is reserved for the query vector/text, so filters start at $2
        filter_clause, filter_values = self._build_filter_clause(
            request.filters, param_offset=1
        )
        vector_filter_clause, vector_filter_values = self._build_filter_clause(
            request.filters, table_alias="f", param_offset=1
        )

        # 3. Parallel vector + fulltext search
        vector_task = self._vector_search(
            vector_query, vector_filter_clause, vector_filter_values
        )
        fulltext_task = self._fulltext_search(fulltext_query, filter_clause, filter_values)

        vector_results, fulltext_results = await self._gather_with_timeout(
            vector_task, fulltext_task, timeout=30.0
        )

        # 4. RRF fusion
        k = self.config.search.rrf.k
        fused = self._rrf_fusion(vector_results, fulltext_results, k=k)

        total = len(fused)

        # 5. Pagination (after fusion)
        page = request.page
        page_size = min(request.page_size, self.config.behavior.max_page_size)
        offset = (page - 1) * page_size
        paged_ids = [pk for pk, _ in fused[offset : offset + page_size]]

        # 6. Fetch full rows
        rows = await self._fetch_rows_by_ids(paged_ids)
        row_map = {row[self.pk]: row for row in rows}

        # 7. Assemble results with highlights
        results: list[SearchResultItem] = []
        highlight_enabled = self.config.presentation.highlight.enabled
        prefix = self.config.presentation.highlight.prefix
        suffix = self.config.presentation.highlight.suffix

        for pk, score in fused[offset : offset + page_size]:
            row = row_map.get(pk)
            if row is None:
                continue

            highlights: Optional[dict[str, str]] = None
            if highlight_enabled and query:
                highlights = self._build_highlights(row, query, prefix, suffix)

            item = SearchResultItem(
                id=pk,
                score=round(score, 6),
                highlights=highlights,
                **{k: v for k, v in row.items() if k != self.pk},
            )
            results.append(item)

        # 8. Suggested filters (facets)
        suggested_filters: list[FilterOption] = []
        if self._has_facetable_fields():
            suggested_filters = await self._get_facet_options(applied=request.filters)

        took_ms = int((time.perf_counter() - start_time) * 1000)

        return SearchResponse(
            results=results,
            total=total,
            page=page,
            page_size=page_size,
            query=query,
            suggested_filters=suggested_filters,
            query_analysis={
                "vector_query": vector_query,
                "fulltext_query": fulltext_query,
                "vector_hits": len(vector_results),
                "fulltext_hits": len(fulltext_results),
            },
            took_ms=took_ms,
        )

    async def suggest(self, query: str, limit: int = 8) -> SuggestResponse:
        """Return autocomplete suggestions based on a prefix match."""
        if not query or len(query.strip()) < self.config.behavior.min_query_length:
            return SuggestResponse(suggestions=[], query=query)

        prefix = query.strip().lower()
        suggestions: list[SuggestionItem] = []

        # Find the first searchable text-like field to use for suggestions
        title_field: Optional[str] = None
        for name, cfg in self.fields.items():
            if cfg.searchable and cfg.type in ("short_text", "long_text"):
                title_field = name
                break

        if title_field is None:
            return SuggestResponse(suggestions=[], query=query)

        async with get_connection() as conn:
            sql = f"""
                SELECT DISTINCT {title_field}
                FROM {self.table}
                WHERE LOWER({title_field}) LIKE $1
                LIMIT $2
            """
            rows = await conn.fetch(sql, f"{prefix}%", limit)

        for row in rows:
            text = row[title_field]
            highlighted = text.replace(prefix, f"<mark>{prefix}</mark>", 1)
            suggestions.append(
                SuggestionItem(
                    type="query",
                    text=text,
                    highlight=highlighted,
                )
            )

        return SuggestResponse(suggestions=suggestions, query=query)

    async def get_filters(
        self, applied: Optional[dict[str, Any]] = None
    ) -> FiltersResponse:
        """Return available filter options with counts."""
        filters = await self._get_facet_options(applied=applied)
        return FiltersResponse(filters=filters, applied=applied)

    # ------------------------------------------------------------------
    # Query preprocessing
    # ------------------------------------------------------------------

    def _preprocess_query(self, query: str) -> tuple[str, str]:
        """Split query, remove stopwords, return (vector_text, fulltext_text)."""
        tokens = query.split()
        stopwords = set(self.config.search.stopwords)
        cleaned = [t for t in tokens if t.lower() not in stopwords]

        if not cleaned:
            # If everything is a stopword, fall back to original query
            cleaned = tokens

        vector_text = " ".join(cleaned)
        fulltext_text = " ".join(cleaned)
        return vector_text, fulltext_text

    # ------------------------------------------------------------------
    # SQL filter builder
    # ------------------------------------------------------------------

    def _build_filter_clause(
        self,
        filters: Optional[dict[str, Any]],
        table_alias: Optional[str] = None,
        param_offset: int = 0,
    ) -> tuple[str, list[Any]]:
        """Build a WHERE clause fragment and parameter list from filters.

        Returns (clause_string, values).  The clause string is safe to
        interpolate directly because column names come from config and
        operators are whitelisted; *values* are passed as parameters.

        Args:
            param_offset: Number of parameters already consumed before this
                clause (so that placeholders start at $offset+1).
        """
        if not filters:
            return "", []

        clauses: list[str] = []
        values: list[Any] = []
        alias_prefix = f"{table_alias}." if table_alias else ""

        for field_name, condition in filters.items():
            # Validate field exists in config (defensive)
            if self.fields and field_name not in self.fields:
                continue

            col = f"{alias_prefix}{field_name}"

            if isinstance(condition, dict):
                for op, val in condition.items():
                    clause = self._operator_clause(col, op, val, values, param_offset)
                    if clause:
                        clauses.append(clause)
            elif isinstance(condition, list):
                # IN operator
                placeholders = ", ".join(
                    f"${param_offset + len(values) + i + 1}" for i in range(len(condition))
                )
                clauses.append(f"{col} IN ({placeholders})")
                values.extend(condition)
            else:
                # Equality
                clauses.append(f"{col} = ${param_offset + len(values) + 1}")
                values.append(condition)

        if not clauses:
            return "", []

        return " AND ".join(clauses), values

    def _operator_clause(
        self, field: str, op: str, value: Any, values: list[Any], param_offset: int = 0
    ) -> Optional[str]:
        """Return a single operator clause and append the value."""
        idx = param_offset + len(values) + 1
        op_map = {
            "eq": "=",
            "ne": "!=",
            "gt": ">",
            "gte": ">=",
            "lt": "<",
            "lte": "<=",
        }
        if op in op_map:
            values.append(value)
            return f"{field} {op_map[op]} ${idx}"
        if op == "in" and isinstance(value, list):
            placeholders = ", ".join(f"${idx + i}" for i in range(len(value)))
            values.extend(value)
            return f"{field} IN ({placeholders})"
        if op == "between" and isinstance(value, list) and len(value) == 2:
            values.extend(value)
            return f"{field} BETWEEN ${idx} AND ${idx + 1}"
        return None

    # ------------------------------------------------------------------
    # Vector search
    # ------------------------------------------------------------------

    async def _vector_search(
        self,
        query_text: str,
        filter_clause: str,
        filter_values: list[Any],
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        """Return vector search results as [{id, score}]."""
        if not self.config.search.strategies.get("vector", True):
            return []

        try:
            query_vector = await self.embedding_service.generate_query(query_text)
            query_vector_str = "[" + ",".join(str(x) for x in query_vector) + "]"
        except Exception:
            return []

        embeddings_table = f"{self.table}_embeddings"

        # When filters exist we need to join the main table
        pk_ref = f"{self.pk}_ref"
        if filter_clause:
            where_sql = f"e.embed_type = 'combined' AND {filter_clause}"
            sql = f"""
                SELECT e."{pk_ref}", e.embedding <=> $1::vector AS distance
                FROM {embeddings_table} e
                JOIN {self.table} f ON e."{pk_ref}" = f.{self.pk}
                WHERE {where_sql}
                ORDER BY e.embedding <=> $1::vector
                LIMIT ${len(filter_values) + 2}
            """
            args = [query_vector_str] + filter_values + [limit]
        else:
            where_sql = f"e.embed_type = 'combined'"
            sql = f"""
                SELECT e."{pk_ref}", e.embedding <=> $1::vector AS distance
                FROM {embeddings_table} e
                WHERE {where_sql}
                ORDER BY e.embedding <=> $1::vector
                LIMIT $2
            """
            args = [query_vector_str, limit]

        async with get_connection() as conn:
            rows = await conn.fetch(sql, *args)

        return [
            {"id": row[pk_ref], "score": 1.0 - float(row["distance"])}
            for row in rows
        ]

    # ------------------------------------------------------------------
    # Fulltext search
    # ------------------------------------------------------------------

    async def _fulltext_search(
        self,
        query_text: str,
        filter_clause: str,
        filter_values: list[Any],
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        """Return fulltext search results as [{id, score}]."""
        if not self.config.search.strategies.get("fulltext", True):
            return []

        vector_col = "pandasearch_fts_vector"
        lang = self.config.search.fulltext.language

        where_parts: list[str] = [
            f'"{vector_col}" @@ plainto_tsquery(\'{lang}\', $1)'
        ]
        if filter_clause:
            where_parts.append(filter_clause)

        where_sql = " AND ".join(where_parts)

        sql = f"""
            SELECT {self.pk},
                   ts_rank_cd("{vector_col}",
                              plainto_tsquery('{lang}', $1)) AS rank
            FROM {self.table}
            WHERE {where_sql}
            ORDER BY rank DESC
            LIMIT ${len(filter_values) + 2}
        """
        args = [query_text] + filter_values + [limit]

        async with get_connection() as conn:
            rows = await conn.fetch(sql, *args)

        return [
            {"id": row[self.pk], "score": float(row["rank"])}
            for row in rows
        ]

    def _combined_text_expr(self) -> str:
        """Build COALESCE concatenation of searchable text fields."""
        searchable_fields = [
            name
            for name, cfg in self.fields.items()
            if cfg.searchable and cfg.type in ("short_text", "long_text", "category")
        ]
        if not searchable_fields:
            # Fallback: use primary key (will produce empty tsvector, but safe)
            searchable_fields = [self.pk]

        parts = [f'COALESCE("{f}"::text, \'\')' for f in searchable_fields]
        return " || ' ' || ".join(parts)

    # ------------------------------------------------------------------
    # RRF fusion
    # ------------------------------------------------------------------

    @staticmethod
    def _rrf_fusion(
        vector_results: list[dict[str, Any]],
        fulltext_results: list[dict[str, Any]],
        k: int = 60,
    ) -> list[tuple[Any, float]]:
        """Reciprocal Rank Fusion. Returns [(id, score), ...] sorted desc."""
        scores: dict[Any, float] = {}

        for rank, item in enumerate(vector_results):
            pk = item["id"]
            scores[pk] = scores.get(pk, 0.0) + 1.0 / (k + rank + 1)

        for rank, item in enumerate(fulltext_results):
            pk = item["id"]
            scores[pk] = scores.get(pk, 0.0) + 1.0 / (k + rank + 1)

        return sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # ------------------------------------------------------------------
    # Row fetching & highlighting
    # ------------------------------------------------------------------

    async def _fetch_rows_by_ids(self, ids: list[Any]) -> list[dict[str, Any]]:
        """Fetch full rows for a list of primary keys, preserving input order
        is handled by the caller."""
        if not ids:
            return []

        # Build safe column list if we know the fields
        if self.fields:
            columns = ", ".join(
                [self.pk] + [name for name in self.fields if name != self.pk]
            )
        else:
            columns = "*"

        sql = f"""
            SELECT {columns} FROM {self.table}
            WHERE {self.pk} = ANY($1)
        """
        async with get_connection() as conn:
            rows = await conn.fetch(sql, ids)
        return [dict(row) for row in rows]

    def _build_highlights(
        self,
        row: dict[str, Any],
        query: str,
        prefix: str,
        suffix: str,
    ) -> dict[str, str]:
        """Wrap matching query tokens in highlight tags for searchable fields."""
        highlights: dict[str, str] = {}
        tokens = [t.lower() for t in query.split() if t]

        for field_name, cfg in self.fields.items():
            if not cfg.searchable or cfg.type not in ("short_text", "long_text", "category"):
                continue
            value = row.get(field_name)
            if not value:
                continue
            text = str(value)
            highlighted = self._highlight_text(text, tokens, prefix, suffix)
            if highlighted != text:
                highlights[field_name] = highlighted

        return highlights

    @staticmethod
    def _highlight_text(
        text: str, tokens: list[str], prefix: str, suffix: str
    ) -> str:
        """Case-insensitive highlight of any token occurrence."""
        if not tokens:
            return text
        result = text
        # Simple word-boundary-ish replacement: replace each token
        # independently.  To avoid double-wrapping we process longest first.
        for token in sorted(tokens, key=len, reverse=True):
            if not token:
                continue
            # Case-insensitive replace using a manual scan
            lower_result = result.lower()
            lower_token = token.lower()
            idx = lower_result.find(lower_token)
            while idx != -1:
                # Check if already wrapped
                before = result[:idx]
                after = result[idx + len(token) :]
                # Simple heuristic: if prefix already right before, skip
                if before.endswith(prefix):
                    idx = lower_result.find(lower_token, idx + 1)
                    continue
                original = result[idx : idx + len(token)]
                result = before + prefix + original + suffix + after
                lower_result = result.lower()
                idx = lower_result.find(lower_token, idx + len(prefix) + len(original) + len(suffix))
        return result

    # ------------------------------------------------------------------
    # Facet / filter options
    # ------------------------------------------------------------------

    def _has_facetable_fields(self) -> bool:
        return any(cfg.facetable for cfg in self.fields.values())

    async def _get_facet_options(
        self, applied: Optional[dict[str, Any]] = None
    ) -> list[FilterOption]:
        """Run GROUP BY counts for each facetable field."""
        options: list[FilterOption] = []

        for field_name, cfg in self.fields.items():
            if not cfg.facetable:
                continue

            label = cfg.display_name or field_name
            facet_type = self._facet_type_for_field(cfg)

            if facet_type == "multi_select":
                opts = await self._facet_multi_select(field_name, applied)
            elif facet_type == "range":
                opts = await self._facet_range(field_name, applied)
            elif facet_type == "boolean":
                opts = await self._facet_boolean(field_name, applied)
            else:
                opts = None

            if opts is not None:
                options.append(
                    FilterOption(
                        field=field_name,
                        type=facet_type,
                        label=label,
                        options=opts.get("options"),
                        min=opts.get("min"),
                        max=opts.get("max"),
                    )
                )

        return options

    def _facet_type_for_field(self, cfg: FieldConfig) -> str:
        if cfg.type == "boolean":
            return "boolean"
        if cfg.type == "number":
            return "range"
        return "multi_select"

    async def _facet_multi_select(
        self, field: str, applied: Optional[dict[str, Any]]
    ) -> Optional[dict[str, Any]]:
        filter_clause, filter_values = self._build_filter_clause(
            {k: v for k, v in (applied or {}).items() if k != field}
        )

        where_sql = f"WHERE {filter_clause}" if filter_clause else ""
        sql = f"""
            SELECT {field} AS value, COUNT(*) AS count
            FROM {self.table}
            {where_sql}
            GROUP BY {field}
            ORDER BY count DESC
            LIMIT 20
        """
        async with get_connection() as conn:
            rows = await conn.fetch(sql, *filter_values)

        options = [
            {"value": row["value"], "count": row["count"]}
            for row in rows
            if row["value"] is not None
        ]
        return {"options": options}

    async def _facet_range(
        self, field: str, applied: Optional[dict[str, Any]]
    ) -> Optional[dict[str, Any]]:
        filter_clause, filter_values = self._build_filter_clause(
            {k: v for k, v in (applied or {}).items() if k != field}
        )

        where_sql = f"WHERE {filter_clause}" if filter_clause else ""
        sql = f"""
            SELECT MIN({field}) AS min_val, MAX({field}) AS max_val
            FROM {self.table}
            {where_sql}
        """
        async with get_connection() as conn:
            row = await conn.fetchrow(sql, *filter_values)

        if row is None or row["min_val"] is None:
            return None
        return {
            "min": float(row["min_val"]),
            "max": float(row["max_val"]),
        }

    async def _facet_boolean(
        self, field: str, applied: Optional[dict[str, Any]]
    ) -> Optional[dict[str, Any]]:
        filter_clause, filter_values = self._build_filter_clause(
            {k: v for k, v in (applied or {}).items() if k != field}
        )

        where_sql = f"WHERE {filter_clause}" if filter_clause else ""
        sql = f"""
            SELECT {field} AS value, COUNT(*) AS count
            FROM {self.table}
            {where_sql}
            GROUP BY {field}
            ORDER BY count DESC
        """
        async with get_connection() as conn:
            rows = await conn.fetch(sql, *filter_values)

        options = [
            {"value": row["value"], "count": row["count"]}
            for row in rows
        ]
        return {"options": options}

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    async def _gather_with_timeout(self, *coros, timeout: float = 30.0):
        """Run coroutines concurrently and return results with a timeout."""
        import asyncio

        tasks = [asyncio.create_task(c) for c in coros]
        try:
            return await asyncio.wait_for(asyncio.gather(*tasks), timeout=timeout)
        except asyncio.TimeoutError:
            for t in tasks:
                t.cancel()
            raise
