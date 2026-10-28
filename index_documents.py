from pathlib import Path
from rag.knowledge_chunk import KnowledgeChunk
from rag.embedding_service import (EmbeddingService, MODEL_NAME)
from rag.document_loader import load_document
from rag.text_splitter import split_markdown_chunks
from rag.vector_store import (create_chroma_client, get_or_create_knowledge_collection)



PROJECT_ROOT = Path(__file__).resolve().parent
KNOWLEDGE_PATH = PROJECT_ROOT / 'data' / 'knowledge.md'
KNOWLEDGE_NAME = KNOWLEDGE_PATH.name


def load_existing_metadata(
        collection,
        source: str
) -> dict[str, dict]:
    result = collection.get(
        where={
            "source": source,
        },
        include=[
            'metadatas'
        ]
    )

    ids = result['ids']
    metadatas = result['metadatas']

    return {
        record_id: metadata or {}
        for record_id, metadata in zip(ids, metadatas)
    }


def build_metadata(
        chunk: KnowledgeChunk
) -> dict[str, str]:
    return {
        "source": chunk.source,
        "section": chunk.section,
        "content_hash": chunk.content_hash,
        "embedding_model": MODEL_NAME
    }


def select_chunks_to_upsert(
        chunks: list[KnowledgeChunk],
        existing_metadata: dict[str, dict]
) -> tuple[
    list[KnowledgeChunk],
    int,
    int,
    int
]:
    chunks_to_upsert: list[KnowledgeChunk] = []

    new_count = 0
    updated_count = 0
    unchanged_count = 0

    for chunk in chunks:
        metadata = existing_metadata.get(chunk.id)
        if metadata is None:
            chunks_to_upsert.append(chunk)
            new_count += 1
            continue

        content_changed = (metadata.get('content_hash') != chunk.content_hash)

        model_changed = (metadata.get('embedding_model') != MODEL_NAME)

        if content_changed or model_changed:
            chunks_to_upsert.append(chunk)
            updated_count += 1
        else:
            unchanged_count += 1

    return (
        chunks_to_upsert,
        new_count,
        updated_count,
        unchanged_count
    )


def upsert_chunks(
        collection,
        chunks: list[KnowledgeChunk],
) -> None:
    if not chunks:
        return

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
        build_metadata(chunk)
        for chunk in chunks
    ]

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )



def delete_stale_chunks(
        collection,
        existing_ids: set[str],
        current_ids: set[str]
) -> int:
    stale_ids = list(existing_ids - current_ids)
    if stale_ids:
        collection.delete(
            ids=stale_ids
        )
    return len(stale_ids)



def main():
    document = load_document(KNOWLEDGE_PATH)

    chunks = split_markdown_chunks(text=document, source=KNOWLEDGE_NAME)

    if not chunks:
        raise ValueError("没有从知识文档中切分出任何知识片段")

    client = create_chroma_client()
    collection = get_or_create_knowledge_collection(client)

    existing_metadata = load_existing_metadata(collection, KNOWLEDGE_NAME)

    (chunks_to_upsert, new_count, updated_count, unchanged_count) \
        = select_chunks_to_upsert(chunks=chunks, existing_metadata=existing_metadata)

    upsert_chunks(collection=collection, chunks=chunks_to_upsert)

    existing_ids = set(existing_metadata.keys())
    current_ids = {
        chunk.id
        for chunk in chunks
    }

    delete_count = delete_stale_chunks(
        collection=collection,
        existing_ids=existing_ids,
        current_ids=current_ids
    )

    print(f"当前知识片段总数:{len(chunks)}")
    print(f"本次新增:{new_count}")
    print(f"本次更新:{updated_count}")
    print(f"本次无变化:{unchanged_count}")
    print(f"本次删除:{delete_count}")
    print(f"当前向量库记录数量:{collection.count()}")


if __name__ == "__main__":
    main()