from fastapi import APIRouter, Depends, Query, Request
from typing import Optional

from users.entity.UsersEntity import UsersEntity, UsersRoleEntity, UsersBanEntity
from users.service import UsersService
from utils.RolePermission import require_admin

users_router = APIRouter()

'''
    在注册和登录接口中，登录接口要进行JWT认证
    将登录成功后的JWT token返回给客户端
    即check_code接口和email_password接口都要生成JWT token并返回给客户端
'''








"""
    用于登录的接口
"""

# 发送邮箱验证码接口
@users_router.get(
    # 请求路径
    path="/sendEmail",
    # 接口简短摘要，显示在 Swagger UI 的接口列表中
    summary="发送邮件",
    # 接口详细描述，显示在 Swagger UI 的接口详情中
    description="""
        给用户输入的邮箱号发送验证码
        访问路径：http://localhost:8000/users/sendEmail
        请求参数：
            email：字符串类型，用户输入的邮箱号
        返回值：
            {
                "code": 状态码，成功200、失败400，int
                "msg": 提示信息，字符串
                "data": None，数据内容，Object
            }
    """,
)
def send_email(email: str):
    return UsersService.send_email(email)


# 验证邮箱验证码接口
@users_router.get(
    path="/checkCode",
    summary="验证验证码",
    description="""
        验证用户输入的邮箱号和验证码是否正确
        访问路径：http://localhost:8000/users/checkCode
        请求参数：
            email：字符串类型，用户输入的邮箱号
            code：字符串类型，用户输入的验证码
        返回值：
            {
                "code": 状态码，成功200、失败400，int
                "msg": 提示信息，字符串
                "data": None，数据内容，Object
            }
    """,
)
def check_code(email: str, code: str):
    return UsersService.check_code(email, code)




# 使用密码登录接口
@users_router.get(
    path="/emailPassword",
    summary="使用密码登录",
    description="""
        使用密码登录用户，需要输入邮箱号、密码，系统验证邮箱号和密码是否正确，
        若正确则登录成功，若错误则登录失败
        访问路径：http://localhost:8000/users/emailPassword
        请求参数：
            email：字符串类型，用户输入的邮箱号
            password：字符串类型，用户输入的密码
        返回值：
            {
                "code": 状态码，成功200、失败400，int
                "msg": 提示信息，字符串
                "data": None，数据内容，Object
            }
    """,
)
def email_password(email: str, password: str):
    return UsersService.email_password(email, password)


# 忘记密码接口
@users_router.get(
    path="/forgetPassword",
    summary="忘记密码",
    description="""
        忘记密码，需要输入邮箱号，系统验证邮箱号是否存在，
        若存在则返回重置密码的链接，若不存在则返回错误信息
        访问路径：http://localhost:8000/users/forgetPassword
        请求参数：
            email：字符串类型，用户输入的邮箱号
        返回值：
            {
                "code": 状态码，成功200、失败400，int
                "msg": 提示信息，字符串
                "data": None，数据内容，Object
            }
    """,
)
def forget_password(email: str, password: str, code: str):
    return UsersService.forget_password(email, password, code)



"""
    用于注册的接口
"""

@users_router.post(
    path="/register",
    summary="注册用户",
    description="""
        注册用户，需要输入邮箱号、密码、用户名、发送验证码，系统验证验证码是否正确，
        若正确则注册成功，并存入数据库
        访问路径：http://localhost:8000/users/register
        请求参数：
            email：字符串类型，用户输入的邮箱号
            password：字符串类型，用户输入的密码
            username：字符串类型，用户输入的用户名
            
        返回值：
            {
                "code": 状态码，成功200、失败400，int
                "msg": 提示信息，字符串
                "data": None，数据内容，Object
            }
    """,
)
def register(usersEntity: UsersEntity):
    return UsersService.register(usersEntity)


# 获取用户权限信息的接口
@users_router.get(
    path="/getUserRoleList",
    summary="获取用户权限信息",
    description="""
        获取用户权限信息，需要输入用户ID，系统验证用户ID是否存在，
        若存在则返回用户权限信息，若不存在则返回错误信息
        访问路径：http://localhost:8000/users/get
        请求参数：
            user_id：整数类型，用户ID
        返回值：
            {
                "code": 状态码，成功200、失败400，int
                "msg": 提示信息，字符串
                "data": None，数据内容，Object
            }
    """,
)
def get_user_role_list(
        current_user: dict = Depends(require_admin),
):
    # 是否是管理员用户
    if current_user is None:
        return {
            "code": 400,
            "msg": "用户不存在,请先登录",
            "data": None,
        }
    return UsersService.get_user_role_list()






