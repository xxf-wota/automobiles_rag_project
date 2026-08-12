# 加载大模型
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()


def load_llm():
    return ChatOpenAI(
        model=os.getenv("LLM_MODEL_NAME"),
        api_key=os.getenv("DASHSCOPE_API_KEY"), # 从环境变量中获取DashScope API密钥
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        streaming=True,
    )
