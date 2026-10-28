# Python AI Lab

一个用于学习 Python AI 应用开发的练习项目。目前项目实现了基于本地 Markdown 知识库、BGE 中文文本向量、Chroma 向量数据库和 DeepSeek 的最小 RAG（检索增强生成）链路。

项目将知识库建库与日常问答分离：文档向量只在手动建库时计算，正常问答只计算用户问题的向量，从而避免重复处理知识文档。

## 当前功能

- 从本地 Markdown 文件读取知识资料
- 按 Markdown 二级标题切分知识片段
- 为知识片段生成稳定 ID 和内容哈希
- 根据内容哈希和 Embedding 模型执行增量建库
- 未发生变化时跳过模型加载和向量计算
- 使用 `BAAI/bge-small-zh-v1.5` 生成本地文本向量
- 为查询添加 BGE 中文检索指令，文档保持原文编码
- 使用 Chroma 将文档、向量和 Metadata 持久化到本地
- 使用余弦距离执行 Top-K 语义检索
- 使用 `0.60` 作为第一版最大距离阈值
- 将检索片段与用户问题组合成 RAG Prompt
- 通过 DeepSeek 的 OpenAI 兼容接口生成回答
- 输出模型回答和 Token 总用量
- 使用固定问题集统计 Hit@1、Hit@2 和距离分布
- 比较多个候选距离阈值的接受、拒绝效果
- 对空问题、无检索结果、配置错误和模型服务异常进行处理

## 技术栈

- Python 3.13+
- uv
- OpenAI Python SDK
- DeepSeek OpenAI 兼容接口
- sentence-transformers
- `BAAI/bge-small-zh-v1.5`
- Chroma
- NumPy
- python-dotenv

## 项目结构

```text
python-ai-lab/
├── data/
│   ├── knowledge.md          # LanShare 知识库原文
│   ├── eval_questions.json   # 检索评估问题
│   └── chroma_db/            # Chroma 本地数据，不提交到Git
├── labs/
│   ├── chroma_lab/           # Chroma 基础练习
│   ├── embedding_lab/        # Embedding与相似度练习
│   └── sqlite_lab/           # SQLite分层与事务练习
├── rag/
│   ├── document_loader.py    # 读取知识文档
│   ├── text_splitter.py      # 按二级标题生成结构化知识片段
│   ├── knowledge_chunk.py    # KnowledgeChunk与哈希生成
│   ├── embedding_service.py  # 本地查询、文档向量化
│   ├── vector_store.py       # Chroma路径、客户端和Collection
│   ├── vector_retriever.py   # Top-K向量检索与距离过滤
│   ├── vector_evaluator.py   # 命中率、距离与阈值评估
│   └── prompt_builder.py     # 构建RAG增强提示词
├── config.py                 # DeepSeek环境配置
├── deepseek_client.py        # 模型请求与ChatResult转换
├── index_documents.py        # 手动建立或同步向量知识库
├── main.py                   # 命令行RAG问答入口
├── pyproject.toml            # 项目依赖与元数据
├── uv.lock                   # uv依赖锁文件
├── .env.example              # 环境变量示例
└── .gitignore                # 本地配置和运行数据忽略规则
```

## 安装

在项目根目录执行：

```powershell
uv sync
```

首次使用 sentence-transformers 模型时需要下载模型文件，因此需要能够访问对应的模型仓库。模型下载完成后会使用本地缓存。

## 配置 DeepSeek

复制环境变量示例：

```powershell
Copy-Item .env.example .env
```

编辑 `.env`：

```dotenv
DEEPSEEK_API_KEY=replace_with_your_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-flash
```

真实 API Key 只能保存在本地 `.env` 中。`.env` 已加入 `.gitignore`，不应提交到 Git 仓库。

## 建立向量知识库

首次运行项目前，执行：

```powershell
uv run python index_documents.py
```

建库流程：

```text
data/knowledge.md
    ↓
按Markdown二级标题切分
    ↓
生成KnowledgeChunk、稳定ID和内容哈希
    ↓
读取当前来源在Chroma中的Metadata
    ↓
比较ID、content_hash和embedding_model
    ├── 新增或发生变化：计算向量并upsert
    ├── 完全未变化：跳过模型加载和向量计算
    └── 已从文档删除：从Chroma中删除旧记录
```

增量判断规则：

- 数据库中没有相同 ID：新增片段并生成向量
- ID 相同，但 `content_hash` 不同：正文已变化，重新生成向量
- ID 相同，但 `embedding_model` 不同：模型已变化，重新生成向量
- ID、内容哈希和模型均相同：保留原记录，不加载 Embedding 模型
- 数据库中存在、当前来源中已不存在：删除过期记录

