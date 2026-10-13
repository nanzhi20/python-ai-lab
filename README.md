# Python AI Lab

一个用于学习 Python AI 应用开发的练习项目。当前版本通过 DeepSeek 提供的 OpenAI 兼容接口完成命令行单轮问答，并展示本次请求消耗的 Token 总数。

## 当前功能

- 从终端读取用户问题
- 调用 DeepSeek 模型生成回答
- 将 SDK 响应转换为项目自己的 `ChatResult` 对象
- 输出模型回答和 Token 消耗总数
- 拒绝空字符串和纯空白问题
- 对认证失败、网络连接失败和其他 API 调用失败给出提示
- 从 `.env` 加载 API Key、接口地址和模型名称

## 环境要求

- Python 3.13 或更高版本
- [uv](https://docs.astral.sh/uv/)
- 可用的 DeepSeek API Key

## 安装与运行

在项目根目录执行：

```powershell
uv sync
```

复制环境变量示例文件：

```powershell
Copy-Item .env.example .env
```

编辑 `.env`，将占位内容替换为自己的 API Key：

```dotenv
DEEPSEEK_API_KEY=replace_with_your_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-flash
```

启动程序：

```powershell
uv run python main.py
```

根据终端提示输入问题，程序会输出模型回答和本次请求消耗的 Token 总数。

## 配置说明

| 环境变量 | 作用 | 默认值 |
| --- | --- | --- |
| `DEEPSEEK_API_KEY` | DeepSeek API 身份认证密钥 | 无，必须配置 |
| `DEEPSEEK_BASE_URL` | DeepSeek API 基础地址 | `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | 调用的模型名称 | `deepseek-flash` |

真实 API Key 只能保存在本地 `.env` 中。`.env` 已加入 `.gitignore`，不应提交到 Git 仓库；`.env.example` 只保留可公开的示例配置。

## 项目结构

```text
python-ai-lab/
├── main.py                 # 命令行入口、结果展示和异常提示
├── config.py               # 环境变量读取与配置校验
├── deepseek_client.py      # DeepSeek 调用及响应转换
├── pyproject.toml          # 项目元数据和依赖声明
├── uv.lock                 # uv 锁定的依赖版本
├── .python-version         # 项目使用的 Python 版本
├── .env.example            # 可提交的环境变量示例
├── .env                    # 本地真实配置，不提交
└── .gitignore              # Git 忽略规则
```

## 代码职责

- `main.py`：组织程序流程，接收终端输入，并把异常转换为用户可理解的提示。
- `config.py`：加载环境变量并创建不可变的 `DeepSeekSettings` 配置对象。
- `deepseek_client.py`：封装 OpenAI 兼容客户端、发送单轮问题，并将外部响应转换为 `ChatResult`。

## 当前范围

当前版本只实现最小单轮问答，暂不包含：

- 多轮对话和上下文记忆
- 流式输出
- RAG、Embedding 和向量数据库
- 异步调用与自动重试
- Web 页面或 HTTP 接口

这些能力可以在后续学习阶段逐步添加。
