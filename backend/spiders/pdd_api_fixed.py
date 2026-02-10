import time
import random
import requests
from datetime import datetime
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# 店铺映射
shopdict = {
    '19536518704': '19250015'

}



PDD_API_URL = "https://yingxiao.pinduoduo.com/mms-gateway/venus/api/goods/promotion/v2/list"


# ===============================
# 1️⃣ 启动 Selenium（真实浏览器）
# ===============================
def create_driver(profile_name):
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--start-maximized")

    # 👇 每个账号一个独立用户目录
    chrome_options.add_argument(
        f"--user-data-dir=/Users/Aceberg/chrome_profiles/{profile_name}"
    )

    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)
    return driver


# ===============================
# 2️⃣ 等待你手动/自动登录
# ===============================
def wait_for_login(driver):
    driver.get("https://yingxiao.pinduoduo.com/")

    print("🟡 请在浏览器中手动登录拼多多商家后台")
    print("🟢 登录完成后，回到终端，按【回车】继续...")

    input()  # ⬅️ 阻塞，直到你按回车

    # 给页面一点缓冲时间
    time.sleep(2)

    print("✅ 已确认登录，继续执行")


# ===============================
# 3️⃣ 前端触发一次请求并抓参数
# ===============================
def get_once_request_params(driver):
    driver.requests.clear()

    # ⚠️ 关键：通过 JS 触发前端请求（模拟翻页）
    driver.execute_script("""
        const evt = new Event('scroll');
        window.dispatchEvent(evt);
    """)

    time.sleep(2)

    for req in driver.requests:
        if req.response and "promotion/v2/list" in req.url:
            print("✅ 捕获到 promotion 请求")
            return {
                "crawlerInfo": req.params.get("crawlerInfo"),
                "anti_content": req.headers.get("anti-content"),
                "user_agent": req.headers.get("user-agent"),
                "cookies": driver.get_cookies(),
            }

    raise RuntimeError("❌ 未捕获到 promotion 接口请求")


# ===============================
# 4️⃣ 用这一套参数请求一页
# ===============================
def request_one_page(params, date_str):
    session = requests.Session()

    for c in params["cookies"]:
        session.cookies.set(c["name"], c["value"], domain=c.get("domain"))

    headers = {
        "user-agent": params["user_agent"],
        "anti-content": params["anti_content"],
        "content-type": "application/json",
        "referer": "https://yingxiao.pinduoduo.com/",
        "origin": "https://yingxiao.pinduoduo.com",
    }

    payload = {
        "crawlerInfo": params["crawlerInfo"],
        "clientType": 1,
        "blockType": 3,
        "withTagsInfo": True,
        "beginDate": date_str,
        "endDate": date_str,
        "pageNumber": 1,   # 🔥 永远是 1
        "pageSize": 50,
        "sortBy": 9999,
        "orderBy": 9999,
        "filter": {},
        "scenesMode": 1
    }

    resp = session.post(PDD_API_URL, headers=headers, json=payload, timeout=15)
    resp.raise_for_status()
    return resp.json()


# 点击下一页，不要用pagenumber
def click_next_page_safe(driver):
    btn = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((
            By.XPATH,
            '/html/body/div[1]/div/div[2]/div[2]/div[4]/div[3]/div[3]/ul/li[10]/button'
        ))
    )
    btn.click()



def wait_first_promotion(driver, timeout=30):
    print("⏳ 等待页面自动发 promotion 第 1 页请求")
    start = time.time()
    last_count = 0

    while time.time() - start < timeout:
        current_count = len(driver.requests)
        
        # 打印调试信息
        if current_count != last_count:
            print(f"📊 当前捕获到 {current_count} 个请求")
            last_count = current_count
        
        for req in driver.requests:
            if "promotion/v2/list" in req.url:
                print(f"🔍 找到 promotion 请求: {req.url[:100]}")
                
                if req.response:
                    try:
                        import json
                        data = json.loads(req.response.body.decode("utf-8"))
                        if data.get("success"):
                            print("✅ 捕获第 1 页 promotion 请求")
                            return data.get("result", {}).get("adInfos", [])
                        else:
                            print(f"⚠️ 请求失败: {data.get('errorMsg', 'unknown')}")
                    except Exception as e:
                        print(f"⚠️ 解析响应失败: {e}")
                else:
                    print("⏳ 请求还没有响应")
                    
        time.sleep(0.5)

    print(f"❌ 超时：{timeout}秒内未捕获到有效的 promotion 响应")
    return []

def wait_for_promotion_response(driver, timeout=20):
    start = time.time()
    while time.time() - start < timeout:
        for req in driver.requests:
            if req.response and "promotion/v2/list" in req.url:
                try:
                    import json
                    data = json.loads(req.response.body.decode("utf-8"))
                    if data.get("success"):
                        return data.get("result", {}).get("adInfos", [])
                except Exception:
                    pass
        time.sleep(0.3)
    return []


def wait_promotion_page_ready(driver, timeout=30):
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.ID, "odinTable"))
    )
    print("✅ 推广页面已加载")
    time.sleep(3)  # 给页面更多时间初始化

# 
def force_trigger_promotion_request(driver):
    print("🧠 主动触发 promotion 首次请求")

    # 找到"下一页"按钮（更稳）
    next_btn = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((
            By.XPATH,
            "/html/body/div[1]/div/div[2]/div[2]/div[4]/div[3]/div[3]/ul/li[10]/button"
        ))
    )

    # 如果是 disabled，说明还没准备好
    if "disabled" in next_btn.get_attribute("class"):
        print("⏳ 下一页不可点，等待页面稳定")
        time.sleep(3)

    # 清空请求记录，然后点击
    driver.requests.clear()
    next_btn.click()
    
    # 给更多时间让请求发出
    time.sleep(4)


# ===============================
# 5️⃣ 正确分页（一页一参数）
# ===============================
def get_all_promotion_data(driver):
    all_data = []
    page = 1

    # 第 1 页：等自动请求
    items = wait_first_promotion(driver)
    if not items:
        print("❌ 第 1 页都没拿到，直接结束")
        return all_data

    all_data.extend(items)

    while True:
        print(f"📄 抓取第 {page + 1} 页")

        driver.requests.clear()
        click_next_page_safe(driver)

        items = wait_first_promotion(driver)

        if not items:
            print("⚠️ 无更多数据")
            break

        all_data.extend(items)

        if len(items) < 50:
            print("✅ 已到最后一页")
            break

        page += 1
        time.sleep(2)

    return all_data









# ===============================
# 6️⃣ 主入口
# ===============================
if __name__ == "__main__":

    SHOP_PROFILES = [
        "pdd_shop_001",
        # "pdd_shop_002",
        # "pdd_shop_003",
    ]

    for shop in SHOP_PROFILES:
        print(f"\n🚀 处理店铺 {shop}")
        driver = create_driver(shop)

        try:
            wait_for_login(driver)

            print("👉 请确认你已经【手动进入推广页面】")
            input("确认后按回车...")

            wait_promotion_page_ready(driver)

            force_trigger_promotion_request(driver)

            data = get_all_promotion_data(driver)
            
            print(f"\n✅ 店铺 {shop} 完成，共抓取 {len(data)} 条数据")

        finally:
            driver.quit()
