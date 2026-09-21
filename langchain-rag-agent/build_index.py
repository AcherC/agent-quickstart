"""
构建向量索引：把docs/目录下的文档切块、向量化、存入ChromaDB
"""
import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from pathlib import Path

# ========== 1. 加载文档 ==========
# 获取脚本所在目录
BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
CHROMA_DIR = BASE_DIR / "chroma_db"

print(f"脚本目录：{BASE_DIR}")
print(f"文档目录：{DOCS_DIR}")
print(f"文档存在：{DOCS_DIR.exists()}")
print("步骤1：加载文档...")
loader = DirectoryLoader(
    str(DOCS_DIR),   # 用绝对路径
    glob="**/*.txt",
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8"}
)
documents = loader.load()
print(f"加载了 {len(documents)} 个文档")

# ========== 2. 切块 ==========
print("步骤2：切块...")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,        # 每块最大300字符
    chunk_overlap=50,      # 块之间重叠50字符
    separators=["\n\n", "\n", "。", "！", "？", " ", ""],
    length_function=len,
    add_start_index=True   # 记录块在原文的位置，用于引用溯源
)
chunks = splitter.split_documents(documents)
print(f"切成了 {len(chunks)} 块")

# ========== 3. 加载Embedding模型 ==========
print("步骤3：加载Embedding模型（首次会下载，约100MB）...")
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-zh-v1.5",  # 中文小模型，快且效果好
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}  # 归一化，余弦=内积
)

# ========== 4. 存入ChromaDB ==========
print("步骤4：向量化并存入ChromaDB...")
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db",  # 持久化目录
    collection_name="enterprise_docs"  # 集合名
)
print(f"索引构建完成！向量库位置：./chroma_db")

# ========== 5. 验证 ==========
print("\n步骤5：验证检索...")
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
results = retriever.invoke("怎么算加班费用？")
for i, doc in enumerate(results):
    print(f"\n--- 结果{i+1} ---")
    print(f"来源：{doc.metadata.get('source')}")
    print(f"内容：{doc.page_content[:100]}...")