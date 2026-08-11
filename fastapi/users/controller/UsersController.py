from fastapi import APIRouter

from users.entity.UsersEntity import UsersEntity
from users.service import UsersService

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


