import json

from langchain_chroma import Chroma
import os
from dotenv import load_dotenv
import pandas as pd
from langchain_core.documents import Document

from ai import LoadEmbeddingModel

load_dotenv()



# 构建汽车数据
# 数据集路径
database_path = ["./懂车帝1.csv", "./汽车之家.csv"]
# 数据库存储路径
persist_directory = os.getenv("CHROMA_PATH")
# 数据集名称
collection_name = os.getenv("COLLECTION_NAME")

# 编码格式为gbk，否则会出现utf-8编码报错
# 使用for循环来读取两个文件
documents = []
for file_path in database_path:
    df = pd.read_csv(file_path, encoding="gbk") # 是一个DataFrame对象
    # 转list
    data_list = df.to_dict("records")
    # 列表里套字典，所以需要转为json字符串，并且使用ensure_ascii=False，否则会出现中文编码报错
    documents.extend([Document(page_content=json.dumps(doc, ensure_ascii=False), metadata={"source": file_path}) for doc in data_list])
# print(data_list) # list[{}, {}, ...]
# print(documents)





# 构建向量数据库
try:
    Chroma.from_documents(
        documents=documents, # 内部必须是list[Document]
        collection_name=collection_name,
        persist_directory=persist_directory,
        embedding=LoadEmbeddingModel.load_embedding_model(),
        # 使用余弦相似度计算
        collection_metadata={"hnsw:space": "cosine"}
    )
    print("向量数据库构建成功")
except Exception as e:
    print(f"构建向量数据库失败：{e}")
