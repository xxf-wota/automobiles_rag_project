# redis数据库工具类
import os
from dotenv import load_dotenv
import redis

load_dotenv()

# 连接redis数据库
def get_redis_conn():
    return redis.Redis(
        host=os.getenv('REDIS_HOST'), # redis数据库主机
        port=int(os.getenv('REDIS_PORT')), # redis数据库端口
        db=int(os.getenv('REDIS_DB')), # redis数据库数据库索引，默认0
        # 将redis数据库返回的字符串转换为utf-8编码
        decode_responses=True
    )


# 关闭redis连接
def close_redis_conn(conn):
    conn.close()

# 存入token到redis中
def set_token(user_id, token, expire=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")) * 60):
    conn = get_redis_conn()
    conn.setex(user_id, expire, token)
    close_redis_conn(conn)
    return True


# 验证token是否过期
def verify_token(user_id):
    conn = get_redis_conn()
    token = conn.get(user_id)
    close_redis_conn(conn)
    return token is not None
