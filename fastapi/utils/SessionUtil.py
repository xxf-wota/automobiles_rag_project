import uuid
from common import RedisUtil
import os
from dotenv import load_dotenv
load_dotenv()

SESSTION_EXPIRE = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")) * 60

def create_session(user_id: str, token: str, role: str, email: str, username: str, status: bool) -> str:
    """创建session，返回session_id"""
    session_id = str(uuid.uuid4()) # 生成随机session_id
    conn = RedisUtil.get_redis_conn()
    session_data = {
        "token": token,
        "user_id": user_id,
        "role": role,
        "email": email,
        "username": username,
        # bool 会触发 redis-py 的 DataError，统一转成 int 存储
        "status": int(status),
    }
    # 注意：本机 Redis 为 3.0.x，HSET 一次只支持一个字段（多字段是 Redis 4.0 才支持），
    # 不能使用 hset(name, mapping=...) 的多字段写法，需逐字段写入
    for field, value in session_data.items():
        conn.hset(session_id, field, value)
    conn.expire(session_id, SESSTION_EXPIRE) # 设置过期时间
    RedisUtil.close_redis_conn(conn)
    return session_id

def get_session(session_id: str) -> dict | None:
    """根据session_id获取用户信息，不存在或过期返回None"""
    conn = RedisUtil.get_redis_conn()
    # session 通过 hset 存储为哈希结构，必须用 hgetall 读取
    # 若用 get 读取哈希键会始终返回 None，导致所有请求都提示“会话已过期”
    data = conn.hgetall(session_id)
    RedisUtil.close_redis_conn(conn)
    return data if data else None

def delete_session(session_id: str) -> None:
    """删除session（退出登录时调用"""
    conn = RedisUtil.get_redis_conn()
    conn.delete(session_id)
    RedisUtil.close_redis_conn(conn)

def refresh_session(session_id: str) -> None:
    """刷新session过期时间"""
    conn = RedisUtil.get_redis_conn()
    conn.expire(session_id, SESSTION_EXPIRE) # 刷新过期时间
    RedisUtil.close_redis_conn(conn)

