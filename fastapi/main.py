from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn as uv

from ai import LoadChroma, LoadRerankerModel, LoadLLM, LoadOllama
from chat.controller.ChatController import chat_router
from chat.controller.HistoryController import history_router
from chat.utils import BM25Util
from users.controller.UsersController import users_router

# 生命周期配置
@asynccontextmanager
async def start_end_run(app):
    # 在应用启动时执行模型加载，避免在每次请求时都加载模型，提高响应速度
    # 加载意图识别模型对象
    app.state.ollama = LoadOllama.load_ollama()
    # 加载大模型对象
    app.state.llm = LoadLLM.load_llm()
    # 加载向量数据库对象
    app.state.vector = LoadChroma.load_Chroma_conn()
    # 加载BM25索引和文档
    app.state.bm25, app.state.docs = BM25Util.build_bm25_index(app.state.vector)
    # 加载重排序模型
    app.state.reranker = LoadRerankerModel.load_reranker_model()
    # 应用启动时执行
    print("项目启动")
    yield
    # 应用关闭时执行
    print("项目关闭")

app = FastAPI(lifespan=start_end_run)

# 注册users路由
app.include_router(
    router=users_router, # 需要注册的路由
    prefix="/users", # 路由前缀
    tags=["users"] # swagger 路由标签
   )

# 注册chat路由
app.include_router(
    router=chat_router, # 需要注册的路由
    prefix="/chat", # 路由前缀
    tags=["chat"] # swagger 路由标签
   )

# 注册history路由
app.include_router(
    router=history_router, # 需要注册的路由
    prefix="/history", # 路由前缀
    tags=["history"] # swagger 路由标签
   )



# 跨域配置
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 启动服务
if __name__ == '__main__':
    uv.run(
        app,
        host="localhost",
        port=8000,
        reload=False
    )