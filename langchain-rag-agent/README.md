# 企业知识库 Agent 助手

基于 LangChain + DeepSeek 构建的企业内部知识库智能问答 Agent，整合 RAG 检索、Agentic 决策与多轮对话记忆，支持员工自助查询公司制度、流程规范等内部知识。

## 项目背景

企业内部制度文档分散在多个系统中，员工查找信息依赖关键词搜索，无法处理自然语言复杂查询（如“请假流程和迟到处罚分别是什么”）。本项目通过 RAG + Agent 架构，让员工用自然语言即可获取准确答案，并附带引用来源。

## 核心功能

- **Agentic RAG**：将向量检索封装为工具，由 Agent 通过 ReAct 循环自主决定是否检索、检索几次、是否组合其他工具，避免无效调用
- **引用溯源**：每条回答附带来源文件，解决 RAG “幻觉引用”问题
- **多轮对话记忆**：同一会话内 Agent 能理解追问，不同会话之间完全隔离
- **结构化输出**：答案以 JSON 格式返回，包含 `answer` 和 `citations` 字段
- **LangSmith 评估**：集成自定义评估器与 RAGAS 指标，支持量化回归测试

## 技术栈

| 组件 | 技术 |
|------|------|
| 编排框架 | LangChain / LangGraph |
| LLM | DeepSeek API (deepseek-chat) |
| Embedding | BGE-small-zh-v1.5 |
| 向量数据库 | ChromaDB |
| 评估平台 | LangSmith + RAGAS |
| 开发语言 | Python 3.11 |

## 项目结构

```text
enterprise-rag-agent/
├── docs/                    # 知识库文档
│   ├── hr_policy.txt
│   └── product_guide.txt
├── chroma_db/               # 向量库持久化目录（不提交到Git）
├── rag_agent.py             # Agent 主程序
├── build_index.py           # 构建向量索引
├── evaluate_agent.py        # LangSmith 评估脚本
├── config.py                # 配置管理
├── .env                     # 环境变量（不提交到Git）
├── .gitignore
└── requirements.txt

## 快速开始
1. 环境准备
bash
# 创建 conda 环境
conda create -n rag-agent python=3.11 -y
conda activate rag-agent

# 安装依赖
pip install -r requirements.txt
2. 配置环境变量
bash
# 复制模板
cp .env.example .env

# 编辑 .env，填入你的 API Key
.env 文件内容：

env
# DeepSeek API
DEEPSEEK_API_KEY=sk-your-deepseek-key

# LangSmith（可选，用于追踪和评估）
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=lsv2_sk-your-langsmith-key
LANGSMITH_PROJECT=enterprise-rag-agent
3. 构建向量索引
bash
python build_index.py
4. 运行 Agent
bash
python rag_agent.py
## 使用示例
text
你：请假流程是什么？
  [决策] 调用 search_java_knowledge({'query': '请假流程'})
  [工具] 返回 3 条相关文档
助手：所有休假均需提前通过公司办公系统提交正式申请，按照层级审批流程完成审批...[1]

你：那迟到怎么处罚？
  [决策] 调用 search_java_knowledge({'query': '迟到 处罚'})
  [工具] 返回 3 条相关文档
助手：迟到早退按照时长分级处理，单次迟到15分钟以内口头提醒...[2]
## 项目架构
text
用户输入
   │
   ▼
┌──────────────────────────────────────────┐
│  Checkpointer（短期记忆）                  │
│  读取当前 thread_id 的历史消息             │
├──────────────────────────────────────────┤
│  Agent（create_agent）                    │
│  ├─ 模型决策：要不要检索？调哪个工具？      │
│  ├─ 工具1：search_java_knowledge（RAG）   │
│  ├─ 工具2：calculator                     │
│  └─ ReAct 循环：直到给出最终回答           │
├──────────────────────────────────────────┤
│  返回结果 + 保存状态到 Checkpointer        │
└──────────────────────────────────────────┘
## 评估体系
本项目使用 LangSmith 建立评估数据集，包含以下评估器：

评估器	类型	作用
answer_correctness	自定义（LLM-as-judge）	判断回答与参考答案语义是否一致
retrieval_relevance	自定义（LLM-as-judge）	判断检索到的文档是否与问题相关
faithfulness	RAGAS	答案是否完全基于检索内容（衡量幻觉）
answer_relevancy	RAGAS	答案是否切题
运行评估：

bash
python evaluate_agent.py