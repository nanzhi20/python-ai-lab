from rag.embedding_service import EmbeddingService, MODEL_NAME
from rag.document_loader import load_document
from rag.text_splitter import split_markdown_chunks
from pathlib import Path

from rag.vector_store import (
    create_chroma_client,
    get_or_create_knowledge_collection
)


PROJECT_ROOT = Path(__file__).resolve().parent
KNOWLEDGE_PATH = PROJECT_ROOT / "data" / "knowledge.md"


def main():
    document = load_document(KNOWLEDGE_PATH)
    chunks = split_markdown_chunks(text=document, source="knowledge.md")

    client = create_chroma_client()
    collection = get_or_create_knowledge_collection(client)

    embedding_service = EmbeddingService()

    documents = [
        chunk.content
        for chunk in chunks
    ]

    embeddings = embedding_service.encode_documents(documents)

    ids = [
        chunk.id
        for chunk in chunks
    ]

    metadatas = [
        {
            "source": chunk.source,
            "section": chunk.section,
            "content_hash": chunk.content_hash,
            "embedding_model": MODEL_NAME
        }
        for chunk in chunks
    ]

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    existing_result = collection.get(
        include=[]
    )

    existing_ids = set(existing_result["ids"])
    current_ids = set(ids)

    stale_ids = list(
        existing_ids - current_ids
    )

    if stale_ids:
        collection.delete(ids=stale_ids)

    print(f"本次处理知识点:{len(chunks)}")
    print(f"当前向量库记录数量:{collection.count()}")


if __name__ == "__main__":
    main()
