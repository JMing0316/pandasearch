"""
🐼 PandaSearch — Universal AI-powered search plugin for PostgreSQL.

Configure any table with YAML, get intelligent search in 30 seconds.
"""

__version__ = "0.1.0"
__author__ = "PandaSearch Team"

__all__ = ["SearchEngine"]

# Lazy import to avoid heavy dependencies at package load time
def __getattr__(name: str):
    if name == "SearchEngine":
        from pandasearch.search_engine import SearchEngine as _SearchEngine
        return _SearchEngine
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
