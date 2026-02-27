import time
from datetime import datetime
import json
import gzip
from io import BytesIO
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ===============================
# 1️⃣ 启动 Selenium（真实浏览器）
# ===============================
def create_driver(profile_name):
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--start-maximized")

    chrome_options.add_argument(
        f"--user-data-dir=/Users/Aceberg/chrome_profiles/{profile_name}"
    )

    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)
    return driver


# ===============================
# 2️⃣ 等你手动登录
# ===============================
def wait_for_login(driver):
    driver.get("https://yingxiao.pinduoduo.com/")

    print("🟡 请在浏览器中手动登录拼多多商家后台")
    print("🟢 登录完成后，回到终端，按【回车】继续...")
    input()

    time.sleep(2)
    print("✅ 已确认登录")


# ===============================
# 3️⃣ 等推广页面加载完成
# ===============================
def wait_promotion_page_ready(driver, timeout=30):
    print("🚀 自动进入推广页面")

    driver.get("https://yingxiao.pinduoduo.com/goods/promotion/list")

    # 等表格主体出现（而不是只等页面 load）
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "odinTable"))
    )

    print("✅ 推广页面已打开")
    time.sleep(2)


# ===============================
# 4️⃣ 解析 promotion 响应（支持 gzip）
# ===============================
def parse_promotion_response(req):
    body = req.response.body
    encoding = req.response.headers.get("Content-Encoding", "")

    if "gzip" in encoding:
        body = gzip.GzipFile(fileobj=BytesIO(body)).read()

    return json.loads(body.decode("utf-8"))


# 获取最后一个promotion
def get_latest_promotion_from_requests(driver):
    """
    用于第一页：从已有 requests 中，拿最近一次 promotion 响应
    """
    for req in reversed(driver.requests):
        if req.response and "promotion/v2/list" in req.url:
            try:
                data = parse_promotion_response(req)
                if data.get("success"):
                    return data.get("result", {}).get("adInfos", [])
            except Exception:
                pass
    return []



# ===============================
# 5️⃣ 等“下一次新的 promotion 请求”
# ===============================
def wait_next_promotion(driver, since_ts, timeout=20):
    """
    只返回：since_ts 之后产生的 promotion 请求
    """
    start = time.time()

    # ✅ 关键修复：float → datetime
    since_dt = datetime.fromtimestamp(since_ts)

    while time.time() - start < timeout:
        for req in driver.requests:
            if (
                req.response
                and "promotion/v2/list" in req.url
                and req.date
                and req.date >= since_dt
            ):
                try:
                    data = parse_promotion_response(req)
                    if data.get("success"):
                        return data.get("result", {}).get("adInfos", [])
                except Exception:
                    pass
        time.sleep(0.3)

    return []


# ===============================
# 6️⃣ 点击“下一页”
# ===============================
def click_next_page(driver):
    """
    只负责尝试触发下一页
    任意异常 = 已到最后一页
    """
    try:
        next_li = driver.find_elements(
            By.XPATH,
            "//li[contains(@class,'anq-pagination-next')]"
        )

        if not next_li:
            return False

        # 判断 aria-disabled（唯一可靠信号）
        if next_li[0].get_attribute("aria-disabled") == "true":
            return False

        btn = next_li[0].find_element(By.TAG_NAME, "button")
        driver.execute_script("arguments[0].click();", btn)
        return True

    except Exception:
        return False






# ===============================
# 7️⃣ 从当前页面状态开始爬
# ===============================
def crawl_from_current_page(driver):
    all_items = []
    seen_ids = set()

    print("⏳ 读取当前页 promotion 请求（第一页）")

    # ✅ 第 1 页：直接从历史 requests 中取
    first_items = get_latest_promotion_from_requests(driver)

    if not first_items:
        print("❌ 当前页未捕获到 promotion 数据")
        return all_items

    for it in first_items:
        gid = it.get("goodsId")
        if gid and gid not in seen_ids:
            seen_ids.add(gid)
            all_items.append(it)

    page = 1
    print(f"✅ 第 1 页获取 {len(first_items)} 条")

    while True:
        print(f"📄 翻到第 {page + 1} 页")

        # ✅ 等表格稳定（避免点到中间态）
        time.sleep(1)

        since_ts = time.time()

        if not click_next_page(driver):
            print("✅ 已到最后一页，结束")
            break

        # 点击下一页后 休息
        time.sleep(2)


        items = wait_next_promotion(driver, since_ts)

        if not items:
            print("⚠️ 本页未捕获到 promotion 请求，结束")
            break

        new_count = 0
        for it in items:
            gid = it.get("goodsId")
            if gid and gid not in seen_ids:
                seen_ids.add(gid)
                all_items.append(it)
                new_count += 1

        print(f"✅ 本页新增 {new_count} 条")

        if new_count == 0:
            print("⚠️ 数据未推进，结束")
            break

        if len(items) < 50:
            print("✅ 返回数量不足 50，已到最后一页")
            break

        page += 1
        time.sleep(1.2)

    return all_items














# ===============================
# 8️⃣ 主入口
# ===============================
if __name__ == "__main__":

    SHOP_PROFILES = [
        "pdd_shop_001",
    ]

    for shop in SHOP_PROFILES:
        print(f"\n🚀 处理店铺 {shop}")
        driver = create_driver(shop)

        try:
            wait_for_login(driver)

            print("👉 请手动进入【推广页面】")
            input("确认后按回车开始抓取...")

            wait_promotion_page_ready(driver)

            data = crawl_from_current_page(driver)

            print(f"\n🎉 抓取完成，共 {len(data)} 条 promotion 数据")

        finally:
            driver.quit()
