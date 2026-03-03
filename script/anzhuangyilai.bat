@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo PDD数据采集工具 - 环境配置
echo ========================================
echo.

:: 检查 Python 环境
echo [1/3] 检查 Python 环境...
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

:: 创建虚拟环境
echo [2/3] 创建虚拟环境...
if exist "venv" (
    echo ⚠️ 虚拟环境已存在，是否重新创建？
    echo    按任意键重新创建，或关闭窗口取消
    pause >nul
    echo 🗑️  删除旧的虚拟环境...
    rmdir /s /q venv
)

python -m venv venv
if errorlevel 1 (
    echo ❌ 创建虚拟环境失败
    pause
    exit /b 1
)
echo ✅ 虚拟环境创建成功
echo.

:: 激活虚拟环境并安装依赖
echo [3/3] 安装依赖包...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)
echo ✅ 依赖安装完成
echo.

echo ========================================
echo ✅ 环境配置完成！
echo ========================================
echo.
echo 现在可以运行 "运行工具.bat" 启动程序
echo.
pause
