"""
认证模块：密码哈希、Session Token 管理
"""
import os
import base64
import hashlib
import hmac
from itsdangerous import URLSafeSerializer
from fastapi import Request

# 生产环境请用环境变量
ADMIN_USER = os.getenv("ADMIN_USER", "admin")

# ===== PBKDF2 password hashing (no bcrypt dependency) =====
# 格式: pbkdf2_sha256$iterations$salt$hash
def hash_password(password: str, iterations: int = 260_000) -> str:
    """生成 PBKDF2 密码哈希"""
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return "pbkdf2_sha256${}${}${}".format(
        iterations,
        base64.urlsafe_b64encode(salt).decode("utf-8").rstrip("="),
        base64.urlsafe_b64encode(dk).decode("utf-8").rstrip("="),
    )


def verify_password(password: str, stored: str) -> bool:
    """验证密码（支持 PBKDF2 哈希或明文比对）"""
    if not stored:
        return False
    
    # 如果是 PBKDF2 格式
    if stored.startswith("pbkdf2_sha256$"):
        try:
            parts = stored.split("$")
            if len(parts) != 4:
                return False
            algo, iters, salt_b64, dk_b64 = parts
            if algo != "pbkdf2_sha256":
                return False
            iterations = int(iters)
            # Base64 URL-safe 解码（补全 padding）
            def decode_b64(s):
                # 补全到 4 的倍数
                missing_padding = len(s) % 4
                if missing_padding:
                    s += "=" * (4 - missing_padding)
                return base64.urlsafe_b64decode(s)
            
            salt = decode_b64(salt_b64)
            dk_expected = decode_b64(dk_b64)
            dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
            return hmac.compare_digest(dk, dk_expected)
        except Exception as e:
            # 调试：打印错误（生产环境应移除）
            import logging
            logging.warning(f"Password verification error: {e}")
            return False
    
    # 兼容明文（仅开发环境，生产环境应移除）
    return password == stored


# 初始密码：admin123（生产环境请修改）
# 如果你想自己生成新的hash：临时运行 python 并 print(hash_password("你的密码"))
# 然后把输出粘贴到 ADMIN_PASS_HASH
# 
# 注意：如果登录失败，可以临时使用明文比对（见下方注释）
ADMIN_PASS_HASH = os.getenv(
    "ADMIN_PASS_HASH",
    # 默认使用明文 "admin123"（开发环境快速修复）
    # 生产环境请生成哈希：python -c "from app.auth import hash_password; print(hash_password('your_password'))"
    "admin123"  # 临时明文，方便开发
)

# Session 密钥（生产环境必须修改）
SECRET = os.getenv("SECRET_KEY", "CHANGE_ME_TO_A_RANDOM_SECRET_IN_PRODUCTION")
serializer = URLSafeSerializer(SECRET, salt="eiho-admin")


def create_session_token(username: str) -> str:
    """创建 session token"""
    return serializer.dumps({"u": username})


def read_session_token(token: str) -> dict:
    """读取并验证 session token"""
    return serializer.loads(token)


def is_logged_in(request: Request) -> bool:
    """检查用户是否已登录"""
    token = request.cookies.get("eiho_session")
    if not token:
        return False
    try:
        data = read_session_token(token)
        return data.get("u") == ADMIN_USER
    except Exception:
        return False
