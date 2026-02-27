"""
拼多多自动化爬虫 - 使用Selenium自动获取crawlerInfo
"""
import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


class PDDAutoCrawler:
    def __init__(self, headless=False):
        """
        初始化爬虫
        
        参数:
            headless: 是否使用无头模式（不显示浏览器窗口）
        """
        self.driver = None
        self.headless = headless
        self.crawler_info = None
        self.cookies = None
        
    def init_driver(self):
        """初始化浏览器驱动"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        # 反检测设置
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 启用网络日志
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
        # 修改navigator.webdriver标志
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        })
        
    def login(self, username=None, password=None):
        """
        登录拼多多商家后台
        
        参数:
            username: 用户名（可选，如果不提供则需要手动登录）
            password: 密码（可选）
        """
        if not self.driver:
            self.init_driver()
        
        # 访问登录页面
        self.driver.get('https://mms.pinduoduo.com/login')
        
        if username and password:
            # 自动登录（需要根据实际页面结构调整）
            try:
                username_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "username"))
                )
                password_input = self.driver.find_element(By.ID, "password")
                
                username_input.send_keys(username)
                password_input.send_keys(password)
                
                login_button = self.driver.find_element(By.CLASS_NAME, "login-button")
                login_button.click()
            except Exception as e:
                print(f"自动登录失败: {e}")
                print("请手动登录...")
        else:
            print("请在浏览器中手动登录...")
        
        # 等待登录完成
        WebDriverWait(self.driver, 60).until(
            EC.url_contains('pinduoduo.com')
        )
        
        print("登录成功！")
        
    def extract_crawler_info_from_logs(self):
        """从浏览器网络日志中提取crawlerInfo"""
        logs = self.driver.get_log('performance')
        
        for log in logs:
            try:
                log_data = json.loads(log['message'])
                message = log_data.get('message', {})
                method = message.get('method', '')
                
                # 查找网络请求
                if method == 'Network.requestWillBeSent':
                    params = message.get('params', {})
                    request = params.get('request', {})
                    url = request.get('url', '')
                    
                    # 找到推广列表API请求
                    if 'goods/promotion' in url:
                        headers = request.get('headers', {})
                        
                        # 提取anti-content（即crawlerInfo）
                        if 'anti-content' in headers:
                            self.crawler_info = headers['anti-content']
                            print(f"✅ 成功提取 crawlerInfo: {self.crawler_info[:50]}...")
                            
                        # 提取cookie
                        if 'cookie' in headers:
                            self.cookies = headers['cookie']
                            
                        return True
                        
            except Exception as e:
                continue
                
        return False
        
    def navigate_to_promotion_page(self):
        """导航到推广列表页面，触发API请求"""
        if not self.driver:
            raise Exception("浏览器未初始化")
        
        # 访问推广列表页面
        self.driver.get('https://yingxiao.pinduoduo.com/goods/promotion/list')
        
        # 等待页面加载
        time.sleep(3)
        
        # 尝试从日志中提取crawlerInfo
        if self.extract_crawler_info_from_logs():
            return True
        
        # 如果没有找到，尝试刷新页面
        print("未找到crawlerInfo，刷新页面重试...")
        self.driver.refresh()
        time.sleep(3)
        
        return self.extract_crawler_info_from_logs()
        
    def get_fresh_crawler_info(self):
        """
        获取最新的crawlerInfo
        
        返回:
            dict: {"crawler_info": str, "cookies": str}
        """
        try:
            if not self.driver:
                self.login()
            
            # 导航到推广页面获取crawlerInfo
            if self.navigate_to_promotion_page():
                return {
                    "success": True,
                    "crawler_info": self.crawler_info,
                    "cookies": self.cookies
                }
            else:
                return {
                    "success": False,
                    "message": "无法提取crawlerInfo"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"获取crawlerInfo失败: {str(e)}"
            }
            
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            

# 使用示例
if __name__ == "__main__":
    crawler = PDDAutoCrawler(headless=False)
    
    try:
        # 登录（首次使用需要手动登录）
        crawler.login()
        
        # 获取最新的crawlerInfo
        result = crawler.get_fresh_crawler_info()
        
        if result['success']:
            print("\n" + "="*50)
            print("✅ 成功获取最新的crawlerInfo:")
            print(f"crawlerInfo: {result['crawler_info']}")
            print("="*50)
            
            # 保存到文件供其他脚本使用
            with open('pdd_crawler_info.json', 'w') as f:
                json.dump({
                    'crawler_info': result['crawler_info'],
                    'cookies': result['cookies'],
                    'update_time': datetime.now().isoformat()
                }, f, indent=2)
            print("\n✅ 已保存到 pdd_crawler_info.json")
        else:
            print(f"\n❌ 失败: {result['message']}")
            
    finally:
        # 保持浏览器打开10秒，方便查看
        time.sleep(10)
        crawler.close()
