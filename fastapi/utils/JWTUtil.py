import os
import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))  # 30分钟

# 生成Token
def create_access_token(data: Dict[str, str]) -> str:
    """
    生成JWT Token
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "exp": expire, # 过期时间，防止token被永久使用
        "iat": datetime.now(timezone.utc), # 签发时间，可用于判断token新旧
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 解码Token并返回用户信息
def decode_token(token: str) -> Optional[Dict]:
    """
    解码JWT Token
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None