#!/bin/bash

echo "========================================"
echo "重新构建前端"
echo "========================================"
echo ""

cd web

echo "1. 安装依赖（如果需要）..."
if [ ! -d "node_modules" ]; then
    npm install
fi

echo ""
echo "2. 构建生产版本..."
npm run build

echo ""
echo "3. 复制到 backend/dist..."
rm -rf ../backend/dist
cp -r dist ../backend/dist

echo ""
echo "✓ 前端构建完成！"
echo ""
echo "现在可以启动后端："
echo "  cd backend"
echo "  python3 run.py"