"""
    修改用户权限接口 admin or user
"""
@users_router.post(
    path="/changeRole",
    summary="修改用户权限",
    description="""
        修改用户权限，需要输入用户ID、角色，系统验证用户ID是否存在，
        若存在则修改成功，若不存在则修改失败
        访问路径：http://localhost:8000/users/changeRole
        请求参数：
            user_id：整数类型，用户ID
            role：字符串类型，用户角色
        返回值：
            {
                "code": 状态码，成功200、失败400，int
                "msg": 提示信息，字符串
                "data": None，数据内容，Object
            }
    """,
)
def change_role(
        usersRoleEntity: UsersRoleEntity,
        current_user: dict = Depends(require_admin),
):
    if current_user is None:
        return {
            "code": 400,
            "msg": "用户不存在,请先登录",
            "data": None,
        }
    return UsersService.change_role(usersRoleEntity)





# 获取用户封禁状态接口
@users_router.get(
    path="/getUserBanStatus",
    summary="获取用户封禁状态",
    description="""
        获取用户封禁状态，需要输入用户ID，系统验证用户ID是否存在，
        若存在则返回用户封禁状态，若不存在则返回错误信息
        访问路径：http://localhost:8000/users/getUserBanStatus
        请求参数：
            user_id：整数类型，用户ID
        返回值：
            {
                "code": 状态码，成功200、失败400，int
                "msg": 提示信息，字符串
                "data": None，数据内容，Object
            }
    """,
)
def get_user_ban_status(
        current_user: dict = Depends(require_admin),
):
    if current_user is None:
        return {
            "code": 400,
            "msg": "用户不存在,请先登录",
            "data": None,
        }
    return UsersService.get_user_ban_status()








"""
    对用户进行封禁接口
"""
@users_router.post(
    path="/banUser",
    summary="封禁用户",
    description="""
        封禁用户，需要输入用户ID，系统验证用户ID是否存在，
        若存在则封禁成功，若不存在则封禁失败
        访问路径：http://localhost:8000/users/banUser
        请求参数：
            user_id：整数类型，用户ID
        返回值：
            {
                "code": 状态码，成功200、失败400，int
                "msg": 提示信息，字符串
                "data": None，数据内容，Object
            }
    """,
)
def ban_user(
        usersBanEntity: UsersBanEntity,
        current_user: dict = Depends(require_admin),
):
    if current_user is None:
        return {
            "code": 400,
            "msg": "用户不存在,请先登录",
            "data": None,
        }
    return UsersService.ban_user(usersBanEntity)


# 自动解封用户接口
@users_router.get(
    path="/autoChangeStatus",
    summary="自动解封用户",
    description="""
        自动解封用户，需要输入用户ID，系统验证用户ID是否存在，
        若存在则自动解封成功，若不存在则自动解封失败
        访问路径：http://localhost:8000/users/autoChangeStatus
        请求参数：
            user_id：整数类型，用户ID
        返回值：
            {
                "code": 状态码，成功200、失败400，int
                "msg": 提示信息，字符串
                "data": None，数据内容，Object
            }
    """,
)
def auto_change_status(
        userId: Optional[int] = Query(None),
        current_user: dict = Depends(require_admin),
):
    if current_user is None:
        return {
            "code": 400,
            "msg": "用户不存在,请先登录",
            "data": None,
        }
    return UsersService.auto_change_status(userId)


# 退出登录接口
@users_router.get(
    path="/logout",
    summary="退出登录",
    description="""
        退出登录，删除Redis中的session，使session_id立即失效
        访问路径：http://localhost:8000/users/logout
    """,
)
def logout(request: Request):
    # 从请求头提取 session_id 并删除，无需依赖 get_current_user，
    # 因为已过期的会话删除也应是幂等操作
    auth_header = request.headers.get("Authorization")
    session_id = None
    if auth_header and auth_header.startswith("Bearer "):
        session_id = auth_header.split(" ")[1]
    if not session_id:
        return {
            "code": 400,
            "msg": "未提供认证凭证",
            "data": None,
        }
    return UsersService.logout(session_id)



