"""FastAPI application entry point for PandaSearch."""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pandasearch.config import Settings
from pandasearch.database import init_db
from pandasearch.search_engine import SearchEngine

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    await init_db()
    app.state.search_engine = SearchEngine()
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


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": "0.1.0",
        "message": "🐼 胖达很健康！",
    }


@app.post("/api/v1/search")
async def search(query: str, user_id: int | None = None):
    """Main search endpoint."""
    engine: SearchEngine = app.state.search_engine
    return await engine.search(query=query, user_id=user_id)


@app.get("/api/v1/suggest")
async def suggest(q: str, limit: int = 8):
    """Autocomplete suggestions."""
    engine: SearchEngine = app.state.search_engine
    return await engine.suggest(query=q, limit=limit)


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
