import os
import random
import smtplib
from datetime import datetime

from email.mime.text import MIMEText

from dotenv import load_dotenv

from common import RedisUtil, MySQLUtil
from users.dao import UsersDao
from users.entity.UsersEntity import UsersEntity, UsersRoleEntity, UsersBanEntity
from utils.JWTUtil import create_access_token
from utils import SessionUtil

load_dotenv()

"""
    注册：
        用户需要输入邮箱号、密码、用户名、发送验证码，系统验证验证码是否正确，
        若正确则注册成功，并存入数据库
"""


"""
    登录：
        有两种登录方式：邮箱验证码登录和邮箱密码登录
        邮箱验证码登录：用户输入邮箱号和验证码，系统验证验证码是否正确
        邮箱密码登录：用户输入邮箱号和密码，系统验证密码是否正确
"""


# 发送邮箱验证码服务
"""
    发送邮箱验证码服务：
        若用户未注册，则用于注册时的验证码验证
        若用户已注册，则用于登录时的验证码验证
        用户输入邮箱号，系统生成6位随机验证码，发送到用户邮箱
        验证码过期时间为1分钟
"""

def send_email(email: str):
    # 生成验证码
    code = ""
    for i in range(6):
        # random.random() 生成0-1之间的随机数
        code += str(int(random.random() * 10))

    # 配置发送信息
    sender = os.getenv("SENDER_EMAIL") # 发送邮箱号
    sender_pwd = os.getenv("SENDER_EMAIL_PASSWORD") # 授权码
    subject = "验证码来了" # 邮件主题
    context = f"您的验证码是：{code}，请在1分钟内输入" # 邮件内容
    # 创建邮箱内容对象
    message = MIMEText(context, "plain", "utf-8")
    # 添加邮箱内容
    message["From"] = sender
    message["To"] = email
    message["Subject"] = subject
    print(message)
    try:
        # 构建发送邮箱对象
        smtp = smtplib.SMTP(
            host=os.getenv("SMTP_HOST"),
            port=int(os.getenv("SMTP_PORT")),
        )
        # 开启邮箱发送服务 TLS
        smtp.starttls()
        # 验证发送方和授权码是否正确
        smtp.login(sender, sender_pwd)
        # 发送邮件
        smtp.sendmail(sender, email, message.as_string())
        # 关闭邮箱连接
        smtp.quit()
        # 还需要将验证码存入redis数据库，等待用户输入
        # 验证码过期时间为1分钟
        # 连接redis数据库
        redis = RedisUtil.get_redis_conn()
        # 存储验证码到redis数据库
        redis.set(email, code, ex=60)
        # 关闭redis连接
        RedisUtil.close_redis_conn(redis)

        return {
            "code": 200,
            "msg": "发送成功",
            "data": None
        }
    except Exception as e:
        print(f"发送邮件失败：{e}")
        return {
            "code": 400,
            "msg": "邮箱发送失败",
            "data": None
        }

# 验证邮箱验证码服务
# 只能用在登录时验证验证码是否正确
# 注册时不能用此方法验证验证码
def check_code(email: str, code: str):
    try:
        # 从redis数据库中获取验证码
        # 连接redis数据库
        redis = RedisUtil.get_redis_conn()
        redis_code = redis.get(email)
        print(redis_code)
        # 关闭redis连接
        RedisUtil.close_redis_conn(redis)
        # 验证验证码是否正确
        if redis_code != code:
            return {
                "code": 400,
                "msg": "验证码错误，请重新输入验证码",
                "data": None
            }
        # 当验证码正确时，给用户邮箱发送提醒邮件并返回成功信息

        # 从数据库中查询用户信息
        # 此时数据库已经有数据了，直接用数据库中的数据，不依赖前端传递的用户信息
        # 只有后端拿到用户信息才能实时更新用户状态
        user_data = UsersDao.query_user_by_email(email)
        # 从数据库中查询用户角色
        users_role = UsersDao.query_users_role(user_data[0]["user_id"])
        role = users_role[0]["role"]
        # 从数据库中查询用户封禁状态
        user_status = UsersDao.get_user_ban_status_by_user_id(user_data[0]["user_id"])
        status = user_status[0]["status"]

        # 被封禁用户禁止登录
        if status:
            return {
                "code": 400,
                "msg": "账号已被封禁，请联系管理员",
                "data": None
            }

        # 生成JWT Token
        user_id = user_data[0]["user_id"]
        username = user_data[0]["username"]
        token = create_access_token({
            "user_id": user_id,
            "email": email,
            "username": username,
            "role": role,
            "status": status,
        })
        session_id = SessionUtil.create_session(user_id, token, role, email, username, status)

        # 配置发送信息
        sender = os.getenv("SENDER_EMAIL") # 发送邮箱号
        sender_pwd = os.getenv("SENDER_EMAIL_PASSWORD") # 授权码
        subject = "登录成功" # 邮件主题
        context = f"您已成功登录，欢迎来到我们的平台，若不是您操作，请及时冻结账号" # 邮件内容

        # 邮箱内容对象
        message = MIMEText(context, "plain", "utf-8")
        # 添加邮箱内容
        message["From"] = sender
        message["To"] = email
        message["Subject"] = subject
        print(message)
        # 构建发送邮箱对象
        smtp = smtplib.SMTP(
            host=os.getenv("SMTP_HOST"),
            port=int(os.getenv("SMTP_PORT")),
        )
        # 开启邮箱发送服务 TLS
        smtp.starttls()
        # 验证发送方和授权码是否正确
        smtp.login(sender, sender_pwd)
        # 发送邮件
        smtp.sendmail(sender, email, message.as_string())
        # 关闭邮箱连接
        smtp.quit()

        return {
            "code": 200,
            "msg": "登录成功，已发送提醒邮件到您的邮箱号",
            "data": {
                "session_id": session_id,
                "user_id": user_id,
                "email": email,
                "username": username,
                "role": role,
                "status": status
            }
        }

    except Exception as e:
        return {
            "code": 400,
            "msg": "验证码已失效，请重新发送验证码",
            "data": None
        }


