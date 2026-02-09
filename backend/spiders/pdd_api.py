import time
import random
import requests
from datetime import datetime
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


PDD_API_URL = "https://yingxiao.pinduoduo.com/mms-gateway/venus/api/goods/promotion/v2/list"


# ===============================
# 1️⃣ 启动 Selenium（真实浏览器）
# ===============================
def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)
    return driver


# ===============================
# 2️⃣ 等待你手动/自动登录
# ===============================
def wait_for_login(driver):
    driver.get("https://yingxiao.pinduoduo.com/")

    print("🟡 请登录拼多多商家后台，登录完成后等待页面加载...")
    WebDriverWait(driver, 300).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    time.sleep(5)
    print("✅ 登录完成")


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
def request_one_page(params, date_str, page_number):
    session = requests.Session()

    for c in params["cookies"]:
        session.cookies.set(
            c["name"],
            c["value"],
            domain=c.get("domain")
        )

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
        "pageNumber": page_number,
        "pageSize": 50,
        "sortBy": 9999,
        "orderBy": 9999,
        "filter": {},
        "scenesMode": 1
    }

    resp = session.post(
        PDD_API_URL,
        headers=headers,
        json=payload,
        timeout=15
    )
    resp.raise_for_status()
    return resp.json()


# ===============================
# 5️⃣ 正确分页（一页一参数）
# ===============================
def get_all_promotion_data(driver, date_str):
    all_data = []
    page = 1

    while True:
        print(f"📄 抓取第 {page} 页")

        params = get_once_request_params(driver)
        result = request_one_page(params, date_str, page)

        if not result.get("success"):
            print("⚠️ 接口返回失败，停止")
            break

        items = result.get("result", {}).get("adInfos", [])
        if not items:
            print("✅ 无更多数据")
            break

        all_data.extend(items)

        if len(items) < 50:
            print("✅ 已到最后一页")
            break

        page += 1
        time.sleep(random.uniform(1.5, 3.0))

    return all_data


# ===============================
# 6️⃣ 主入口
# ===============================
if __name__ == "__main__":
    driver = create_driver()
    try:
        wait_for_login(driver)

        today = datetime.now().strftime("%Y-%m-%d")
        data = get_all_promotion_data(driver, today)

        print(f"\n🎉 抓取完成，总条数: {len(data)}")

    finally:
        driver.quit()
