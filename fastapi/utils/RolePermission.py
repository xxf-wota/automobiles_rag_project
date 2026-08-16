from fastapi import Request, HTTPException, Depends
from utils.JWTUtil import decode_token


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
    token = auth_header.split(" ")[1]

    # 4. 解码验证
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Token无效或已过期"
        )

    # 5. 返回用户信息
    return {
        "user_id": payload.get("user_id"),
        "email": payload.get("email"),
        "username": payload.get("username"),
        "role": payload.get("role")
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
