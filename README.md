# Python AI Lab

一个用于学习 Python AI 应用开发的练习项目。项目通过 DeepSeek 提供的 OpenAI 兼容接口完成命令行问答，并实现了一条基于本地 Markdown 知识库和关键词检索的最小 RAG 链路。

## 当前功能

- 从终端读取用户问题
- 从本地 Markdown 文件加载知识资料
- 按 Markdown 二级标题切分知识片段
- 使用 jieba 对中文问题和知识片段进行分词
- 根据问题与片段的共同词数量计算相关分数
- 选取分数最高的两个片段作为参考资料
- 将参考资料和问题组合成增强提示词
- 调用 DeepSeek 生成基于资料的回答
- 展示命中的知识片段、相关分数和模型回答
- 将 SDK 响应转换为项目自己的 `ChatResult` 对象
- 输出 Token 消耗总数
- 拒绝空字符串和纯空白问题
- 没有检索结果时直接提示现有资料无法确定
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

根据终端提示输入问题。程序会先输出检索到的知识片段和相关分数，再输出基于这些资料生成的回答。

可以使用以下问题验证当前知识库：

```text
同名文件会覆盖吗？
文字列表如何自动刷新？
项目可以直接暴露到公网吗？
```

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
├── data/
│   └── knowledge.md        # LanShare 本地知识资料
├── rag/
│   ├── document_loader.py  # 读取知识文档
│   ├── text_splitter.py    # 按 Markdown 标题切分片段
│   ├── retriever.py        # jieba 分词与关键词检索
│   └── prompt_builder.py   # 构建 RAG 增强提示词
├── main.py                 # 组织 RAG 流程、展示结果和处理异常
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

- `main.py`：组织文档加载、切分、检索、提示词构建和模型调用，并把异常转换为用户可理解的提示。
- `config.py`：加载环境变量并创建不可变的 `DeepSeekSettings` 配置对象。
- `deepseek_client.py`：封装 OpenAI 兼容客户端、发送单轮问题，并将外部响应转换为 `ChatResult`。
- `document_loader.py`：使用 `pathlib` 按 UTF-8 编码读取本地知识文档。
- `text_splitter.py`：按照 Markdown 二级标题把知识文档切成独立片段。
- `retriever.py`：使用 jieba 分词，以问题和片段的词语交集数量作为相关分数，并返回 Top-K 结果。
- `prompt_builder.py`：把检索资料、回答规则和原始问题组合成最终提示词。

## RAG 调用流程

```text
用户问题
    ↓
读取 data/knowledge.md
    ↓
按 Markdown 标题切分
    ↓
jieba 中文分词
    ↓
关键词交集评分与 Top-K 检索
    ↓
构建包含参考资料的增强提示词
    ↓
DeepSeek 生成回答
```

当前检索器的分数计算方式为：

```text
score = 问题词语集合与片段词语集合的交集数量
```

这种实现便于观察完整 RAG 链路，但只能识别字面上相同或相近的词语，不具备真正的向量语义理解能力。

## 当前范围

当前版本实现了关键词检索驱动的最小 RAG，暂不包含：

- 多轮对话和上下文记忆
- 流式输出
- Embedding 和向量语义检索
- 向量数据库
- PDF、Word 等复杂文档解析
- 文档上传与知识库管理
- LangChain 或 LlamaIndex
- 异步调用与自动重试
- Web 页面或 HTTP 接口

这些能力可以在后续学习阶段逐步添加。