# 使用密码登录服务
def email_password(email: str, password: str):
    # 要验证邮箱号和密码是否正确，需要从数据库中查询用户信息
    user_data = UsersDao.query_user_by_email(email)
    # 查询结果为空时，说明邮箱号不存在
    # 注意：DictCursor 返回的是 list，不是 tuple
    if not user_data:
        return {
            "code": 400,
            "msg": "邮箱号不存在，请先注册",
            "data": None
        }
    if user_data[0]["password"] != password:
        return {
            "code": 400,
            "msg": "密码错误，请重新输入",
            "data": None
        }
    # 若邮箱号和密码都正确，返回成功信息
    try:
        # 查询用户角色
        users_role = UsersDao.query_users_role(user_data[0]["user_id"])
        role = users_role[0]["role"]

        # 从数据库中查询用户信息
        # 此时数据库已经有数据了，直接用数据库中的数据，不依赖前端传递的用户信息
        # 只有后端拿到用户信息才能实时更新用户状态
        user_id = user_data[0]["user_id"]
        username = user_data[0]["username"]
        user_status = UsersDao.get_user_ban_status_by_user_id(user_id)
        status = user_status[0]["status"]

        # 被封禁用户禁止登录
        if status:
            return {
                "code": 400,
                "msg": "账号已被封禁，请联系管理员",
                "data": None
            }
        # 生成token
        token = create_access_token({
            "user_id": user_id,
            "email": email,
            "username": username,
            "role": role,
            "status": status
        })
        session_id = SessionUtil.create_session(user_id, token, role, email, username, status)

        # 发送提醒邮件到用户邮箱号
        # 配置发送信息
        sender = os.getenv("SENDER_EMAIL")  # 发送邮箱号
        sender_pwd = os.getenv("SENDER_EMAIL_PASSWORD")  # 授权码
        subject = "登录成功"  # 邮件主题
        context = f"您已成功登录，欢迎来到我们的平台，若不是您操作，请及时冻结账号"  # 邮件内容
        message = MIMEText(context, "plain", "utf-8")        # 添加邮箱内容
        message["From"] = sender
        message["To"] = email
        message["Subject"] = subject
        # 构建发送邮箱对象
        smtp = smtplib.SMTP(
            host=os.getenv("SMTP_HOST"),
            port=int(os.getenv("SMTP_PORT")),
        )
        # 开启邮箱发送服务 TLS
        smtp.starttls()
        # 验证发送方和授权码是否正确
        smtp.login(sender, sender_pwd)
        # 发送邮件
        smtp.sendmail(sender, email, message.as_string())
        # 关闭邮箱连接
        smtp.quit()
        # 返回成功信息
        return {
            "code": 200,
            "msg": "登录成功，已发送提醒邮件到您的邮箱号",
            "data": {
                "session_id": session_id,
                "user_id": user_id,
                "email": email,
                "username": username,
                "role": role,
                "status": status
            }
        }
    except Exception as e:
        return {
            "code": 400,
            "msg": "系统错误，登录请稍后重试",
            "data": None
        }

