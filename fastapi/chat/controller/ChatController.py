from fastapi import APIRouter, Depends, Request
import json

from chat.entity.ConversationEntity import ConversationEntity
from chat.service import ChatService
from starlette.responses import StreamingResponse

from chat.utils import IntentionUtil
from utils.RolePermission import get_current_user

# 注册chat路由
chat_router = APIRouter()

# 聊天接口
@chat_router.get(
    path="/chat",
    summary="聊天接口",
    description="""
        与模型进行聊天
        访问路径：http://localhost:8000/chat/chat
        请求参数：
            question：用户的问题
            historyId：历史记录id，用于继续对话
        返回值：
            流式输出 SSE
    """
)
# 使用流式输出需要返回一个可迭代对象
# 需要使用JWT，控制用户权限
def chat(
    request: Request,
    question: str,
    historyId: int, # 历史记录id
    current_user: dict = Depends(get_current_user),
):
    # 检查用户是否存在
    if current_user is None:
        return {
            "code": 400,
            "msg": "用户不存在,请先登录",
            "data": None,
        }
    userId = current_user["user_id"]
    # 调用ollama模型
    ollama = request.app.state.ollama
    # 调用大模型对象
    llm = request.app.state.llm
    # 调用向量数据库对象
    vector = request.app.state.vector
    # 调用BM25索引对象
    bm25 = request.app.state.bm25
    # 调用文档对象
    docs = request.app.state.docs
    # 调用重排序模型对象
    reranker = request.app.state.reranker


    def generate():
        for raw_chunk in ChatService.chat(
                question, userId, historyId,
                request=request, llm=llm, vector=vector, bm25=bm25, docs=docs, reranker=reranker
        ):
            # 空行归一化交给前端在完整文本上处理，这里直接透传原始 chunk
            yield f"data: {json.dumps({'content': raw_chunk})}\n\n"

        yield f"data: {json.dumps({'content': '[DONE]'})}\n\n"
    return StreamingResponse(
        content=generate(),
        media_type="text/event-stream",
    )

# 保存聊天记录
# 需要使用JWT，控制用户权限
@chat_router.post(
    path="/saveConversation",
    summary="保存聊天记录",
    description="""
        保存聊天记录
        访问路径：http://localhost:8000/chat/saveConversation
        请求参数：
            question：用户的问题
            historyId：历史记录id
        返回值：
            保存结果
    """
)
def save_conversation(
    conversationEntity: ConversationEntity,
    current_user: dict = Depends(get_current_user),
):
    # 检查用户是否存在
    if current_user is None:
        return {
            "code": 400,
            "msg": "用户不存在,请先登录",
            "data": None,
        }
    # 保存聊天记录
    userId = current_user["user_id"]
    conversationEntity.userId = userId
    return ChatService.save_conversation(conversationEntity)