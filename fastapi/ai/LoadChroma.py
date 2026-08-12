import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from ai import LoadEmbeddingModel

load_dotenv()


# 加载向量数据库
def load_Chroma_conn():
    return Chroma(
        collection_name=os.getenv("COLLECTION_NAME"),
        persist_directory=os.getenv("CHROMA_PATH"),
        embedding_function=LoadEmbeddingModel.load_embedding_model()
    )
