"""Embedding generation service for PandaSearch.

Supports both OpenAI API and local sentence-transformers models.
"""

import asyncio
import os
from typing import Optional

from pandasearch.config import Settings

settings = Settings()


class EmbeddingService:
    """Generate embeddings using OpenAI API or local sentence-transformers."""

    @staticmethod
    def _resolve_bge_m3_path() -> str:
        """Resolve BGE-M3 model path, checking multiple candidate locations."""
        snapshot = "5617a9f61b028005a4858fdac845db406aefb181"
        candidates = [
            # Docker: mounted at /models
            f"/models/bge-m3/models--BAAI--bge-m3/snapshots/{snapshot}",
            # Docker: mounted at /app/models
            f"/app/models/bge-m3/models--BAAI--bge-m3/snapshots/{snapshot}",
            # Local dev: two levels up from backend/pandasearch/embedding.py
            os.path.join(
                os.path.dirname(__file__), "..", "..", "models", "bge-m3",
                "models--BAAI--bge-m3", "snapshots", snapshot
            ),
        ]
        for path in candidates:
            if os.path.isdir(path):
                return path
        # Fallback to first candidate; SentenceTransformer will raise a clear error
        return candidates[0]

    def __init__(
        self,
        model: str = "text-embedding-3-small",
        dimensions: int = 1536,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.model = model
        self.dimensions = dimensions
        self._embeddings = None
        self._local_model = None

        # Determine backend: OpenAI or local
        is_openai_model = (
            model.startswith("openai:")
            or model in ("text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002")
        )
        has_api_key = bool(api_key or settings.OPENAI_API_KEY)

        if is_openai_model and has_api_key:
            from langchain_openai import OpenAIEmbeddings
            self._embeddings = OpenAIEmbeddings(
                model=model.replace("openai:", "") if model.startswith("openai:") else model,
                dimensions=dimensions,
                api_key=api_key or settings.OPENAI_API_KEY,
                base_url=base_url or settings.OPENAI_BASE_URL,
            )
        elif is_openai_model and not has_api_key:
            raise ValueError(
                "OPENAI_API_KEY is required for OpenAI embedding models. "
                "Please set it in your .env file or pass it as api_key parameter."
            )
        else:
            # Use local sentence-transformers
            self._init_local_model(model)

    def _init_local_model(self, model_name: str) -> None:
        """Initialize sentence-transformers model."""
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "sentence-transformers is required for local embedding models. "
                "Install with: pip install sentence-transformers"
            )

        # Map common aliases to HuggingFace model names or local paths
        model_map = {
            "moonshot-v1-embedding": "BAAI/bge-small-zh-v1.5",
            "bge-small-zh": "BAAI/bge-small-zh-v1.5",
            "bge-base-zh": "BAAI/bge-base-zh-v1.5",
            "bge-large-zh": "BAAI/bge-large-zh-v1.5",
            "bge-m3": self._resolve_bge_m3_path(),
        }
        hf_name = model_map.get(model_name, model_name)

        self._local_model = SentenceTransformer(hf_name)
        # Override dimensions with actual model output size
        self.dimensions = self._local_model.get_embedding_dimension()

    async def generate(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        if not texts:
            return []

        loop = asyncio.get_event_loop()

        if self._embeddings is not None:
            # OpenAI via LangChain
            result = await loop.run_in_executor(
                None, self._embeddings.embed_documents, texts
            )
            return result

        # Local sentence-transformers
        def _encode():
            return self._local_model.encode(texts, convert_to_numpy=True).tolist()

        return await loop.run_in_executor(None, _encode)

    async def generate_query(self, text: str) -> list[float]:
        """Generate embedding for a single query text."""
        loop = asyncio.get_event_loop()

        if self._embeddings is not None:
            result = await loop.run_in_executor(
                None, self._embeddings.embed_query, text
            )
            return result

        def _encode():
            return self._local_model.encode(text, convert_to_numpy=True).tolist()

        return await loop.run_in_executor(None, _encode)

    def format_text_for_embedding(
        self,
        item: dict,
        fields: dict,
        template: Optional[str] = None,
    ) -> str:
        """Format a data item into text for embedding.

        Combines searchable fields according to their weights and strategies.
        """
        parts = []

        # Sort fields by weight descending
        sorted_fields = sorted(
            fields.items(),
            key=lambda x: x[1].weight,
            reverse=True,
        )

        for field_name, field_config in sorted_fields:
            if field_config.type == "ignore":
                continue
            if not field_config.searchable and field_config.weight <= 0:
                continue

            value = item.get(field_name)
            if value is None:
                continue

            # Convert to string
            text_value = str(value).strip()
            if not text_value:
                continue

            # Repeat field text according to weight (simple weighting)
            repeat_count = max(1, int(field_config.weight * 2))
            for _ in range(repeat_count):
                parts.append(text_value)

        if template:
            try:
                return template.format(**item)
            except (KeyError, ValueError):
                pass

        return " ".join(parts)
