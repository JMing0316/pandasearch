"""FastAPI application entry point for PandaSearch."""

from contextlib import asynccontextmanager
from typing import Any, Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from pandasearch.api_models import (
    FiltersResponse,
    HealthResponse,
    SearchRequest,
    SearchResponse,
    SuggestResponse,
    SyncRequest,
    SyncResponse,
)
from pandasearch.config import Settings
from pandasearch.database import init_db
from pandasearch.search_engine import SearchEngine

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    await init_db()

    # Try to load config from default path or create minimal engine
    engine = SearchEngine()
    default_config = "configs/minimal.yaml"
    try:
        engine = await SearchEngine.from_yaml(default_config)
        print(f"🐼 配置已加载: {default_config}")
    except Exception as e:
        print(f"🐼 配置加载失败: {type(e).__name__}: {e}")
        print("🐼 等待运行时初始化...")

    app.state.search_engine = engine
    print("🐼 胖达已就绪！")
    yield
    # Shutdown
    print("🐼 胖达休息中...")


app = FastAPI(
    title="PandaSearch",
    description="🐼 Universal AI-powered search plugin for PostgreSQL",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------
# Health
# ------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    engine: SearchEngine = app.state.search_engine
    config = engine.get_config()
    return HealthResponse(
        status="ok",
        version="0.1.0",
        database="connected",
        indexed_items=0,
        message="🐼 胖达很健康！",
    )


# ------------------------------------------------------------------
# Search
# ------------------------------------------------------------------

@app.post("/api/v1/search", response_model=SearchResponse)
async def search_endpoint(request: SearchRequest):
    """Main search endpoint (hybrid vector + fulltext + SQL filter)."""
    engine: SearchEngine = app.state.search_engine
    return await engine.search(request)


# ------------------------------------------------------------------
# Suggest
# ------------------------------------------------------------------

@app.get("/api/v1/suggest", response_model=SuggestResponse)
async def suggest_endpoint(
    q: str = Query(..., min_length=1, description="Query prefix"),
    limit: int = Query(8, ge=1, le=20, description="Max suggestions"),
):
    """Autocomplete suggestions based on prefix match."""
    engine: SearchEngine = app.state.search_engine
    return await engine.suggest(query=q, limit=limit)


# ------------------------------------------------------------------
# Filters
# ------------------------------------------------------------------

@app.get("/api/v1/filters", response_model=FiltersResponse)
async def filters_endpoint(
    applied: Optional[str] = Query(None, description="JSON-encoded applied filters"),
):
    """Get available filter options with counts."""
    engine: SearchEngine = app.state.search_engine
    import json
    parsed: Optional[dict[str, Any]] = None
    if applied:
        try:
            parsed = json.loads(applied)
        except json.JSONDecodeError:
            parsed = None
    return await engine.get_filters(applied=parsed)


# ------------------------------------------------------------------
# Config
# ------------------------------------------------------------------

@app.get("/api/v1/config")
async def config_endpoint():
    """Get current search configuration."""
    engine: SearchEngine = app.state.search_engine
    return engine.get_config()


# ------------------------------------------------------------------
# Sync
# ------------------------------------------------------------------

@app.post("/api/v1/sync")
async def sync_endpoint(request: SyncRequest):
    """Sync data to search indexes (incremental or full rebuild)."""
    engine: SearchEngine = app.state.search_engine
    result = await engine.sync(
        item_ids=request.item_ids, full_rebuild=request.full_rebuild
    )
    return SyncResponse(
        status="completed" if not result.get("errors") else "completed_with_errors",
        total_items=result.get("processed", 0),
        processed=result.get("processed", 0),
        batch_size=100,
        estimated_seconds=None,
    )


# ------------------------------------------------------------------
# Init
# ------------------------------------------------------------------

@app.post("/api/v1/init")
async def init_endpoint():
    """One-click initialise search indexes for the configured table."""
    engine: SearchEngine = app.state.search_engine
    result = await engine.init()
    return {
        "status": "ok",
        "embeddings_table": result.get("embeddings_table"),
        "hnsw_index": result.get("hnsw_index"),
        "fulltext_index": result.get("fulltext_index"),
        "sync": result.get("sync"),
    }


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------

def cli():
    """CLI entry point."""
    import uvicorn
    uvicorn.run(
        "pandasearch.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.APP_DEBUG,
    )


if __name__ == "__main__":
    cli()
