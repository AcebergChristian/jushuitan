@echo off
chcp 65001 >nul

echo ========================================
echo PDD Crawler - Quick Start
echo ========================================
echo.

:: Activate venv
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo [OK] Virtual environment activated
    echo.
) else (
    echo [ERROR] Virtual environment not found
    echo [INFO] Please run clean_install.bat first
    pause
    exit /b 1
)

:: Run script
echo ========================================
echo [START] Running PDD Crawler
echo ========================================
echo.
python pdd_clawer.py

:: Keep window open
echo.
echo ========================================
echo [DONE] Completed
echo ========================================
pause
