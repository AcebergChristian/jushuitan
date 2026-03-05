@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo Clean Install - PDD Crawler
echo ========================================
echo.

:: Delete old venv
if exist "venv" (
    echo [INFO] Removing old virtual environment...
    rmdir /s /q venv
    echo [OK] Old venv removed
)
echo.

:: Create new venv
echo [1/4] Creating new virtual environment...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create venv
    pause
    exit /b 1
)
echo [OK] Venv created
echo.

:: Activate venv
echo [2/4] Activating venv...
call venv\Scripts\activate.bat
echo [OK] Venv activated
echo.

:: Upgrade core tools
echo [3/4] Upgrading core tools...
python -m pip install --upgrade pip
pip install --upgrade setuptools==69.0.0 wheel
echo [OK] Core tools ready
echo.

:: Install dependencies one by one
echo [4/5] Installing dependencies...
pip install packaging
pip install blinker==1.7.0
pip install kaitaistruct
pip install pyOpenSSL
pip install selenium==4.15.0
pip install selenium-wire==5.1.0
pip install peewee
pip install pymysql
pip install python-dotenv
pip install webdriver-manager
pip install requests
echo [OK] All dependencies installed
echo.

:: Download ChromeDriver
echo [5/5] Setting up ChromeDriver...
if exist "chromedriver.exe" (
    echo [INFO] chromedriver.exe already exists
    echo [OK] ChromeDriver ready
) else (
    echo [INFO] Downloading ChromeDriver...
    python download_chromedriver.py
    if exist "chromedriver.exe" (
        echo [OK] ChromeDriver downloaded
    ) else (
        echo [WARNING] ChromeDriver download failed
        echo [INFO] Will try to use system ChromeDriver or auto-download at runtime
    )
)
echo.

:: Test import
echo ========================================
echo [TEST] Testing selenium-wire import...
echo ========================================
python -c "from seleniumwire import webdriver; print('[OK] selenium-wire works!')"
if errorlevel 1 (
    echo [ERROR] selenium-wire import failed
    pause
    exit /b 1
)
echo.

:: Run script
echo ========================================
echo [START] Running PDD Crawler
echo ========================================
echo.
python pdd_clawer.py

echo.
echo ========================================
echo [DONE] Completed
echo ========================================
pause
