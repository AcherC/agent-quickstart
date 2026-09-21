"""
RAG Agent主程序
"""
import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"  
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.prompts import ChatPromptTemplate
# ========== 1. 加载向量库 ==========
print("加载向量库...")
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-zh-v1.5",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings,
    collection_name="enterprise_docs"
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# ========== 2. 初始化模型 ==========
# 用Ollama本地模型（免费），也可以换成ChatOpenAI
model = ChatOllama(model="qwen2.5:7b", temperature=0)

# ========== 3. 定义Prompt ==========
prompt = ChatPromptTemplate.from_template("""
你是一个Java面试助手。基于参考资料回答问题，并给出引用。

参考资料：
{context}

问题：{question}

请按以下JSON格式输出：
{{
  "answer": "你的回答",
  "citations": [
    {{"index": 1, "source": "来源文件名", "content": "引用的原文片段"}}
  ]
}}

只输出JSON，不要其他内容。
""")

# ========== 4. 格式化检索结果 ==========
def format_docs_with_index(docs):
    """给文档编号，方便模型引用"""
    formatted = []
    for i, doc in enumerate(docs):
        source = doc.metadata.get("source", "未知")
        formatted.append(f"[{i+1}] 来源：{source}\n内容：{doc.page_content}")
    return "\n\n".join(formatted)

# ========== 5. 组装基础RAG链 ==========
rag_chain = (
    RunnableParallel(
        context=retriever | format_docs_with_index,
        question=RunnablePassthrough()
    )
    | prompt
    | model
    | JsonOutputParser()
)

# ========== 6. 测试 ==========
if __name__ == "__main__":
    result = rag_chain.invoke("怎么算加班费用？")
    print("回答：", result["answer"])
    print("\n引用：")
    for c in result["citations"]:
        print(f"  [{c['index']}] {c['source']}")
        print(f"      {c['content'][:50]}...")