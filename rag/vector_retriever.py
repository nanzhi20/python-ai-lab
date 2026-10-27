from dataclasses import dataclass
from rag.embedding_service import EmbeddingService


DEFAULT_MAX_DISTANCE = 0.60


@dataclass(frozen=True)
class VectorRetrievalResult:
    id: str
    content: str
    source: str
    section: str
    distance: float


def retrieve_by_vector(
        question: str,
        collection,
        embedding_service: EmbeddingService,
        top_k: int = 2,
        max_distance: float | None = DEFAULT_MAX_DISTANCE
) -> list[VectorRetrievalResult]:
    if not question or not question.strip():
        raise ValueError("检索问题不能为空")

    if top_k <= 0:
        raise ValueError("返回条数必须大于0")

    if max_distance is not None and max_distance < 0:
        raise ValueError("最大距离不能小于0")

    record_count = collection.count()
    if record_count == 0:
        return []
    actual_top_k = min(top_k, record_count)

    query_embedding = embedding_service.encode_query(question)

    query_results = collection.query(
        query_embeddings=[
            query_embedding
        ],
        n_results=actual_top_k,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    ids = query_results["ids"][0]
    documents = query_results["documents"][0]
    metadatas = query_results["metadatas"][0]
    distances = query_results["distances"][0]

    return [
        VectorRetrievalResult(
            id=record_id,
            content=document,
            section=metadata["section"],
            source=metadata["source"],
            distance=float(distance)
        )
        for record_id, document, metadata, distance in zip(ids, documents, metadatas, distances)
        if (
                max_distance is None
                or distance <= max_distance
        )
    ]


