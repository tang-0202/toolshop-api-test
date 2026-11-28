"""
TOOLSHOP 接口自动化测试 —— 配置

原则：这个文件里没有任何秘密，可以安全地提交到 GitHub。
秘密放在两个地方：
  本地 → 同目录下的 .env（已被 .gitignore 拦住）
  CI   → GitHub 仓库 Settings → Secrets
"""

import os

from dotenv import load_dotenv

# 本地跑的时候，把 .env 里的键值对读进环境变量。
# 在 CI 上这个文件不存在，load_dotenv() 什么也不做、也不报错。
# 注意：默认不覆盖已经存在的环境变量 —— 所以 CI 的 Secrets 优先。
load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://api.practicesoftwaretesting.com")

# 注意这里没有写死的密码，只有"从环境里取"这个动作
TEST_USER = {
    "email": os.getenv("TEST_EMAIL", ""),
    "password": os.getenv("TEST_PASSWORD", ""),
}