脚本按 `source` 查询和清理记录，因此同步当前 `knowledge.md` 时不会误删其他来源的数据。每次运行会输出新增、更新、未变化、删除以及向量库总记录数。

以下情况需要重新运行建库脚本：

- 首次建立知识库
- 修改了 `data/knowledge.md`
- 修改了文档切分规则
- 更换为相同向量维度的 Embedding 模型
- 删除了 `data/chroma_db/`

## 运行问答程序

完成建库后执行：

```powershell
uv run python main.py
```

主流程：

```text
用户输入问题
    ↓
BGE生成问题向量
    ↓
Chroma执行Top-K余弦距离检索
    ↓
过滤距离大于0.60的结果
    ↓
将检索片段和问题组合成Prompt
    ↓
DeepSeek生成基于资料的回答
```

如果没有片段通过距离阈值，程序会直接输出：

```text
根据现有资料无法确定。
```

此时不会调用 DeepSeek，能够避免一次不必要的模型请求。

如果尚未建立 Chroma Collection，程序会提示先执行 `index_documents.py`。

## 检索评估

运行：

```powershell
uv run python -m rag.vector_evaluator
```

评估器会：

- 使用 `data/eval_questions.json` 中的问题进行检索
- 对可回答问题统计 Hit@1 和 Hit@2
- 记录可回答问题与知识库外问题的 Top-1 距离
- 输出最小值、最大值和平均值
- 比较多个候选距离阈值的误接受与误拒绝数量

当前评估集包含：

- 19 道知识库内问题
- 10 道知识库外问题

当前向量检索结果：

| 指标 | 结果 |
| --- | ---: |
| Hit@1 | 14/19，73.68% |
| Hit@2 | 18/19，94.74% |
| 可回答问题 Top-1 距离 | 0.2819～0.5853，平均0.4272 |
| 知识库外问题 Top-1 距离 | 0.4811～0.7944，平均0.6622 |

候选阈值中，`0.60` 的当前结果为：

| 分类结果 | 数量 |
| --- | ---: |
| 正常问题正确接受 | 19/19 |
| 正常问题误拒 | 0/19 |
| 知识库外问题正确拒绝 | 6/10 |
| 知识库外问题误接受 | 4/10 |
| 总体区分准确率 | 86.21% |

`0.60` 是根据当前小型知识库和评估集选择的第一版经验阈值，不是 BGE 或 Chroma 的通用参数。更换知识库、切分规则或 Embedding 模型后，应重新执行评估。

## 关键设计说明

### 查询与文档采用不同编码方式

查询会添加 BGE 推荐的中文检索指令：

```text
为这个句子生成表示以用于检索相关文章：
```

知识文档不添加该前缀。两者均使用归一化向量。

### 文档向量不会在每次问答时重新计算

文档向量由 `index_documents.py` 预先生成并存入 Chroma。运行 `main.py` 时只计算用户问题的向量。

### ID与内容哈希职责不同

- ID 根据来源和章节生成，用于稳定定位记录
- 内容哈希根据正文生成，用于标识正文是否发生变化

当前切分规则假设一个二级标题对应一个知识片段。如果未来需要把同一章节继续切成多段，ID还应包含片段序号等稳定定位信息。

## 数据与安全

以下内容不会提交到 Git：

```text
.env
.venv/
.idea/
data/chroma_db/
data/chroma_demo/
data/sqlite_demo.db
```

项目只用于本地学习。当前没有实现用户认证、权限控制、敏感信息过滤或面向公网的服务接口。

## 当前限制

- 知识库来源目前只有一个 Markdown 文件
- 文档切分只支持 Markdown 二级标题
- 增量建库目前只处理单个 Markdown 来源文件
- Chroma Collection 的向量维度固定；更换为不同维度的模型时，需要删除旧向量库或创建新 Collection 后完整重建
- 距离阈值不能完全区分知识库内外问题
- 评估集规模较小，结果不能代表通用性能
- 仅支持单轮命令行问答
- 不支持流式输出和多轮会话记忆
- 不支持 PDF、Word 等复杂文档解析
- 不包含 Web 页面或 HTTP 接口
- 未使用 LangChain 或 LlamaIndex

## 后续方向

- 增加更多知识库外评估问题
- 分析 Hit@1 和 Hit@2 失败案例
- 支持多个知识文档和来源过滤
- 增加对 PDF、Word 等文件的解析
- 增加多轮对话或流式输出
- 为 RAG 结果增加引用展示


