"""Index management module for PandaSearch."""

import logging
from typing import Optional

from pandasearch.config import SearchPluginConfig
from pandasearch.database import get_connection
from pandasearch.embedding import EmbeddingService

logger = logging.getLogger(__name__)


class IndexManager:
    """Manage search indexes (vector + fulltext) for a configured table."""

    def __init__(
        self,
        config: SearchPluginConfig,
        embedding_service: EmbeddingService,
    ):
        self.config = config
        self.embedding_service = embedding_service

        self.table = config.data_source.table
        self.primary_key = config.data_source.primary_key
        if not self.primary_key:
            raise ValueError("data_source.primary_key must be set in config.")

        self.fields = config.fields or {}
        self.dimensions = config.search.embedding.dimensions
        self.batch_size = config.search.embedding.batch_size
        self.embeddings_table = f"{self.table}_embeddings"

    def _validate_fields(self) -> None:
        """Ensure fields configuration is available."""
        if not self.fields:
            raise ValueError(
                "Field configuration is required. "
                "Please run schema discovery or provide fields in config."
            )

    async def init_table(self) -> dict:
        """One-click initialization.

        Creates embeddings table, HNSW index, GIN fulltext index,
        and performs a full data sync.
        """
        self._validate_fields()

        results = {
            "embeddings_table": False,
            "hnsw_index": False,
            "fulltext_index": False,
            "sync": None,
        }

        await self.create_embeddings_table()
        results["embeddings_table"] = True

        await self.create_hnsw_index()
        results["hnsw_index"] = True

        await self.create_fulltext_index()
        results["fulltext_index"] = True

        results["sync"] = await self.sync_data(full_rebuild=True)
        return results

    async def create_embeddings_table(self) -> None:
        """Create the vector embeddings table for the target table.

        If the table already exists but with a different VECTOR dimension,
        it is dropped and recreated to match the current config.
        """
        pk = self.primary_key
        table = self.table
        embeddings_table = self.embeddings_table
        dimensions = self.dimensions
        pk_ref = f"{pk}_ref"

        async with get_connection() as conn:
            # Check if table exists and what dimension it was created with
            # Use to_regclass() to safely handle missing tables (returns NULL instead of error)
            row = await conn.fetchrow(
                """
                SELECT atttypmod
                FROM pg_attribute
                WHERE attrelid = to_regclass($1)
                  AND attname = 'embedding'
                  AND NOT attisdropped
                """,
                embeddings_table,
            )
            if row is not None:
                existing_dim = row["atttypmod"]
                if existing_dim != dimensions:
                    logger.warning(
                        "Embeddings table '%s' exists with dimension %s, "
                        "but config requires %s. Dropping and recreating.",
                        embeddings_table,
                        existing_dim,
                        dimensions,
                    )
                    await conn.execute(
                        f'DROP TABLE IF EXISTS "{embeddings_table}" CASCADE;'
                    )
                else:
                    logger.info(
                        "Embeddings table '%s' already exists with correct dimension %s.",
                        embeddings_table,
                        dimensions,
                    )
                    return

            sql = f"""
            CREATE TABLE IF NOT EXISTS "{embeddings_table}" (
                id BIGSERIAL PRIMARY KEY,
                "{pk_ref}" BIGINT NOT NULL REFERENCES "{table}"("{pk}") ON DELETE CASCADE,
                embed_type VARCHAR(20) NOT NULL DEFAULT 'combined',
                embedding VECTOR({dimensions}),
                model_version VARCHAR(50),
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE("{pk_ref}", embed_type)
            );
            """
            await conn.execute(sql)
            logger.info("Embeddings table '%s' created with dimension %s.", embeddings_table, dimensions)

    async def create_hnsw_index(self) -> None:
        """Create HNSW index on the embedding column."""
        embeddings_table = self.embeddings_table
        index_name = f"idx_{embeddings_table}_hnsw"

        sql = f"""
        CREATE INDEX IF NOT EXISTS "{index_name}"
        ON "{embeddings_table}"
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64);
        """

        async with get_connection() as conn:
            await conn.execute(sql)
            logger.info("HNSW index '%s' ensured.", index_name)

    async def create_fulltext_index(self) -> None:
        """Create GIN fulltext index on the target table via trigger-maintained column.

        Uses a regular column + trigger instead of a generated column,
        because PostgreSQL's to_tsvector() is STABLE and cannot be used
        in a generated-column expression regardless of plpgsql wrapping.
        """
        self._validate_fields()

        table = self.table
        index_name = f"idx_{table}_fts"
        vector_col = "pandasearch_fts_vector"
        trigger_name = "_pandasearch_fts_trigger"
        trigger_func = "_pandasearch_fts_update"

        searchable_fields = [
            name
            for name, cfg in self.fields.items()
            if cfg.searchable and cfg.type in ("short_text", "long_text", "category")
            and name != vector_col  # exclude PandaSearch's own column
        ]

        if not searchable_fields:
            logger.warning(
                "No searchable fields found for table '%s', skipping fulltext index.",
                table,
            )
            return

        # Build expressions for trigger function (needs NEW. prefix)
        # and for back-fill UPDATE (uses bare column names in table context)
        coalesce_parts_trigger = " || ' ' || ".join(
            f'COALESCE(NEW."{field}"::TEXT, \'\')' for field in searchable_fields
        )
        coalesce_parts_update = " || ' ' || ".join(
            f'COALESCE("{field}"::TEXT, \'\')' for field in searchable_fields
        )

        async with get_connection() as conn:
            # 1. Ensure the target column exists (regular, not generated)
            await conn.execute(f"""
                ALTER TABLE "{table}"
                ADD COLUMN IF NOT EXISTS "{vector_col}" tsvector;
            """)

            # 2. Create / replace the trigger function
            await conn.execute(f"""
                CREATE OR REPLACE FUNCTION {trigger_func}()
                RETURNS trigger AS $$
                BEGIN
                    NEW."{vector_col}" := to_tsvector('simple', {coalesce_parts_trigger});
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
            """)

            # 3. Attach trigger (idempotent: drop first, then create)
            await conn.execute(f"""
                DROP TRIGGER IF EXISTS {trigger_name} ON "{table}";
                CREATE TRIGGER {trigger_name}
                BEFORE INSERT OR UPDATE ON "{table}"
                FOR EACH ROW
                EXECUTE FUNCTION {trigger_func}();
            """)

            # 4. Back-fill existing rows where the column is NULL
            await conn.execute(f"""
                UPDATE "{table}"
                SET "{vector_col}" = to_tsvector('simple', {coalesce_parts_update})
                WHERE "{vector_col}" IS NULL;
            """)

            # 5. Create GIN index
            await conn.execute(f"""
                CREATE INDEX IF NOT EXISTS "{index_name}"
                ON "{table}" USING GIN ("{vector_col}");
            """)

            logger.info("Fulltext index '%s' ensured (trigger-based).", index_name)

    async def sync_data(
        self,
        item_ids: Optional[list] = None,
        full_rebuild: bool = False,
    ) -> dict:
        """Sync data from source table to embeddings table.

        Args:
            item_ids: Optional list of primary keys to sync incrementally.
            full_rebuild: If True, truncate embeddings table before syncing.

        Returns:
            Dict with processed count, batch count, and any errors.
        """
        self._validate_fields()

        table = self.table
        pk = self.primary_key
        embeddings_table = self.embeddings_table
        fields = self.fields
        batch_size = self.batch_size

        result = {
            "processed": 0,
            "batches": 0,
            "errors": [],
        }

        async with get_connection() as conn:
            if full_rebuild:
                await conn.execute(
                    f'TRUNCATE TABLE "{embeddings_table}" RESTART IDENTITY;'
                )
                logger.info(
                    "Truncated embeddings table '%s' for full rebuild.",
                    embeddings_table,
                )

            if item_ids == []:
                logger.info("Empty item_ids list provided; nothing to sync.")
                return result

            if item_ids:
                placeholders = ", ".join(f"${i + 1}" for i in range(len(item_ids)))
                query = f'SELECT * FROM "{table}" WHERE "{pk}" IN ({placeholders})'
                rows = await conn.fetch(query, *item_ids)
            else:
                query = f'SELECT * FROM "{table}"'
                rows = await conn.fetch(query)

            if not rows:
                logger.info("No rows to sync.")
                return result

            for i in range(0, len(rows), batch_size):
                batch = rows[i : i + batch_size]
                result["batches"] += 1

                texts = []
                pk_values = []
                for row in batch:
                    item = dict(row)
                    pk_value = item.get(pk)
                    if pk_value is None:
                        msg = f"Missing primary key '{pk}' in row from table '{table}'"
                        logger.warning(msg)
                        result["errors"].append(msg)
                        continue

                    text = self.embedding_service.format_text_for_embedding(
                        item=item,
                        fields=fields,
                    )
                    texts.append(text)
                    pk_values.append(pk_value)

                if not texts:
                    continue

                try:
                    embeddings = await self.embedding_service.generate(texts)
                except Exception as e:
                    msg = f"Failed to generate embeddings for batch {result['batches']}: {e}"
                    logger.error(msg)
                    result["errors"].append(msg)
                    continue

                values = []
                for pk_val, emb in zip(pk_values, embeddings):
                    emb_str = "[" + ",".join(str(x) for x in emb) + "]"
                    values.append(
                        (pk_val, "combined", emb_str, self.embedding_service.model)
                    )

                try:
                    await conn.executemany(
                        f"""
                        INSERT INTO "{embeddings_table}" ("{pk}_ref", embed_type, embedding, model_version)
                        VALUES ($1, $2, $3::vector, $4)
                        ON CONFLICT ("{pk}_ref", embed_type) DO UPDATE SET
                            embedding = EXCLUDED.embedding,
                            model_version = EXCLUDED.model_version,
                            updated_at = NOW()
                        """,
                        values,
                    )
                    result["processed"] += len(values)
                except Exception as e:
                    msg = f"Failed to insert batch {result['batches']}: {e}"
                    logger.error(msg)
                    result["errors"].append(msg)

        logger.info(
            "Sync completed: %s rows processed in %s batches.",
            result["processed"],
            result["batches"],
        )
        return result

    async def drop_indexes(self) -> None:
        """Drop all search-related indexes, the embeddings table,
        and the fulltext trigger / column."""
        table = self.table
        embeddings_table = self.embeddings_table
        vector_col = "pandasearch_fts_vector"
        trigger_name = "_pandasearch_fts_trigger"
        trigger_func = "_pandasearch_fts_update"

        async with get_connection() as conn:
            # Drop HNSW index
            await conn.execute(
                f'DROP INDEX IF EXISTS "idx_{embeddings_table}_hnsw";'
            )
            # Drop GIN index
            await conn.execute(
                f'DROP INDEX IF EXISTS "idx_{table}_fts";'
            )
            # Drop trigger (must happen before dropping the function)
            await conn.execute(
                f'DROP TRIGGER IF EXISTS {trigger_name} ON "{table}";'
            )
            # Drop trigger function
            await conn.execute(
                f'DROP FUNCTION IF EXISTS {trigger_func}() CASCADE;'
            )
            # Drop the fts column
            await conn.execute(
                f'ALTER TABLE "{table}" DROP COLUMN IF EXISTS "{vector_col}" CASCADE;'
            )
            # Drop embeddings table
            await conn.execute(
                f'DROP TABLE IF EXISTS "{embeddings_table}" CASCADE;'
            )
            logger.info(
                "Dropped indexes, embeddings table and fts trigger for '%s'.",
                table,
            )
