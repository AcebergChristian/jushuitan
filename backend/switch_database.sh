#!/bin/bash

# 数据库切换脚本

echo "================================"
echo "数据库切换工具"
echo "================================"
echo ""
echo "请选择数据库类型:"
echo "1) SQLite (本地开发)"
echo "2) MySQL (生产环境)"
echo ""
read -p "请输入选项 (1 或 2): " choice

case $choice in
    1)
        echo ""
        echo "切换到 SQLite..."
        export DATABASE_URL='sqlite:///database.db'
        echo "DATABASE_URL=sqlite:///database.db" > backend/.env
        echo "✓ 已切换到 SQLite"
        echo "  数据库文件: backend/database.db"
        ;;
    2)
        echo ""
        echo "切换到 MySQL..."
        export DATABASE_URL='mysql://pdd:PzNPetJFEwWkdzGD@t21.nulls.cn:3306/pdd'
        echo "DATABASE_URL=mysql://pdd:PzNPetJFEwWkdzGD@t21.nulls.cn:3306/pdd" > backend/.env
        echo "✓ 已切换到 MySQL"
        echo "  主机: t21.nulls.cn:3306"
        echo "  数据库: pdd"
        ;;
    *)
        echo "无效选项"
        exit 1
        ;;
esac

echo ""
echo "环境变量已设置，请重启应用程序"
echo ""
