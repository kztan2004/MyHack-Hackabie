import numpy as np
from app.core.config import Settings


class EmbeddingService:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def embed(self, text: str) -> list[float]:
        if not self.settings.gemini_api_key:
            # Fallback to zero vector if no key
            return [0.0] * 768

        from google import genai
        from google.genai import types

        client = genai.Client(api_key=self.settings.gemini_api_key)
        response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=text,
            config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY"),
        )
        return response.embeddings[0].values

    def cosine(self, left: list[float] | None, right: list[float] | None) -> float:
        if not left or not right or len(left) != len(right):
            return 0.0
        
        vec1 = np.array(left)
        vec2 = np.array(right)
        
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        similarity = np.dot(vec1, vec2) / (norm1 * norm2)
        return float(max(0.0, min(1.0, similarity)))
