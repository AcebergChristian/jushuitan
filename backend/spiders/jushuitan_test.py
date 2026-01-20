import time
from playwright.sync_api import sync_playwright

def fetch_order_amount_list():
    captured_data = None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=400)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            locale="zh-CN",
            timezone_id="Asia/Shanghai",
        )
        page = context.new_page()

        # 1. 去登录页
        page.goto("https://sc.scm121.com/login")
        print("请完成手动登录、滑块/验证码等操作...")
        input("登录成功 + 进入订单/分配页面后，按回车继续...")

        # 2. 刷新确保 cookie/session 稳定
        page.reload()
        time.sleep(5)

        # 3. 如果登录后不是目标页，再导航（根据实际调整）
        # page.goto("https://sc.scm121.com/tradeManage/tower/distribute")
        # time.sleep(5)

        print("已进入页面。现在请你手动：")
        print("  - 设置搜索条件（时间范围、订单状态等）")
        print("  - 点击『查询』或『搜索』按钮")
        print("监听已开启，接口响应会自动打印...")

        def on_response(response):
            nonlocal captured_data
            url = response.url
            print(f"响应: {url} | 状态: {response.status}")
            if "/api/inner/order/list" in url and response.status == 200:
                try:
                    captured_data = response.json()
                    print("\n" + "="*60)
                    print("捕获到目标接口！")
                    print(captured_data)
                    print("="*60 + "\n")
                except Exception as e:
                    print(f"JSON 解析失败: {e}")

        page.on("response", on_response)

        # 保持浏览器打开足够久，让你手动操作
        print("浏览器保持打开 120 秒（可手动延长），操作完成后按 Ctrl+C 结束...")
        time.sleep(120)  # 或更长

        if captured_data:
            print("最终捕获数据：", captured_data)
        else:
            print("未捕获到 /api/company/order/amount/list 接口")

        # browser.close()  # 先别关，方便看控制台

    return captured_data

if __name__ == "__main__":
    data = fetch_order_amount_list()