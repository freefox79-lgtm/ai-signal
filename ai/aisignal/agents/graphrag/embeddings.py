import requests
import numpy as np
import os

class OllamaClient:
    """
    Ollama API Client for Embeddings
    """
    def __init__(self, base_url=None, model="nomic-embed-text"):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model

    def embed(self, text: str) -> list:
        """
        Generate embedding for text using Ollama
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": text
                },
                timeout=5
            )
            response.raise_for_status()
            return response.json()["embedding"]
        except Exception as e:
            print(f"⚠️ [Embeddings] Ollama connection failed: {e}")
            print(f"   Using MOCK embedding (random noise) for: {text[:20]}...")
            # Return random vector (dim 768 for nomic-embed-text approximation)
            return np.random.rand(768).tolist()

def get_ollama_client():
    return OllamaClient()
