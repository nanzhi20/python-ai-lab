from config import load_settings
from deepseek_client import DeepSeekClient
from openai import AuthenticationError, APIError, APIConnectionError
from rag.document_loader import load_document
from rag.text_splitter import split_markdown_sections
from rag.retriever import retrieve
from rag.prompt_builder import build_rag_prompt


def main():
    try:
        settings = load_settings()
        client = DeepSeekClient(settings)
        question = input("请输入问题：")

        text = load_document("data/knowledge.md")
        chunks = split_markdown_sections(text)

        retrieval_results = retrieve(question=question, chunks=chunks)
        if not retrieval_results:
            print("根据现有资料无法确定。")
            return

        print("------------------------------------------")
        print("检索到的参考资料如下")
        for index, retrieval_result in enumerate(retrieval_results, start=1):
            print(
                f"\n--- 参考片段 {index}，"
                f"分数 {retrieval_result.score} ---"
            )
            print(retrieval_result.chunk)
        print("------------------------------------------")

        references = [
            result.chunk
            for result in retrieval_results
        ]
        final_prompt = build_rag_prompt(question=question, context_chunks=references)

        result = client.chat(question=final_prompt)
        print("模型回答:")
        print(result.content)
        print(f"消耗token总数：{result.total_tokens}")


    except FileNotFoundError as error:
        print(f"知识库读取失败：{error}")
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
