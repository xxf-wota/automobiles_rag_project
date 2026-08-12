# 加载重排序模型

from FlagEmbedding import FlagReranker
import os
from dotenv import load_dotenv
load_dotenv()

def load_reranker_model():
    return FlagReranker(
        model_name_or_path=os.getenv("RERANKER_MODEL_PATH"),
        use_fp16=True,
    )







