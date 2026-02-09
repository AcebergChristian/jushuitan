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
def click_next_page(driver):
    next_btn = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((
            By.XPATH,
            '//*[@id="odinTable"]/div[3]/ul/li[11]/button'
        ))
    )
    next_btn.click()



def wait_for_promotion_response(driver, timeout=15):
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



# 获取当前页面数据
def get_current_page_data(driver):
    for req in driver.requests:
        if req.response and "promotion/v2/list" in req.url:
            body = req.response.body
            try:
                import json
                data = json.loads(body.decode("utf-8"))
                if data.get("success"):
                    return data.get("result", {}).get("adInfos", [])
            except Exception:
                pass
    return []



# ===============================
# 5️⃣ 正确分页（一页一参数）
# ===============================
def get_all_promotion_data(driver):
    all_data = []
    page = 1

    while True:
        print(f"📄 浏览器抓取第 {page} 页")

        if page == 1:
            # 第 1 页：不要 clear，等首次请求
            items = wait_for_promotion_response(driver)
        else:
            # 第 2 页开始：翻页 → 新请求
            driver.requests.clear()
            click_next_page(driver)
            items = wait_for_promotion_response(driver)

        if not items:
            print("⚠️ 本页无数据或失败，停止")
            break

        all_data.extend(items)

        if len(items) < 50:
            print("✅ 已到最后一页")
            break

        page += 1
        time.sleep(random.uniform(1.5, 2.5))

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
            time.sleep(5)  # 等页面初始化

            today = datetime.now().strftime("%Y-%m-%d")
            data = get_all_promotion_data(driver)

            print(f"✅ {shop} 抓取 {len(data)} 条")

        finally:
            driver.quit()
