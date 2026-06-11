"""Universal search engine for PandaSearch.

Orchestrates IndexManager (index creation & data sync) and
SearchPipeline (hybrid search, suggestions, filters).
"""

from typing import Any, Optional

from pandasearch.api_models import (
    FiltersResponse,
    SearchRequest,
    SearchResponse,
    SuggestResponse,
    SyncRequest,
    SyncResponse,
)
from pandasearch.config import SearchPluginConfig
from pandasearch.embedding import EmbeddingService
from pandasearch.index_manager import IndexManager
from pandasearch.search_pipeline import SearchPipeline


class SearchEngine:
    """Universal AI search engine for any PostgreSQL table."""

    def __init__(self, config: Optional[SearchPluginConfig] = None):
        self.config = config
        self._embedding_service: Optional[EmbeddingService] = None
        self._index_manager: Optional[IndexManager] = None
        self._pipeline: Optional[SearchPipeline] = None

    # ------------------------------------------------------------------
    # Lazy initialisation of sub-services
    # ------------------------------------------------------------------

    def _ensure_services(self) -> None:
        """Create embedding service, index manager and search pipeline."""
        if self.config is None:
            raise RuntimeError("SearchEngine has no config. Call load_config() first.")

        if self._embedding_service is None:
            emb_cfg = self.config.search.embedding
            self._embedding_service = EmbeddingService(
                model=emb_cfg.model.replace("openai:", ""),
                dimensions=emb_cfg.dimensions,
            )

        if self._index_manager is None:
            self._index_manager = IndexManager(
                config=self.config,
                embedding_service=self._embedding_service,
            )

        if self._pipeline is None:
            self._pipeline = SearchPipeline(
                config=self.config,
                embedding_service=self._embedding_service,
            )

    # ------------------------------------------------------------------
    # Config loading
    # ------------------------------------------------------------------

    @classmethod
    async def from_yaml(cls, path: str) -> "SearchEngine":
        """Create engine from YAML config file with auto schema discovery."""
        import yaml
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        config = SearchPluginConfig(**data)

        # Auto-discover schema if primary_key or fields are missing
        if not config.data_source.primary_key or not config.fields:
            from pandasearch.schema_discovery import SchemaDiscovery
            discovery = SchemaDiscovery()
            discovered = await discovery.discover(config.data_source.table)
            if not config.data_source.primary_key:
                config.data_source.primary_key = discovered.primary_key
            if not config.fields:
                config.fields = discovered.fields

        return cls(config)

    @classmethod
    async def from_dict(cls, data: dict) -> "SearchEngine":
        """Create engine from dict config with auto schema discovery."""
        config = SearchPluginConfig(**data)

        # Auto-discover schema if primary_key or fields are missing
        if not config.data_source.primary_key or not config.fields:
            from pandasearch.schema_discovery import SchemaDiscovery
            discovery = SchemaDiscovery()
            discovered = await discovery.discover(config.data_source.table)
            if not config.data_source.primary_key:
                config.data_source.primary_key = discovered.primary_key
            if not config.fields:
                config.fields = discovered.fields

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

        ds_config = DataSourceConfig(table=table or "")
        config = SearchPluginConfig(data_source=ds_config)

        discovery = SchemaDiscovery(db_url)
        discovered = await discovery.discover(config.data_source.table)

        config.fields = discovered.fields
        config.data_source.primary_key = discovered.primary_key

        return cls(config)

    async def load_config(self, path: Optional[str] = None) -> None:
        """Load or reload configuration from a YAML file."""
        if path:
            self.config = self.from_yaml(path).config
        self._embedding_service = None
        self._index_manager = None
        self._pipeline = None

    # ------------------------------------------------------------------
    # Index management
    # ------------------------------------------------------------------

    async def init(self) -> dict[str, Any]:
        """One-click table initialisation.

        Creates embeddings table, HNSW index, GIN fulltext index,
        and performs a full data sync.
        """
        self._ensure_services()
        return await self._index_manager.init_table()  # type: ignore[union-attr]

    async def sync(self, item_ids: Optional[list[int]] = None, full_rebuild: bool = False) -> dict[str, Any]:
        """Sync data to the search indexes."""
        self._ensure_services()
        return await self._index_manager.sync_data(  # type: ignore[union-attr]
            item_ids=item_ids, full_rebuild=full_rebuild
        )

    # ------------------------------------------------------------------
    # Search API
    # ------------------------------------------------------------------

    async def search(self, request: SearchRequest) -> SearchResponse:
        """Execute a hybrid search query."""
        self._ensure_services()
        return await self._pipeline.search(request)  # type: ignore[union-attr]

    async def suggest(self, query: str, limit: int = 8) -> SuggestResponse:
        """Get autocomplete suggestions."""
        self._ensure_services()
        return await self._pipeline.suggest(query, limit)  # type: ignore[union-attr]

    async def get_filters(self, applied: Optional[dict[str, Any]] = None) -> FiltersResponse:
        """Get available filter options with counts."""
        self._ensure_services()
        return await self._pipeline.get_filters(applied)  # type: ignore[union-attr]

    def get_config(self) -> dict[str, Any]:
        """Return the current search configuration."""
        if self.config is None:
            return {}

        return {
            "table": self.config.data_source.table,
            "fields": {
                name: cfg.model_dump() for name, cfg in (self.config.fields or {}).items()
            },
            "search": self.config.search.model_dump(),
            "presentation": self.config.presentation.model_dump(),
            "behavior": self.config.behavior.model_dump(),
        }

    # ------------------------------------------------------------------
    # Server
    # ------------------------------------------------------------------

    def serve(self, port: int = 8000) -> None:
        """Start the API server."""
        import uvicorn
        uvicorn.run(
            "pandasearch.main:app",
            host="0.0.0.0",
            port=port,
            reload=True,
        )
