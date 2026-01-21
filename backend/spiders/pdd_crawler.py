from playwright.sync_api import sync_playwright
import json
import time

TARGET_API = "/venus/api/goods/promotion/v1/list"

def main():
    all_items = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled"
            ]
        )

        context = browser.new_context(
            viewport={"width": 1400, "height": 900}
        )

        page = context.new_page()

        # ===== 监听接口 =====
        def handle_response(resp):
            if TARGET_API in resp.url:
                try:
                    data = resp.json()
                    result = data.get("result", {})
                    items = result.get("list", [])
                    total = result.get("total", 0)

                    if items:
                        all_items.extend(items)
                        print(f"✅ 抓到 {len(items)} 条，本页累计 {len(all_items)} / {total}")
                except Exception:
                    pass

        page.on("response", handle_response)

        # ===== 打开拼多多后台 =====
        page.goto("https://yingxiao.pinduoduo.com/", timeout=60000)

        print("\n==============================")
        print("👉 请在浏览器中【手动登录拼多多后台】")
        print("👉 如果出现【拖拽验证码】，请手动完成")
        print("👉 确认已经进入后台首页后")
        print("👉 回到【终端】，按一次 Enter 继续")
        print("==============================\n")

        input("⏸ 等待你完成登录，按 Enter 继续...")

        # ===== 进入促销商品页 =====
        page.goto(
            "https://yingxiao.pinduoduo.com/goods/promotion/list?msfrom=mms_sidenav",
            timeout=60000
        )

        print("⏳ 页面加载中...")
        page.wait_for_timeout(5000)

        print("\n⚠️ 请确认：")
        print("1️⃣ 页面已经切换到【已取消】标签")
        print("2️⃣ 日期筛选已是你想要的范围")
        input("确认无误后，按 Enter 开始自动滚动抓取...")

        # ===== 自动滚动分页 =====
        last_height = 0
        same_count = 0

        while True:
            page.mouse.wheel(0, 3000)
            page.wait_for_timeout(2000)

            height = page.evaluate("document.body.scrollHeight")

            if height == last_height:
                same_count += 1
            else:
                same_count = 0

            last_height = height

            if same_count >= 3:
                print("🛑 已滚动到底")
                break

        # ===== 保存数据 =====
        with open("pdd_cancelled_promotion.json", "w", encoding="utf-8") as f:
            json.dump(all_items, f, ensure_ascii=False, indent=2)

        print(f"\n🎉 完成！共抓取 {len(all_items)} 条数据")
        browser.close()


if __name__ == "__main__":
    main()
