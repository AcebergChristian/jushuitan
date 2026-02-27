#!/bin/bash

echo "========================================"
echo "使用 MySQL 启动应用"
echo "========================================"
echo ""

# 设置环境变量
export DATABASE_URL='mysql://pdd:PzNPetJFEwWkdzGD@t21.nulls.cn:3306/pdd'

echo "数据库配置: MySQL"
echo "主机: t21.nulls.cn:3306"
echo "数据库: pdd"
echo ""

# 启动应用
cd backend
python3 run.py
