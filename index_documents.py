from pathlib import Path
from rag.knowledge_chunk import KnowledgeChunk
from rag.embedding_service import (EmbeddingService, MODEL_NAME)
from rag.document_loader import load_document
from rag.text_splitter import split_markdown_chunks
from rag.vector_store import (create_chroma_client, get_or_create_knowledge_collection)



PROJECT_ROOT = Path(__file__).resolve().parent
KNOWLEDGE_DIRECTORY = PROJECT_ROOT / 'data' / 'knowledge'


def find_knowledge_files(
        directory: Path
) -> list[Path]:
    if not directory.is_dir():
        raise FileNotFoundError(
            f"知识库目录不存在:{directory}"
        )

    files = sorted(
        directory.rglob("*.md")
    )
    if not files:
        raise ValueError(
            f"知识库目录 {directory} 中没有Markdown文件"
        )
    return files


def load_knowledge_chunks(
        files: list[Path],
        knowledge_directory: Path
) -> list[KnowledgeChunk]:
    chunks: list[KnowledgeChunk] = []
    existing_ids: set[str] = set()

    for file_path in files:
        document = load_document(file_path)

        source = file_path.relative_to(knowledge_directory).as_posix()

        file_chunks = split_markdown_chunks(
            text=document,
            source=source
        )
        if not file_chunks:
            raise ValueError(f"没有从知识文档 {file_path} 中切分出片段 ")

        for chunk in file_chunks:
            if chunk.id in existing_ids:
                raise ValueError(
                    f"检测到重复知识库片段:"
                    f"source={chunk.source}"
                    f"section={chunk.section}"
                )
            chunks.append(chunk)
            existing_ids.add(chunk.id)

    return chunks


def load_existing_metadata(
        collection,
) -> dict[str, dict]:
    result = collection.get(
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

    files = find_knowledge_files(KNOWLEDGE_DIRECTORY)

    chunks = load_knowledge_chunks(files, KNOWLEDGE_DIRECTORY)

    client = create_chroma_client()
    collection = get_or_create_knowledge_collection(client)

    existing_metadata = load_existing_metadata(collection)

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

    print(f"知识文档数量:{len(files)}")
    print(f"当前知识片段总数:{len(chunks)}")
    print(f"本次新增:{new_count}")
    print(f"本次更新:{updated_count}")
    print(f"本次无变化:{unchanged_count}")
    print(f"本次删除:{delete_count}")
    print(f"当前向量库记录数量:{collection.count()}")


if __name__ == "__main__":
    main()