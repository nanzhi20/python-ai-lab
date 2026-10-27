from config import load_settings
from deepseek_client import DeepSeekClient
from openai import AuthenticationError, APIError, APIConnectionError
from rag.vector_store import create_chroma_client,get_knowledge_collection
from rag.vector_retriever import retrieve_by_vector
from rag.prompt_builder import build_rag_prompt
from rag.embedding_service import EmbeddingService
from chromadb.errors import NotFoundError


def main():
    try:
        settings = load_settings()
        client = DeepSeekClient(settings)
        question = input("请输入问题：")

        chroma_client = create_chroma_client()
        collection = get_knowledge_collection(chroma_client)
        embedding_service = EmbeddingService()

        retrieval_results = retrieve_by_vector(question=question, collection=collection, embedding_service=embedding_service)
        if not retrieval_results:
            print("根据现有资料无法确定。")
            return

        references = [
            result.content
            for result in retrieval_results
        ]
        final_prompt = build_rag_prompt(question=question, context_chunks=references)

        result = client.chat(question=final_prompt)
        print("模型回答:")
        print(result.content)
        print(f"消耗token总数：{result.total_tokens}")

    except NotFoundError:
        print("尚未建立向量知识库，请先运行 index_documents.py")
    except ValueError as error:
        print(f"输入或配置错误:{error}")
    except AuthenticationError:
        print("身份认证失败，请检查 API KEY")
    except APIConnectionError:
        print("无法连接模型服务，请检查网络和服务地址")
    except APIError as error:
        print(f"模型服务调用失败:{error}")


if __name__ == "__main__":
    main()
