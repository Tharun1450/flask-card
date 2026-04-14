import requests
from config import OLLAMA_BASE_URL, OLLAMA_EMBED_MODEL

def generate_embedding(text: str) -> list[float]:
    """
    Generate embedding for a given text using Ollama.
    Uses the nomic-embed-text model.
    """
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/embeddings",
            json={
                "model": OLLAMA_EMBED_MODEL,
                "prompt": text
            },
            timeout=120
        )
        response.raise_for_status()
        data = response.json()
        return data.get("embedding", [])
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return []
