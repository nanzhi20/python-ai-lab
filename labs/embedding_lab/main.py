import numpy as np
from rag.embedding_service import  EmbeddingService

def cosine_similarity(first_embedding, second_embedding) -> float:
    first_length = np.linalg.norm(first_embedding)
    second_length = np.linalg.norm(second_embedding)

    denominator = first_length * second_length

    if denominator == 0:
        raise ValueError("不能计算零向量的余弦相似度")

    similarity = np.dot(first_embedding, second_embedding) / denominator
    return float(similarity)


def retrieve_documents(
        embedding_service: EmbeddingService,
        question: str,
        documents: list[str],
        top_k: int = 2
) -> list[dict]:
    if not question or not question.strip():
        raise ValueError("查询问题不能为空")
    if not documents:
        raise ValueError("待检索文档不能为空")
    if top_k <= 0:
        raise ValueError("top_k必须大于0")

    question_embedding = embedding_service.encode_query(question)

    document_embeddings = embedding_service.encode_documents(documents)

    similarities = (
        np.array(document_embeddings) @ np.array(question_embedding)
    )

    sorted_indices = np.argsort(similarities)[::-1]

    selected_indices = sorted_indices[:min(top_k, len(documents))]

    return [
        {
            'index': int(index),
            'document': documents[index],
            'similarity': float(similarities[index])
        }
        for index in selected_indices
    ]

def main():

    documents = [
        "同名文件不会相互覆盖。",
        "服务重启后，之前上传的文件仍然存在。",
        "文字列表使用JavaScript轮询自动更新。",
        "系统不适合直接暴露到公网。",
        "手机可以通过局域网IP和端口访问系统。"
    ]

    question = "电脑重新开机后，之前传上去的照片还在吗？"

    embedding_service = EmbeddingService()

    results = retrieve_documents(embedding_service=embedding_service, question=question, documents=documents, top_k=3)

    print(f"问题:{question}")
    print(f"检索结果:")
    for rank, result in enumerate(results, start=1):
        print(f"排名:{rank}")
        print(f"原始下标:{result['index']}")
        print(f"文档:{result['document']}")
        print(f"相似度:{result['similarity']:.4f}")




if __name__ == "__main__":
    main()