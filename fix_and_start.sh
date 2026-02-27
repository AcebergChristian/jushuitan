#!/bin/bash

echo "========================================"
echo "数据库问题一键解决方案"
echo "========================================"
echo ""
echo "检测到 SQLite 数据库损坏"
echo ""
echo "推荐方案: 直接使用 MySQL（更稳定、更适合生产环境）"
echo ""
echo "请选择:"
echo "1) 使用 MySQL（推荐 - 需要先解决连接问题）"
echo "2) 修复 SQLite 数据库"
echo "3) 删除 SQLite，创建新的空数据库"
echo "4) 退出"
echo ""
read -p "请输入选项 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "使用 MySQL..."
        echo ""
        echo "步骤 1: 测试 MySQL 连接"
        python3 backend/test_mysql_connection.py
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "步骤 2: 配置环境变量"
            export DATABASE_URL='mysql://pdd:PzNPetJFEwWkdzGD@t21.nulls.cn:3306/pdd'
            echo "DATABASE_URL=mysql://pdd:PzNPetJFEwWkdzGD@t21.nulls.cn:3306/pdd" > backend/.env
            
            echo ""
            echo "步骤 3: 启动应用"
            cd backend
            python3 run.py
        else
            echo ""
            echo "MySQL 连接失败！"
            echo "请先解决连接问题（查看 MYSQL_BLOCKED_SOLUTION.md）"
            echo ""
            echo "快速解决: 在宝塔面板执行 FLUSH HOSTS;"
        fi
        ;;
    
    2)
        echo ""
        echo "修复 SQLite 数据库..."
        python3 backend/quick_fix_db.py
        ;;
    
    3)
        echo ""
        echo "删除并重建 SQLite 数据库..."
        echo "警告: 这将删除所有数据！"
        read -p "确认继续? (yes/no): " confirm
        
        if [ "$confirm" = "yes" ]; then
            # 备份
            timestamp=$(date +%Y%m%d_%H%M%S)
            cp backend/database.db backend/database.db.backup_$timestamp
            echo "✓ 已备份到: backend/database.db.backup_$timestamp"
            
            # 删除
            rm -f backend/database.db
            rm -f backend/database.db-shm
            rm -f backend/database.db-wal
            echo "✓ 已删除损坏的数据库"
            
            # 启动（会自动创建新数据库）
            echo ""
            echo "启动应用（会自动创建新数据库）..."
            cd backend
            python3 run.py
        else
            echo "已取消"
        fi
        ;;
    
    4)
        echo "已退出"
        exit 0
        ;;
    
    *)
        echo "无效选项"
        exit 1
        ;;
esac
