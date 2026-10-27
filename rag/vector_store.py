from pathlib import Path

import chromadb


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHROMA_PATH = PROJECT_ROOT / "data" / "chroma_db"

COLLECTION_NAME = "knowledge_chunks"

def create_chroma_client():
    return chromadb.PersistentClient(
        path=str(CHROMA_PATH)
    )


def get_knowledge_collection(client):
    return client.get_collection(
        name=COLLECTION_NAME,
        embedding_function=None
    )


def get_or_create_knowledge_collection(client):
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=None,
        metadata={
            "hnsw:space": "cosine"
        }
    )