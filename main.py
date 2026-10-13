from config import load_settings
from deepseek_client import DeepSeekClient
from openai import AuthenticationError,APIError,APIConnectionError

def main():
    try:
        settings = load_settings()
        client = DeepSeekClient(settings)
        question = input("请输入问题：")
        result = client.chat(question)

        print("模型回答:")
        print(result.content)

        print(f"消耗token总数：{result.total_tokens}")

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
