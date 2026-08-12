import secrets

# 生成32位密钥
key = secrets.token_urlsafe(32)
print(key)
