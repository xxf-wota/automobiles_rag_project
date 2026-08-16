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


# 用户角色实体类
"""
    需要存入数据库的用户角色信息
"""
class UsersRoleEntity(BaseModel):
    userId: int = Field(description="用户ID")
    role: str = Field(description="用户角色")


# 用户封禁实体类
"""
    需要存入数据库的用户封禁信息
"""
class UsersBanEntity(BaseModel):
    userId: int = Field(description="用户ID")
    status: bool = Field(description="是否封禁")
    ban_time: int = Field(description="封禁时间", default=0)
