"""Schema auto-discovery service for PandaSearch."""

import re
from dataclasses import dataclass, field
from typing import Optional

from pandasearch.config import FieldConfig


@dataclass
class DiscoveredSchema:
    """Result of schema discovery."""
    table: str
    primary_key: str = "id"
    fields: dict[str, FieldConfig] = field(default_factory=dict)


class SchemaDiscovery:
    """Automatically discovers and classifies table schema."""

    # Field name patterns for classification
    TITLE_PATTERNS = ["title", "name", "subject", "headline"]
    DESC_PATTERNS = ["description", "content", "body", "detail", "summary", "bio"]
    CATEGORY_PATTERNS = ["category", "tag", "label", "type", "genre"]
    BRAND_PATTERNS = ["brand", "manufacturer", "maker"]
    PRICE_PATTERNS = ["price", "cost", "amount", "fee"]
    RATING_PATTERNS = ["rating", "score", "rate", "star"]
    COUNT_PATTERNS = ["count", "quantity", "stock", "sales", "sold"]
    IMAGE_PATTERNS = ["image", "img", "photo", "picture", "cover", "thumbnail"]
    IGNORE_PATTERNS = ["url", "link", "href"]
    SYSTEM_FIELDS = ["id", "created_at", "updated_at", "deleted_at"]

    def __init__(self, db_url: Optional[str] = None):
        self.db_url = db_url

    async def discover(self, table_name: str) -> DiscoveredSchema:
        """Discover schema for a given table."""
        from pandasearch.database import get_connection

        result = DiscoveredSchema(table=table_name)

        async with get_connection(self.db_url) as conn:
            # 1. Get columns
            columns = await conn.fetch("""
                SELECT column_name, data_type, character_maximum_length,
                       is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = $1 AND table_schema = 'public'
                ORDER BY ordinal_position
            """, table_name)

            # 2. Find primary key
            pk_result = await conn.fetch("""
                SELECT kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                WHERE tc.table_name = $1
                    AND tc.constraint_type = 'PRIMARY KEY'
            """, table_name)
            if pk_result:
                result.primary_key = pk_result[0]["column_name"]

            # 3. Sample data for analysis
            sample = await conn.fetch(
                f'SELECT * FROM "{table_name}" LIMIT 100'
            )

            # 4. Classify each field
            for col in columns:
                col_name = col["column_name"]
                field_config = self._classify_field(col, sample)
                result.fields[col_name] = field_config

        return result

    def _classify_field(self, col, sample) -> FieldConfig:
        """Classify a single field based on name, type, and sample data."""
        name = col["column_name"].lower()
        dtype = col["data_type"].lower()
        max_length = col.get("character_maximum_length") or 0

        # Rule 1: System fields → ignore
        if name in self.SYSTEM_FIELDS:
            return FieldConfig(type="ignore", weight=0)

        # Rule 2: Image URL fields
        if any(kw in name for kw in self.IMAGE_PATTERNS):
            return FieldConfig(type="image_url", weight=0)

        # Rule 3: Title/Name fields → short_text, weight=1.0
        if any(kw in name for kw in self.TITLE_PATTERNS):
            return FieldConfig(
                type="short_text", weight=1.0,
                searchable=True, display_name=self._to_display_name(name)
            )

        # Rule 4: Brand fields → category, weight=0.8
        if any(kw in name for kw in self.BRAND_PATTERNS):
            return FieldConfig(
                type="category", weight=0.8,
                searchable=True, filterable=True, facetable=True,
                display_name=self._to_display_name(name)
            )

        # Rule 5: Description/Content → long_text, weight=0.6
        if any(kw in name for kw in self.DESC_PATTERNS):
            return FieldConfig(
                type="long_text", weight=0.6,
                searchable=True, embedding_strategy="separate",
                display_name=self._to_display_name(name)
            )

        # Rule 6: Category/Tag fields → category, weight=0.5
        if any(kw in name for kw in self.CATEGORY_PATTERNS):
            return FieldConfig(
                type="category", weight=0.5,
                searchable=True, filterable=True, facetable=True,
                display_name=self._to_display_name(name)
            )

        # Rule 7: Price fields → number, formatter=currency
        if any(kw in name for kw in self.PRICE_PATTERNS):
            return FieldConfig(
                type="number", weight=0,
                filterable=True, sortable=True,
                formatter="currency",
                display_name=self._to_display_name(name)
            )

        # Rule 8: Rating fields → number
        if any(kw in name for kw in self.RATING_PATTERNS):
            return FieldConfig(
                type="number", weight=0,
                filterable=True, sortable=True,
                display_name=self._to_display_name(name)
            )

        # Rule 9: Count/Quantity fields → number
        if any(kw in name for kw in self.COUNT_PATTERNS):
            return FieldConfig(
                type="number", weight=0,
                filterable=True, sortable=True,
                formatter="compact_number",
                display_name=self._to_display_name(name)
            )

        # Rule 10: URL fields → ignore
        if any(kw in name for kw in self.IGNORE_PATTERNS):
            return FieldConfig(type="ignore", weight=0)

        # Rule 11: Boolean → category
        if dtype == "boolean":
            return FieldConfig(
                type="category", weight=0,
                filterable=True, facetable=True,
                display_name=self._to_display_name(name)
            )

        # Rule 12: JSON → json
        if dtype in ["json", "jsonb"]:
            return FieldConfig(
                type="json", weight=0.3, searchable=True,
                display_name=self._to_display_name(name)
            )

        # Rule 13: Timestamp/Date → date
        if dtype in ["timestamp", "timestamptz", "date"]:
            return FieldConfig(
                type="date", weight=0,
                filterable=True, sortable=True,
                display_name=self._to_display_name(name)
            )

        # Rule 14: Numeric → number
        if dtype in ["integer", "bigint", "numeric", "decimal", "real", "double precision"]:
            return FieldConfig(
                type="number", weight=0,
                filterable=True, sortable=True,
                display_name=self._to_display_name(name)
            )

        # Rule 15: Long text → long_text
        if dtype == "text" or (max_length and max_length > 500):
            return FieldConfig(
                type="long_text", weight=0.5, searchable=True,
                display_name=self._to_display_name(name)
            )

        # Default: short_text
        return FieldConfig(
            type="short_text", weight=0.7, searchable=True,
            display_name=self._to_display_name(name)
        )

    @staticmethod
    def _to_display_name(field_name: str) -> str:
        """Convert snake_case to readable name."""
        # Replace underscores with spaces and capitalize
        return field_name.replace("_", " ").title()
