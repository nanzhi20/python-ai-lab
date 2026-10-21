from sentence_transformers import SentenceTransformer


MODEL_NAME = "BAAI/bge-small-zh-v1.5"
QUERY_INSTRUCTION = "为这个句子生成表示以用于检索相关文章："


class EmbeddingService:
    def __init__(
            self,
            model_name: str = MODEL_NAME,
    ):
        self._model = SentenceTransformer(model_name)


    def encode_query(
            self,
            query: str
    ) -> list[float]:
        if not query or not query.strip():
            raise ValueError("问题不能为空")

        normalized_query = QUERY_INSTRUCTION + query.strip()

        query_embedding = self._model.encode(
            normalized_query,
            normalize_embeddings=True
        )

        return query_embedding.tolist()


    def encode_documents(
            self,
            documents: list[str]
    ) -> list[list[float]]:
        if not documents:
            raise ValueError("文档不能为空")

        normalized_documents = [
            document.strip() for document in documents
        ]

        if any(
            not document
            for document in normalized_documents
        ):
            raise ValueError("文档不能为空")

        documents_embeddings = self._model.encode(documents, normalize_embeddings=True)
        return documents_embeddings.tolist()
