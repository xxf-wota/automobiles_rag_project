import json
import os
import sys
import time

import pandas as pd
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document

# 允许从任意目录运行：把项目根目录加入 sys.path，并基于脚本位置定位数据文件
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
sys.path.insert(0, PROJECT_ROOT)

from ai import LoadEmbeddingModel

load_dotenv()

# 数据集路径（基于脚本所在目录，避免依赖运行时的当前目录）
AUTOHOME_PATH = os.path.join(BASE_DIR, "汽车之家.csv")
AUTOMASTER_PATH = os.path.join(BASE_DIR, "汽车大师问答摘要.csv")

# 向量数据库配置
PERSIST_DIRECTORY = os.getenv("CHROMA_PATH")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

# 每批写入的文档数（控制显存占用并输出进度）
BATCH_SIZE = 1000


# 处理汽车之家.csv（GBK 编码的车型参数数据）
# 每一行是一个车型的参数记录，序列化为 JSON 字符串后入库，保留全部字段
def load_autohome_documents():
    df = pd.read_csv(AUTOHOME_PATH, encoding="gbk", low_memory=False)
    # 删除所有值都为空的列
    df = df.dropna(axis=1, how="all")
    print(f"[汽车之家] 读取到 {df.shape[0]} 行, {df.shape[1]} 列")

    documents = []
    for record in df.to_dict("records"):
        content = json.dumps(record, ensure_ascii=False)
        documents.append(
            Document(page_content=content, metadata={"source": AUTOHOME_PATH})
        )
    print(f"[汽车之家] 生成 {len(documents)} 条文档")
    return documents


# 处理汽车大师问答摘要.csv（UTF-8 编码的维修保养问答数据）
# 以「品牌/车型/问题/解答」拼成一段纯文本入库，问题用于检索匹配，解答用于回答
def load_automaster_documents():
    df = pd.read_csv(AUTOMASTER_PATH, encoding="utf-8-sig", low_memory=False)
    # 空值统一转成空字符串，避免出现 "nan"
    df = df.fillna("")
    print(f"[汽车大师] 读取到 {df.shape[0]} 行, {df.shape[1]} 列")

    documents = []
    for row in df.itertuples(index=False):
        brand = str(row.Brand).strip()
        model = str(row.Model).strip()
        question = str(row.Question).strip()
        report = str(row.Report).strip()
        content = f"品牌：{brand}\n车型：{model}\n问题：{question}\n解答：{report}"
        documents.append(
            Document(
                page_content=content,
                metadata={
                    "source": AUTOMASTER_PATH,
                    "qid": str(row.QID),
                    "brand": brand,
                    "model": model,
                },
            )
        )
    print(f"[汽车大师] 生成 {len(documents)} 条文档")
    return documents


# 批量写入向量数据库（使用余弦相似度，逐批输出进度）
def build_vector_db(documents):
    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=PERSIST_DIRECTORY,
        embedding_function=LoadEmbeddingModel.load_embedding_model(),
        collection_metadata={"hnsw:space": "cosine"},
    )

    total = len(documents)
    for i in range(0, total, BATCH_SIZE):
        batch = documents[i : i + BATCH_SIZE]
        vector_store.add_documents(batch)
        done = min(i + BATCH_SIZE, total)
        print(f"[向量库] 已写入 {done}/{total} 条文档")

    return vector_store


if __name__ == "__main__":
    start = time.time()

    documents = load_autohome_documents() + load_automaster_documents()
    print(f"[向量库] 共 {len(documents)} 条文档，开始构建...")

    build_vector_db(documents)

    cost = time.time() - start
    print(f"向量数据库构建成功，共 {len(documents)} 条文档，耗时 {cost:.1f} 秒")
