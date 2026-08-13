from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn as uv

from chat.controller.ChatController import chat_router
from chat.controller.HistoryController import history_router
from users.controller.UsersController import users_router

# 生命周期配置
@asynccontextmanager
async def start_end_run(app):
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