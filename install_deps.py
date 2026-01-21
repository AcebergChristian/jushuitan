#!/usr/bin/env python
"""
安装正确的依赖库以解决jose库冲突问题
"""
import subprocess
import sys

def install_dependencies():
    """安装项目依赖"""
    deps_to_uninstall = ['jose', 'jose-py']
    deps_to_install = [
        'fastapi==0.104.1',
        'uvicorn[standard]==0.24.0',
        'peewee==3.17.0',
        'sqlite-utils==3.35.0',
        'pydantic==2.5.0',
        'pydantic-settings==2.1.0',
        'passlib[bcrypt]==1.7.4',
        'python-jose[cryptography]==3.3.0',
        'python-multipart==0.0.6',
        'playwright==1.40.0',
        'aiofiles==23.2.1',
        'httpx==0.25.2'
    ]
    
    print("正在卸载冲突的库...")
    for dep in deps_to_uninstall:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", dep])
            print(f"已卸载 {dep}")
        except:
            print(f"{dep} 未安装或卸载失败，继续...")
    
    print("\n正在安装正确的依赖...")
    for dep in deps_to_install:
        subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
        print(f"已安装 {dep}")
    
    print("\n依赖安装完成！")

if __name__ == "__main__":
    install_dependencies()