# 忘记密码服务
def forget_password(email: str, password: str, code: str):
    # 先判断邮箱号是否存在
    isEmail = UsersDao.query_user_by_email(email)
    if not isEmail:
        return {
            "code": 400,
            "msg": "邮箱号不存在，请先注册",
            "data": None
        }
    # 新密码和原密码不能相同
    if password == isEmail[0]["password"]:
        return {
            "code": 400,
            "msg": "新密码不能与原密码相同",
            "data": None
        }
    try:
        # 然后验证验证码是否正确
        # 连接redis数据库
        redis = RedisUtil.get_redis_conn()
        redis_code = redis.get(email)
        # 关闭redis连接
        RedisUtil.close_redis_conn(redis)
        # 验证验证码是否正确
        if redis_code != code:
            return {
                "code": 400,
                "msg": "验证码错误，请重新输入验证码",
                "data": None
            }

        # 邮箱号存在了，发送重置密码邮件
        result = UsersDao.change_password(email, password)
        # 返回结果为 True or False
        if result:
            # 配置发送信息
            sender = os.getenv("SENDER_EMAIL") # 发送邮箱号
            sender_pwd = os.getenv("SENDER_EMAIL_PASSWORD") # 授权码
            subject = "重置密码成功" # 邮件主题
            context = f"您已成功重置密码，若不是您操作，请及时冻结账号" # 邮件内容
            # 创建邮箱内容对象
            message = MIMEText(context, "plain", "utf-8")
            # 添加邮箱内容
            message["From"] = sender
            message["To"] = email
            message["Subject"] = subject
            # 构建发送邮箱对象
            smtp = smtplib.SMTP(
                host=os.getenv("SMTP_HOST"),
                port=int(os.getenv("SMTP_PORT")),
            )
            # 开启邮箱发送服务 TLS
            smtp.starttls()
            # 验证发送方和授权码是否正确
            smtp.login(sender, sender_pwd)
            # 发送邮件
            smtp.sendmail(sender, email, message.as_string())
            # 关闭邮箱连接
            smtp.quit()
            # 返回成功信息
            return {
                "code": 200,
                "msg": "重置密码成功，已发送提醒邮件到您的邮箱号",
                "data": None
            }
        return {
            "code": 400,
            "msg": "重置密码失败",
            "data": None
        }
    except Exception as e:
        print(f"重置密码失败：{e}")
        return {
            "code": 400,
            "msg": f"系统错误，重置密码请稍后重试",
            "data": None
        }

# 注册服务
def register(usersEntity: UsersEntity):
    try:
        # 验证验证码是否正确
        # 连接redis数据库
        redis = RedisUtil.get_redis_conn()
        redis_code = redis.get(usersEntity.email)
        # 关闭redis连接
        RedisUtil.close_redis_conn(redis)
        # 验证验证码是否正确
        if redis_code != usersEntity.code:
            return {
                "code": 400,
                "msg": "验证码错误，请重新输入验证码",
                "data": None
            }
        # 若验证码正确调用插入数据库方法
        result = UsersDao.insert_user(usersEntity)
        # 插入用户状态表
        user_id = UsersDao.query_user_by_email(usersEntity.email)[0]["user_id"]
        ban_result = UsersDao.insert_users_status(user_id, usersEntity.username)

        if result == "插入用户成功" and ban_result:
            # 查询新用户信息
            user_data = UsersDao.query_user_by_email(usersEntity.email)
            user_id = user_data[0]["user_id"]
            # 插入users_role表
            users_role = UsersDao.insert_users_role(user_id, usersEntity.username)
            if not users_role:
                return {
                    "code": 400,
                    "msg": "插入用户角色失败",
                    "data": None
                }
            # 生成JWT Token
            token = create_access_token({
                "user_id": user_id,
                "email": usersEntity.email,
                "username": usersEntity.username,
                "role": "user",
                "status": False  # 表示账号正常状态
            })
            session_id = SessionUtil.create_session(user_id, token, "user", usersEntity.email, usersEntity.username, False)


            # 注册成功后，给用户邮箱发送提醒邮件
            # 配置发送信息
            sender = os.getenv("SENDER_EMAIL")  # 发送邮箱号
            sender_pwd = os.getenv("SENDER_EMAIL_PASSWORD")  # 授权码
            subject = "注册成功"  # 邮件主题
            context = f"{usersEntity.username}已成功注册，欢迎来到我们的平台"  # 邮件内容
            message = MIMEText(context, "plain", "utf-8")
            # 添加邮箱内容
            message["From"] = sender
            message["To"] = usersEntity.email
            message["Subject"] = subject
            # 创建发送邮箱对象
            smtp = smtplib.SMTP(
                host=os.getenv("SMTP_HOST"),
                port=int(os.getenv("SMTP_PORT")),
            )
            # 开启邮箱发送服务 TLS
            smtp.starttls()
            # 验证发送方和授权码是否正确
            smtp.login(sender, sender_pwd)
            # 发送邮件
            smtp.sendmail(sender, usersEntity.email, message.as_string())
            # 关闭邮箱连接
            smtp.quit()
            return {
                "code": 200,
                "msg": "注册成功，已发送提醒邮件到您的邮箱号",
                "data": {
                    "session_id": session_id,
                    "user_id": user_id,
                    "email": usersEntity.email,
                    "username": usersEntity.username,
                    "role": "user",
                    "status": False  # 表示账号正常状态
                }
            }

        return {
            "code": 400,
            "msg": result,
            "data": None
        }

    except Exception as e:
        print(f"注册失败：{e}")
        return {
            "code": 400,
            "msg": "验证码已失效，请重新发送验证码",
            "data": None
        }

