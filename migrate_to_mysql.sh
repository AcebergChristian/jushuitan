#!/bin/bash

# SQLite 到 MySQL 迁移快速启动脚本

echo "========================================"
echo "SQLite → MySQL 数据迁移"
echo "========================================"
echo ""

# 检查 Python
if ! command -v python &> /dev/null; then
    echo "错误: 未找到 Python"
    exit 1
fi

# 检查依赖
echo "1. 检查依赖..."
if ! python -c "import pymysql" 2>/dev/null; then
    echo "   安装 pymysql..."
    pip install pymysql
fi
echo "   ✓ 依赖检查完成"
echo ""

# 运行迁移
echo "2. 开始数据迁移..."
python backend/migrate_to_mysql.py

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "迁移成功！"
    echo "========================================"
    echo ""
    echo "下一步："
    echo "1. 设置环境变量："
    echo "   export DATABASE_URL='mysql://pdd:PzNPetJFEwWkdzGD@t21.nulls.cn:3306/pdd'"
    echo ""
    echo "2. 或创建 .env 文件："
    echo "   cd backend && cp .env.example .env"
    echo ""
    echo "3. 验证迁移："
    echo "   python backend/verify_mysql.py"
    echo ""
    echo "4. 启动应用："
    echo "   python backend/run.py"
    echo ""
else
    echo ""
    echo "迁移失败，请查看错误信息"
    exit 1
fi
