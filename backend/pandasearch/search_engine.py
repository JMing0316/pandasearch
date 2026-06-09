"""Universal search engine for PandaSearch."""

from typing import Any, Optional

from pandasearch.config import SearchPluginConfig


class SearchEngine:
    """Universal AI search engine for any PostgreSQL table."""

    def __init__(self, config: Optional[SearchPluginConfig] = None):
        self.config = config

    @classmethod
    def from_yaml(cls, path: str) -> "SearchEngine":
        """Create engine from YAML config file."""
        import yaml
        with open(path) as f:
            data = yaml.safe_load(f)
        config = SearchPluginConfig(**data)
        return cls(config)

    @classmethod
    def from_dict(cls, data: dict) -> "SearchEngine":
        """Create engine from dict config."""
        config = SearchPluginConfig(**data)
        return cls(config)

    @classmethod
    async def create(
        cls,
        db_url: Optional[str] = None,
        table: Optional[str] = None,
    ) -> "SearchEngine":
        """Auto-discover and create engine (minimal mode)."""
        from pandasearch.config import DataSourceConfig, SearchPluginConfig
        from pandasearch.schema_discovery import SchemaDiscovery

        # Create minimal config with just table name
        ds_config = DataSourceConfig(table=table or "")
        config = SearchPluginConfig(data_source=ds_config)

        # Auto-discover schema
        discovery = SchemaDiscovery(db_url)
        discovered = await discovery.discover(config.data_source.table)

        # Merge discovered fields into config
        config.fields = discovered.fields
        config.data_source.primary_key = discovered.primary_key

        return cls(config)

    async def search(
        self,
        query: str,
        user_id: Optional[int] = None,
        filters: Optional[dict] = None,
        sort_by: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """Execute search query."""
        # TODO: Implement full search pipeline
        return {
            "products": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
            "ai_summary": f"🐼 胖达正在为您搜索：{query}",
            "query_analysis": {"intent": "search", "entities": {}}
        }

    async def suggest(self, query: str, limit: int = 8) -> dict[str, Any]:
        """Get autocomplete suggestions."""
        # TODO: Implement suggestions
        return {"suggestions": []}

    def serve(self, port: int = 8000) -> None:
        """Start the API server."""
        import uvicorn
        uvicorn.run(
            "pandasearch.main:app",
            host="0.0.0.0",
            port=port,
            reload=True,
        )
