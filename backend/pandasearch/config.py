"""Five-layer configuration model for PandaSearch."""

from typing import Literal, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# ============================================================
# Layer 1: Data Source Configuration
# ============================================================

class ConnectionPoolConfig(BaseModel):
    min_size: int = 5
    max_size: int = 20
    timeout: int = 30


class SchemaDiscoveryConfig(BaseModel):
    sample_size: int = 100
    ignore_patterns: list[str] = Field(default_factory=lambda: [
        "id", "created_at", "updated_at", "deleted_at"
    ])
    custom_type_rules: dict = Field(default_factory=dict)


class DataSourceConfig(BaseModel):
    table: str
    primary_key: Optional[str] = None  # Auto-discovered
    connection_pool: ConnectionPoolConfig = Field(default_factory=ConnectionPoolConfig)
    schema_discovery: SchemaDiscoveryConfig = Field(default_factory=SchemaDiscoveryConfig)


# ============================================================
# Layer 2: Field Mapping Configuration
# ============================================================

class FieldConfig(BaseModel):
    type: Literal[
        "short_text", "long_text", "category", "number",
        "boolean", "json", "date", "image_url", "ignore"
    ] = "short_text"
    display_name: Optional[str] = None
    searchable: bool = True
    filterable: bool = False
    sortable: bool = False
    facetable: bool = False
    weight: float = 0.7
    embedding_strategy: Literal["combined", "separate", "ignore"] = "combined"
    formatter: Optional[Literal["currency", "percentage", "date", "compact_number"]] = None
    max_length: Optional[int] = None


# ============================================================
# Layer 3: Search Strategy Configuration
# ============================================================

class StrategyWeightsConfig(BaseModel):
    vector: float = 0.5
    fulltext: float = 0.3
    sql_filter: float = 0.2


class RRFConfig(BaseModel):
    k: int = 60


class EmbeddingConfig(BaseModel):
    model: str = "openai:text-embedding-3-small"
    dimensions: int = 1536
    batch_size: int = 100
    template: str = "default"


class FullTextConfig(BaseModel):
    language: str = "simple"
    highlight: bool = True


class SearchConfig(BaseModel):
    strategies: dict[str, bool] = Field(default_factory=lambda: {
        "vector": True, "fulltext": True, "sql_filter": True
    })
    weights: StrategyWeightsConfig = Field(default_factory=StrategyWeightsConfig)
    rrf: RRFConfig = Field(default_factory=RRFConfig)
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    fulltext: FullTextConfig = Field(default_factory=FullTextConfig)
    synonyms: list[list[str]] = Field(default_factory=list)
    stopwords: list[str] = Field(default_factory=list)


# ============================================================
# Layer 4: Presentation Configuration
# ============================================================

class CardLayoutConfig(BaseModel):
    image_position: Literal["top", "left"] = "top"
    show_labels: bool = False
    max_title_length: int = 50
    badges: list[str] = Field(default_factory=list)


class HighlightConfig(BaseModel):
    enabled: bool = True
    prefix: str = "<mark>"
    suffix: str = "</mark>"


class EmptyStateConfig(BaseModel):
    title: str = "未找到相关结果"
    subtitle: str = "试试其他关键词，或调整筛选条件"
    suggestions: bool = True


class PresentationConfig(BaseModel):
    result_template: Literal["card", "list", "compact"] = "card"
    fields_order: list[str] = Field(default_factory=list)
    card_layout: CardLayoutConfig = Field(default_factory=CardLayoutConfig)
    highlight: HighlightConfig = Field(default_factory=HighlightConfig)
    empty_state: EmptyStateConfig = Field(default_factory=EmptyStateConfig)


# ============================================================
# Layer 5: Behavior Configuration
# ============================================================

class SortOption(BaseModel):
    value: str
    label: str


class CacheConfig(BaseModel):
    query_ttl_seconds: int = 300
    suggest_ttl_seconds: int = 60


class PersonalizationConfig(BaseModel):
    enabled: bool = True
    cold_start_strategy: Literal["popular", "newest", "random"] = "popular"
    behavior_weights: dict[str, int] = Field(default_factory=lambda: {
        "view": 1, "click": 3, "cart": 6, "favorite": 8, "purchase": 15
    })


class BehaviorConfig(BaseModel):
    debounce_ms: int = 300
    suggest_delay_ms: int = 100
    page_size: int = 20
    max_page_size: int = 100
    min_query_length: int = 1
    default_sort: str = "relevance"
    sort_options: list[SortOption] = Field(default_factory=lambda: [
        SortOption(value="relevance", label="相关性"),
        SortOption(value="price_asc", label="价格从低到高"),
        SortOption(value="price_desc", label="价格从高到低"),
        SortOption(value="rating", label="评分最高"),
        SortOption(value="sales", label="销量最高"),
        SortOption(value="newest", label="最新上架"),
    ])
    cache: CacheConfig = Field(default_factory=CacheConfig)
    personalization: PersonalizationConfig = Field(default_factory=PersonalizationConfig)


# ============================================================
# Root Configuration
# ============================================================

class SearchPluginConfig(BaseModel):
    data_source: DataSourceConfig
    fields: Optional[dict[str, FieldConfig]] = None  # Auto-discovered if None
    search: SearchConfig = Field(default_factory=SearchConfig)
    presentation: PresentationConfig = Field(default_factory=PresentationConfig)
    behavior: BehaviorConfig = Field(default_factory=BehaviorConfig)


# ============================================================
# Environment Settings
# ============================================================

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[".env", "../.env"],
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/pandasearch"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_POOL_SIZE: int = 50

    # App
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "change-me"

    # Search
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    CACHE_TTL_SECONDS: int = 300