# 修改用户角色服务
def change_role(usersRoleEntity: UsersRoleEntity):
    # 从usersRoleEntity中提取数据
    userId = usersRoleEntity.userId
    role = usersRoleEntity.role
    # 调用数据库方法修改用户角色
    result = UsersDao.change_role(userId, role)
    if result:
        # 角色已在数据库中修改，get_current_user 会实时读取最新角色，无需更新JWT Token
        return {
            "code": 200,
            "msg": "修改用户角色成功",
            "data": None
        }
    else:
        return {
            "code": 400,
            "msg": result,
            "data": None
        }

# 获取用户角色服务
def get_user_role_list():
    # 调用数据库方法查询用户角色
    result = UsersDao.get_user_role_list()
    if result:
        # 包装成前端需要的格式
        data_list = []
        for item in result:
            data_list.append({
                'user_id': item['user_id'],
                'username': item['username'],
                'role': item['role'],
                'create_time': item['create_time'].strftime("%Y-%m-%d %H:%M:%S"),
            })
        return {
            "code": 200,
            "msg": "用户权限表查询成功",
            "data": data_list
        }
    else:
        return {
            "code": 400,
            "msg": "用户权限表查询失败",
            "data": None
        }



# 获取用户封禁状态服务
def get_user_ban_status():
    # 调用数据库方法查询用户封禁状态
    result = UsersDao.get_user_ban_status()
    if result:
        # 包装成前端需要的格式
        data_list = []
        for item in result:
            data_list.append({
                "user_id": item['user_id'],
                "username": item['username'],
                "status": item['status'],
                # 若用户为被封禁则banned_time和normal_time都为创建时间
                "banned_time": item['banned_time'].strftime("%Y-%m-%d %H:%M:%S"),
                "normal_time": item['normal_time'].strftime("%Y-%m-%d %H:%M:%S"),
            })
        return {
            "code": 200,
            "msg": "用户封禁状态查询成功",
            "data": data_list
        }
    else:
        return {
            "code": 400,
            "msg": "用户封禁状态查询失败",
            "data": None
        }






# 用户封禁服务
def ban_user(usersBanEntity: UsersBanEntity):
    # 从usersBanEntity中提取数据
    userId = usersBanEntity.userId
    status = usersBanEntity.status
    # 调用数据库方法修改用户封禁状态
    result = UsersDao.ban_user(userId, status, usersBanEntity.ban_time)

    if result:
        return {
            "code": 200,
            "msg": "修改用户封禁状态成功",
            "data": None
        }
    else:
        return {
            "code": 400,
            "msg": result,
            "data": None
        }


# 自动解封用户服务
def auto_change_status(userId: int):
    ban_status = UsersDao.get_user_ban_status_by_user_id(userId)[0]
    try:
        # 如果当前时间大于等于用户封禁状态中的封禁时间，则自动解封用户
        if datetime.now() >= ban_status["normal_time"] and ban_status["status"]:
            result = UsersDao.auto_change_status(userId, False)
            if result:
                return {
                    "code": 200,
                    "msg": "自动修改用户封禁状态成功",
                    "data": None
                }

            else:
                return {
                    "code": 400,
                    "msg": result,
                    "data": None
                }

        # 用户未到解封时间（或已无需解封），直接返回成功，避免返回 null 导致前端报错
        return {
            "code": 200,
            "msg": "用户未到解封时间，无需解封",
            "data": None
        }
    except Exception as e:
        print(f"自动解封用户失败：{e}")
        return {
            "code": 400,
            "msg": "自动解封用户失败",
            "data": None
        }


# 退出登录服务
def logout(session_id: str):
    """删除session，使session_id立即失效"""
    try:
        SessionUtil.delete_session(session_id)
        return {
            "code": 200,
            "msg": "退出登录成功",
            "data": None
        }
    except Exception as e:
        print(f"退出登录失败：{e}")
        return {
            "code": 400,
            "msg": "退出登录失败",
            "data": None
        }