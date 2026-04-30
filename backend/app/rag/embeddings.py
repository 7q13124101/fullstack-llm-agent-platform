from abc import ABC, abstractmethod
from app.rag.config import RAGSettings
from app.rag.models import Document


class BaseEmbeddingProvider(ABC):
    """Abstract base class for embedding providers.

    Defines the interface that all embedding providers must implement.
    """
    @abstractmethod
    def embed_queries(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of query texts.

        Args:
            texts: List of text strings to embed.

        Returns:
            List of embedding vectors, one for each input text.
        """
        pass

    @abstractmethod
    def embed_document(self, document: Document) -> list[list[float]]:
        """Embed all chunks of a document.

        Args:
            document: Document object containing chunked pages to embed.

        Returns:
            List of embedding vectors, one for each chunk in the document.
        """
        pass

    @abstractmethod
    def warmup(self) -> None:
        """Ensures the model is loaded and ready for inference."""
        passfrom google import genai
from google.genai import types as genai_typesclass GeminiEmbeddingProvider(BaseEmbeddingProvider):
    """Google Gemini multimodal embedding provider.

    Supports text, images, and documents in a single embedding space.
    Uses the Gemini Embedding 2 model for natively multimodal embeddings.
    """

    def __init__(self, model: str, api_key: str = "") -> None:
        self.model = model
        self.client = genai.Client(api_key=api_key) if api_key else genai.Client()

    def embed_queries(self, texts: list[str]) -> list[list[float]]:
        result = self.client.models.embed_content(
            model=self.model,
            contents=texts,
        )
        return [e.values for e in result.embeddings]

    def embed_document(self, document: Document) -> list[list[float]]:
        contents = []
        for chunk in (document.chunked_pages or []):
            contents.append(chunk.chunk_content if chunk.chunk_content else "")
        result = self.client.models.embed_content(
            model=self.model,
            contents=contents,
        )
        return [e.values for e in result.embeddings]

    def embed_image(self, image_bytes: bytes, mime_type: str = "image/png") -> list[float]:
        """Embed an image directly (multimodal).

        Returns a vector in the same space as text embeddings.
        """
        result = self.client.models.embed_content(
            model=self.model,
            contents=[
                genai_types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            ],
        )
        return result.embeddings[0].values

    def warmup(self) -> None:
        pass
# Embedding orchestrator
class EmbeddingService:
    """Service for managing text embeddings.

    Orchestrates embedding operations using a configured embedding provider.
    Supports multiple backends: OpenAI, Voyage AI, and Sentence Transformers.
    """

    def __init__(self, settings: RAGSettings):
        """Initialize the embedding service.

        Args:
            settings: RAG configuration settings.
        """
        config = settings.embeddings_config
        self.expected_dim = config.dim        from app.core.config import settings as app_settings
        self.provider = GeminiEmbeddingProvider(model=config.model, api_key=app_settings.GOOGLE_API_KEY)
    def embed_query(self, query: str) -> list[float]:
        """Embed a single query text.

        Args:
            query: The text query to embed.

        Returns:
            Embedding vector for the query.
        """
        result = self.provider.embed_queries([query])[0]
        if len(result) != self.expected_dim:
            raise ValueError(
                f"Embedding dimension mismatch: expected {self.expected_dim}, "
                f"got {len(result)}. Check your embedding model configuration."
            )
        return result

    def embed_document(self, document: Document) -> list[list[float]]:
        """Embed all chunks of a document.

        Args:
            document: Document object containing chunked pages.

        Returns:
            List of embedding vectors for each chunk.
        """
        results = self.provider.embed_document(document)
        if results and len(results[0]) != self.expected_dim:
            raise ValueError(
                f"Embedding dimension mismatch: expected {self.expected_dim}, "
                f"got {len(results[0])}. Check your embedding model configuration."
            )
        return results

    def warmup(self) -> None:
        """Ensures the provider is ready for usage."""
        self.provider.warmup()