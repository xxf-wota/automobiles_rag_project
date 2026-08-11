import os
import random
import smtplib

from email.mime.text import MIMEText

from dotenv import load_dotenv

from common import RedisUtil, MySQLUtil
from users.dao import UsersDao
from users.entity.UsersEntity import UsersEntity

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
            "data": None
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

    results = UsersDao.query_user_by_email(email)
    # 当查询结果为一个空元组时，说明邮箱号不存在
    if isinstance(results, tuple):
        return {
            "code": 400,
            "msg": "邮箱号不存在，请先注册",
            "data": None
        }
    if results[0]["password"] != password:
        return {
            "code": 400,
            "msg": "密码错误，请重新输入",
            "data": None
        }
    # 若邮箱号和密码都正确，返回成功信息
    # 发送提醒邮件到用户邮箱号
    # 配置发送信息
    sender = os.getenv("SENDER_EMAIL") # 发送邮箱号
    sender_pwd = os.getenv("SENDER_EMAIL_PASSWORD") # 授权码
    subject = "登录成功" # 邮件主题
    context = f"您已成功登录，欢迎来到我们的平台，若不是您操作，请及时冻结账号" # 邮件内容
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
        "msg": "登录成功，已发送提醒邮件到您的邮箱号",
        "data": None
    }




# 注册服务
"""
    该服务用于用户输入邮箱号、密码、用户名点击发送验证码并输入后，
    系统验证验证码是否正确，若正确则注册成功，并存入数据库
"""
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
        if result == "插入用户成功":
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
                "data": None
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




