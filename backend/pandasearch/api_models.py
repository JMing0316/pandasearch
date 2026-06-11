"""API request/response Pydantic models for PandaSearch."""

from typing import Any, Optional

from pydantic import BaseModel, Field


# ============================================================
# Search API
# ============================================================

class SearchRequest(BaseModel):
    """Request body for /search endpoint."""

    query: str = Field(..., min_length=1, description="Search query string")
    user_id: Optional[int] = Field(None, description="User ID for personalization")
    filters: Optional[dict[str, Any]] = Field(None, description="Structured filters")
    sort_by: str = Field("relevance", description="Sort field")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Results per page")


class SearchResultItem(BaseModel):
    """Single search result item."""

    id: Any = Field(..., description="Primary key value")
    score: float = Field(..., description="Relevance score (0-1)")
    highlights: Optional[dict[str, str]] = Field(None, description="Highlighted fields")
    # All other fields are dynamic based on the table schema
    model_config = {"extra": "allow"}


class FilterOption(BaseModel):
    """Filter option for a single field."""

    field: str = Field(..., description="Field name")
    type: str = Field(..., description="Filter type: multi_select | range | rating | boolean")
    label: str = Field(..., description="Display label")
    options: Optional[list[dict[str, Any]]] = Field(None, description="Available options")
    min: Optional[float] = Field(None, description="Min value for range")
    max: Optional[float] = Field(None, description="Max value for range")


class SearchResponse(BaseModel):
    """Response for /search endpoint."""

    results: list[SearchResultItem] = Field(default_factory=list)
    total: int = Field(0, description="Total matching results")
    page: int = Field(1, description="Current page")
    page_size: int = Field(20, description="Page size")
    query: str = Field("", description="Original query")
    ai_summary: Optional[str] = Field(None, description="AI-generated summary")
    suggested_filters: list[FilterOption] = Field(default_factory=list)
    query_analysis: dict[str, Any] = Field(default_factory=dict)
    took_ms: int = Field(0, description="Search latency in milliseconds")


# ============================================================
# Suggest API
# ============================================================

class SuggestionItem(BaseModel):
    """Single autocomplete suggestion."""

    type: str = Field(..., description="suggestion type: query | category | brand | product")
    text: str = Field(..., description="Suggestion text")
    highlight: Optional[str] = Field(None, description="Highlighted text")
    extra: Optional[dict[str, Any]] = Field(None, description="Additional metadata")


class SuggestResponse(BaseModel):
    """Response for /suggest endpoint."""

    suggestions: list[SuggestionItem] = Field(default_factory=list)
    query: str = Field("", description="Original query")


# ============================================================
# Filters API
# ============================================================

class FiltersResponse(BaseModel):
    """Response for /filters endpoint."""

    filters: list[FilterOption] = Field(default_factory=list)
    applied: Optional[dict[str, Any]] = Field(None, description="Currently applied filters")


# ============================================================
# Config API
# ============================================================

class ConfigResponse(BaseModel):
    """Response for /config endpoint."""

    table: str = Field(..., description="Data source table name")
    fields: dict[str, Any] = Field(default_factory=dict, description="Field configurations")
    search: dict[str, Any] = Field(default_factory=dict, description="Search configuration")
    presentation: dict[str, Any] = Field(
        default_factory=dict, description="Presentation configuration"
    )
    behavior: dict[str, Any] = Field(default_factory=dict, description="Behavior configuration")


# ============================================================
# Sync API
# ============================================================

class SyncRequest(BaseModel):
    """Request body for /sync endpoint."""

    item_ids: Optional[list[int]] = Field(None, description="Specific item IDs to sync")
    full_rebuild: bool = Field(False, description="Whether to rebuild all indexes")


class SyncResponse(BaseModel):
    """Response for /sync endpoint."""

    status: str = Field(..., description="sync status: started | completed | failed")
    total_items: int = Field(0, description="Total items to sync")
    processed: int = Field(0, description="Items processed so far")
    batch_size: int = Field(100, description="Batch size")
    estimated_seconds: Optional[int] = Field(None, description="Estimated completion time")


# ============================================================
# Health API
# ============================================================

class HealthResponse(BaseModel):
    """Response for /health endpoint."""

    status: str = Field("ok", description="Service status")
    version: str = Field("0.1.0", description="API version")
    database: str = Field("unknown", description="Database connection status")
    indexed_items: int = Field(0, description="Number of indexed items")
    message: str = Field("🐼 胖达很健康！", description="Status message")
