import os
import chromadb
from chromadb.config import Settings
from config import CHROMA_DB_DIR

class VectorStore:
    def __init__(self):
        # Initialize persistent client for ChromaDB
        os.makedirs(CHROMA_DB_DIR, exist_ok=True)
        self.client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
        self.collection_name = "document_chunks"
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def clear(self):
        """Clear all existing documents from the collection."""
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        except ValueError:
            # Collection might not exist yet
            pass
        except Exception as e:
            print(f"Error clearing collection: {e}")

    def add_chunks(self, chunks: list[str], embeddings: list[list[float]], metadatas: list[dict]):
        """Add chunks, embeddings, and metadata to ChromaDB."""
        if not chunks or not embeddings:
            return
        
        # Give each chunk a unique ID based on index
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )

    def query(self, query_embedding: list[float], n_results: int = 5):
        """Query top-k similar chunks."""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results

# Singleton instance of VectorStore
vector_db = VectorStore()
