#!/usr/bin/env python3
"""测试环境变量加载"""

import os
from pathlib import Path

print("=" * 60)
print("测试环境变量加载")
print("=" * 60)

# 检查 .env 文件
env_path = Path("backend/.env")
print(f"\n.env 文件路径: {env_path}")
print(f".env 文件存在: {env_path.exists()}")

if env_path.exists():
    print(f"\n.env 文件内容:")
    with open(env_path) as f:
        print(f.read())

# 加载 .env
from dotenv import load_dotenv
load_dotenv(env_path)

# 检查环境变量
database_url = os.getenv('DATABASE_URL')
print(f"\nDATABASE_URL: {database_url}")

if database_url and database_url.startswith('mysql://'):
    print("\n✓ 配置正确，将使用 MySQL")
else:
    print("\n✗ 配置错误，将使用 SQLite")
    print("\n请确保 backend/.env 文件包含:")
    print("DATABASE_URL=mysql://pdd:PzNPetJFEwWkdzGD@t21.nulls.cn:3306/pdd")
