"""
手动下载 ChromeDriver 的辅助脚本
如果 webdriver-manager 无法自动下载，使用这个脚本
"""
import os
import sys
import zipfile
import requests
from io import BytesIO

def get_chrome_version():
    """获取本机 Chrome 版本"""
    try:
        if sys.platform == "win32":
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
            version, _ = winreg.QueryValueEx(key, "version")
            return version
    except:
        pass
    return None

def download_chromedriver():
    """下载 ChromeDriver"""
    print("="*60)
    print("ChromeDriver 下载工具")
    print("="*60)
    
    # 获取 Chrome 版本
    chrome_version = get_chrome_version()
    if chrome_version:
        print(f"检测到 Chrome 版本: {chrome_version}")
        major_version = chrome_version.split('.')[0]
    else:
        print("无法自动检测 Chrome 版本")
        print("请手动输入你的 Chrome 版本号（打开 Chrome -> 设置 -> 关于 Chrome）")
        chrome_version = input("Chrome 版本号（例如: 131.0.6778.86）: ").strip()
        major_version = chrome_version.split('.')[0]
    
    print(f"\n正在查找匹配的 ChromeDriver...")
    
    # 使用 Chrome for Testing API
    try:
        # 获取可用版本列表
        url = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
        print(f"正在访问: {url}")
        
        response = requests.get(url, timeout=30)
        data = response.json()
        
        # 查找匹配的版本
        matching_version = None
        for version_info in reversed(data['versions']):
            if version_info['version'].startswith(major_version + '.'):
                matching_version = version_info
                break
        
        if not matching_version:
            print(f"❌ 未找到匹配 Chrome {major_version} 的 ChromeDriver")
            return False
        
        # 查找 Windows chromedriver 下载链接
        driver_url = None
        for download in matching_version['downloads'].get('chromedriver', []):
            if download['platform'] == 'win64':
                driver_url = download['url']
                break
        
        if not driver_url:
            print(f"❌ 未找到 Windows 版本的下载链接")
            return False
        
        print(f"✅ 找到匹配版本: {matching_version['version']}")
        print(f"下载地址: {driver_url}")
        
        # 下载
        print("\n正在下载...")
        response = requests.get(driver_url, timeout=60)
        
        # 解压
        print("正在解压...")
        with zipfile.ZipFile(BytesIO(response.content)) as zip_file:
            # 查找 chromedriver.exe
            for file_name in zip_file.namelist():
                if file_name.endswith('chromedriver.exe'):
                    # 提取到当前目录
                    with zip_file.open(file_name) as source:
                        with open('chromedriver.exe', 'wb') as target:
                            target.write(source.read())
                    print(f"✅ ChromeDriver 已保存到: {os.path.abspath('chromedriver.exe')}")
                    return True
        
        print("❌ 压缩包中未找到 chromedriver.exe")
        return False
        
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        print("\n手动下载步骤:")
        print("1. 访问: https://googlechromelabs.github.io/chrome-for-testing/")
        print(f"2. 下载与 Chrome {major_version} 匹配的 chromedriver-win64.zip")
        print("3. 解压后将 chromedriver.exe 放到当前目录")
        return False

if __name__ == "__main__":
    success = download_chromedriver()
    if success:
        print("\n" + "="*60)
        print("✅ 完成！ChromeDriver 已准备就绪")
        print("="*60)
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("❌ 下载失败，将在运行时尝试其他方法")
        print("="*60)
        sys.exit(1)
