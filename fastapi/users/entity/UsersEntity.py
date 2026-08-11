from pydantic import BaseModel, Field


# 用户实体类
"""
    需要存入数据库的用户信息
"""
class UsersEntity(BaseModel):
    email: str = Field(description="用户邮箱号")
    password: str = Field(description="用户密码")
    username: str = Field(description="用户用户名")
    # 由于验证码部分业务不需要使用，所以将验证码字段设为空默认值
    # 防止在插入数据库时，验证码字段为空导致插入失败
    code: str = Field(description="用户验证码", default="")
