from fastapi import Request, HTTPException, Depends
from utils.JWTUtil import decode_token
from users.dao import UsersDao

from utils import SessionUtil


# 从请求头中提取并验证JWT Token
# 这个函数会被 Depends 调用
# 返回值是一个字典，包含用户ID、邮箱、用户名、角色
# 这个函数已经包含了提取token和解码验证逻辑
# 如果token无效或已过期，会抛出HTTPException
def get_current_user(request: Request):
    """
    从请求头中提取并验证JWT Token
    这个函数会被 Depends 调用
    """
    # 1. 提取Authorization头
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=401,
            detail="未提供认证凭证"
        )

    # 2. 验证格式：Bearer <token>
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="认证格式错误，请使用 Bearer Token"
        )

    # 3. 提取Token
    session_id = auth_header.split(" ")[1]
    # 4. 提取并验证会话是否存在
    session_data = SessionUtil.get_session(session_id)
    if not session_data:
        raise HTTPException(
            status_code=401,
            detail="会话已过期，请重新登录"
        )

    # 5. 解码验证
    payload = decode_token(session_data["token"])
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Token无效或已过期"
        )

    # 刷新会话
    SessionUtil.refresh_session(session_id)

    # hgetall 返回的 user_id 是字符串，转回 int，保证与数据库类型一致
    user_id = int(session_data.get("user_id"))

    # 6. 从数据库重新查询用户最新的角色和封禁状态
    # token 中的 role/status 是登录时写入的快照，可能已经过期
    # 这里以数据库为准，保证角色变更、封禁能即时生效
    users_role = UsersDao.query_users_role(user_id)
    role = users_role[0]["role"] if users_role else session_data.get("role")

    user_status = UsersDao.get_user_ban_status_by_user_id(user_id)
    status = user_status[0]["status"] if user_status else False

    # 7. 封禁用户禁止访问
    if status:
        raise HTTPException(
            status_code=403,
            detail="账号已被封禁，请联系管理员"
        )

    # 8. 返回用户信息
    # role 使用上面刚从数据库查询到的最新值，保证角色变更即时生效
    return {
        "user_id": user_id,
        "email": session_data.get("email"),
        "username": session_data.get("username"),
        "role": role
    }


# 只返回user_id
# 执行这个函数前，会先执行get_current_user函数，获取当前用户信息
# 然后赋值给current_user参数
# 最后返回user_id
def get_current_user_id(current_user: dict = Depends(get_current_user)):
    """
    获取当前用户ID
    """
    return current_user.get("user_id")


# 只返回email
# 执行这个函数前，会先执行get_current_user函数，获取当前用户信息
# 然后赋值给current_user参数
# 最后返回email
def get_current_email(current_user: dict = Depends(get_current_user)):
    """
    获取当前用户邮箱
    """
    return current_user.get("email")



# 只允许admin角色访问
def require_admin(current_user: dict = Depends(get_current_user)):
    """
    验证用户角色为admin
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="您没有权限访问此资源"
        )
    return current_user
