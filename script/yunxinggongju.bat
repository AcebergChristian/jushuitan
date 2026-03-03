@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo PDD数据采集工具 - 运行脚本
echo ========================================
echo.

:: 检查 Python 环境
echo [1/4] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Python，请先安装 Python 3.8+
    echo.
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo ✅ Python 环境正常
echo.

:: 检查虚拟环境
echo [2/4] 检查虚拟环境...
if not exist "venv" (
    echo 🔧 创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo ✅ 虚拟环境创建成功
) else (
    echo ✅ 虚拟环境已存在
)
echo.

:: 激活虚拟环境
echo [3/4] 激活虚拟环境...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ 激活虚拟环境失败
    pause
    exit /b 1
)
echo ✅ 虚拟环境已激活
echo.

:: 安装依赖
echo [4/4] 检查并安装依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)
echo ✅ 依赖安装完成
echo.

:: 运行脚本
echo ========================================
echo 🚀 启动 PDD 数据采集工具
echo ========================================
echo.
python pdd_clawer.py

:: 保持窗口打开
echo.
echo ========================================
echo 程序执行完成
echo ========================================
pause
