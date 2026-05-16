import hashlib
import math
import re


class EmbeddingService:
    def embed(self, text: str, dimensions: int = 128) -> list[float]:
        vector = [0.0] * dimensions
        tokens = re.findall(r"[a-zA-Z0-9+#.]+", text.lower())
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:2], "big") % dimensions
            sign = 1 if digest[2] % 2 == 0 else -1
            vector[index] += sign
        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [round(value / norm, 6) for value in vector]

    def cosine(self, left: list[float] | None, right: list[float] | None) -> float:
        if not left or not right or len(left) != len(right):
            return 0.0
        return max(0.0, min(1.0, sum(a * b for a, b in zip(left, right, strict=True))))
