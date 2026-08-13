from fastapi import APIRouter, Depends

from chat.service import ChatService, HistoryService
from utils.RolePermission import get_current_user

# 注册history路由
history_router = APIRouter()



# 获取详细的历史记录
@history_router.get(
    path="/conversationLog",
    summary="获取详细的历史记录",
    description="""
        获取详细的历史记录
        访问路径：http://localhost:8000/history/conversationLog
        请求参数：
            historyId：历史记录id
        返回值：
            详细的历史记录
    """
)
def conversation_log(
    historyId: int,
    current_user: dict = Depends(get_current_user),
):
    if current_user is None:
        return {
            "code": 400,
            "msg": "用户不存在,请先登录",
            "data": None,
        }
    return HistoryService.conversation_log(historyId)


# 获取历史记录列表
@history_router.get(
    path="/queryHistoryMenu",
    summary="获取历史记录列表",
    description="""
        获取历史记录列表
        访问路径：http://localhost:8000/history/queryHistoryMenu
        """
)
def query_history_menu(
        userId: int,
        current_user: dict = Depends(get_current_user)
):
    if current_user is None:
        return {
            "code": 400,
            "msg": "用户不存在,请先登录",
            "data": None,
        }
    return HistoryService.query_history_menu(userId)


# 删除指定的历史记录
@history_router.delete(
    path="/deleteConversation",
    summary="删除指定的历史记录",
    description="""
        删除指定的历史记录
        访问路径：http://localhost:8000/history/deleteConversation
        请求参数：
            historyId：历史记录id
        返回值：
            删除结果
    """
)
def delete_conversation(
    historyId: int,
    current_user: dict = Depends(get_current_user)
):
    if current_user is None:
        return {
            "code": 400,
            "msg": "用户不存在,请先登录",
            "data": None,
        }
    return HistoryService.delete_conversation(historyId)


# 搜索父级历史记录
@history_router.get(
    path="/searchParentHistory",
    summary="搜索父级历史记录",
    description="""
        搜索父级历史记录
        访问路径：http://localhost:8000/history/searchParentHistory
        请求参数：
            historyId：历史记录id
        返回值：
            父级历史记录
    """
)
def search_parent_history(
    userId: int,
    question: str,
    current_user: dict = Depends(get_current_user)
):
    if current_user is None:
        return {
            "code": 400,
            "msg": "用户不存在,请先登录",
            "data": None,
        }
    userId = current_user["user_id"]
    return HistoryService.search_parent_history(userId, question)
