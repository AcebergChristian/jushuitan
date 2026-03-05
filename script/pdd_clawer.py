import time
from datetime import datetime, timedelta, date
import json
import gzip
from io import BytesIO
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import os

# 导入本地数据库模型
from models.database_models import PddTable, PddBillRecord, database
from pdddata import pdddata

# ===============================
# 1️⃣ 启动 Selenium（真实浏览器）
# ===============================
def create_driver(profile_name):
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")
    
    # 跨平台路径处理
    if sys.platform == "win32":
        # Windows 路径
        profile_dir = os.path.join(os.path.expanduser("~"), "chrome_profiles", profile_name)
    else:
        # macOS/Linux 路径
        profile_dir = f"/Users/Aceberg/chrome_profiles/{profile_name}"
    
    # 确保目录存在且路径正确
    os.makedirs(profile_dir, exist_ok=True)
    chrome_options.add_argument(f"--user-data-dir={profile_dir}")
    
    # 尝试多种方式创建 driver
    driver = None
    
    # 方法1: 优先使用本地 chromedriver.exe（如果存在）
    try:
        print("🔍 检查本地 chromedriver.exe...")
        local_driver = os.path.join(os.getcwd(), "chromedriver.exe")
        if os.path.exists(local_driver):
            print(f"   找到: {local_driver}")
            service = Service(local_driver)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print("✅ 使用本地 chromedriver.exe")
            driver.set_page_load_timeout(30)
            return driver
        else:
            print("   未找到本地 chromedriver.exe")
    except Exception as e:
        print(f"⚠️ 本地 chromedriver 失败: {e}")
    
    # 方法2: 尝试使用 webdriver-manager（需要网络）
    try:
        print("🔍 尝试自动下载 ChromeDriver...")
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ 使用自动下载的 ChromeDriver")
        driver.set_page_load_timeout(30)
        return driver
    except Exception as e:
        print(f"⚠️ 自动下载失败: {e}")
    
    # 方法3: 让 Selenium 自己找（依赖系统 PATH）
    try:
        print("🔍 尝试使用系统 PATH 中的 ChromeDriver...")
        driver = webdriver.Chrome(options=chrome_options)
        print("✅ 使用系统 ChromeDriver")
        driver.set_page_load_timeout(30)
        return driver
    except Exception as e3:
        print(f"⚠️ 系统 ChromeDriver 失败: {e3}")
    
    # 所有方法都失败
    print(f"\n{'='*60}")
    print("❌ 无法启动 ChromeDriver")
    print(f"{'='*60}")
    print("解决方案:")
    print("1. 手动下载 ChromeDriver:")
    print("   a. 打开 Chrome 浏览器，查看版本号")
    print("      (设置 -> 关于 Chrome)")
    print("   b. 访问: https://googlechromelabs.github.io/chrome-for-testing/")
    print("   c. 下载对应版本的 chromedriver-win64.zip")
    print(f"   d. 解压后将 chromedriver.exe 放到: {os.getcwd()}")
    print("")
    print("2. 或者配置代理后重新运行（如果是网络问题）")
    print(f"{'='*60}\n")
    raise Exception("无法启动 ChromeDriver")


# ===============================
# 2️⃣ 退出登录
# ===============================
def logout(driver):
    """退出当前登录"""
    try:
        print("🚪 正在退出当前登录...")
        
        # 清除所有cookies
        driver.delete_all_cookies()
        print("✅ 已清除所有cookies")
        
        # 清除浏览器缓存和本地存储
        driver.execute_script("window.localStorage.clear();")
        driver.execute_script("window.sessionStorage.clear();")
        print("✅ 已清除本地存储")
        
        print("✅ 退出登录完成")
        
    except Exception as e:
        print(f"⚠️ 退出登录失败: {e}")


# 3️⃣ 等你手动登录
# ===============================
def wait_for_login(driver, username=None, password=None):
    # 先访问一个空白页面，确保可以清除cookies
    driver.get("about:blank")
    time.sleep(1)

    # 清除所有登录信息（确保彻底清除）
    try:
        driver.delete_all_cookies()
        driver.execute_script("window.localStorage.clear();")
        driver.execute_script("window.sessionStorage.clear();")
        print("✅ 已清除所有登录信息")
    except Exception as e:
        print(f"⚠️ 清除登录信息失败: {e}")

    # 先访问退出登录的URL（强制退出）
    try:
        print("🚪 访问退出登录页面...")
        driver.get("https://mms.pinduoduo.com/logout")
        time.sleep(2)
    except:
        pass

    # 再次清除（双重保险）
    try:
        driver.delete_all_cookies()
        driver.execute_script("window.localStorage.clear();")
        driver.execute_script("window.sessionStorage.clear();")
    except:
        pass

    # 现在访问登录页面
    driver.get("https://mms.pinduoduo.com/")
    print("🟡 正在打开拼多多商家后台登录页...")
    time.sleep(3)

    # 检查是否已经登录（通过检查是否在登录页面）
    try:
        # 尝试查找登录页面的特征元素（账号密码登录按钮）
        login_tab = driver.find_elements(By.XPATH, '//*[@id="root"]/div[1]/div/div/main/div/section[2]/div/div/div/div[1]/div/div/div[2]')

        if not login_tab:
            # 没有找到登录元素，说明已经登录
            print("⚠️ 检测到已登录状态")
            print("🔄 需要重新登录到新店铺")
            print("🟡 请手动退出当前店铺，然后登录新店铺")
            print("🟢 登录完成后，回到终端，按【回车】继续...")
            input()
            time.sleep(2)
            print("✅ 已确认登录")
            return

        print("🔐 检测到登录页面，开始登录流程...")

    except Exception as e:
        # 如果检测失败，假设已经登录
        print("⚠️ 未检测到登录页面")
        print("🟡 请手动登录到新店铺")
        print("🟢 登录完成后，回到终端，按【回车】继续...")
        input()
        time.sleep(2)
        print("✅ 已确认登录")
        return

    # 需要登录，执行登录流程
    try:
        # 1. 点击登录按钮（切换到账号密码登录）
        print("🔘 点击账号密码登录...")
        login_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div[1]/div/div/main/div/section[2]/div/div/div/div[1]/div/div/div[2]'))
        )
        driver.execute_script("arguments[0].click();", login_tab)
        time.sleep(1)

        # 2. 输入账号
        if username:
            print(f"📝 输入账号: {username}")
            username_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="usernameId"]'))
            )
            username_input.clear()
            username_input.send_keys(username)
            time.sleep(0.5)
        else:
            print("⚠️ 未提供账号，请手动输入")

        # 3. 输入密码
        if password:
            print("🔑 输入密码...")
            password_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="passwordId"]'))
            )
            password_input.clear()
            password_input.send_keys(password)
            time.sleep(0.5)
        else:
            print("⚠️ 未提供密码，请手动输入")

        # 4. 点击登录按钮（如果提供了账号密码）
        if username and password:
            print("🔐 点击登录按钮...")
            login_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div[1]/div/div/main/div/section[2]/div/div/div/div[2]/section/div/div/button'))
            )
            driver.execute_script("arguments[0].click();", login_button)
            time.sleep(2)

        # 5. 等待手动确认（可能需要验证码）
        print("\n" + "="*60)
        print("⚠️  注意：可能需要手机验证码验证")
        print("🟡 请在浏览器中完成登录（包括验证码验证）")
        print("🟢 登录完成后，回到终端，按【回车】继续...")
        print("="*60 + "\n")
        input()
        time.sleep(2)
        print("✅ 已确认登录")

    except Exception as e:
        print(f"⚠️ 自动登录失败: {e}")
        print("🟡 请在浏览器中手动登录拼多多商家后台")
        print("🟢 登录完成后，回到终端，按【回车】继续...")
        input()
        time.sleep(2)
        print("✅ 已确认登录")



# ===============================
# 3️⃣ 选择日期范围
# ===============================
def select_date_range(driver, target_date=None):
    """
    在推广页面等待用户选择日期，然后读取实际选择的日期
    返回: date对象（年-月-日）- 从页面实际读取的日期
    """
    # 等待用户手动选择日期
    print("\n" + "="*60)
    print("� 请在页面上选择日期")
    print("🟢 选择完成后，按【回车】继续...")
    print("="*60 + "\n")
    input()
    
    # 从页面读取实际设置的日期
    actual_date = None
    try:
        print("🔍 正在读取页面日期...")
        
        # 使用提供的 XPath 读取日期
        date_input = driver.find_element(By.XPATH, '//*[@id="page-container"]/div/div[1]/div[2]/div/div[2]/div[1]/input')
        date_value = date_input.get_attribute('value')
        
        print(f"   读取到的值: {date_value}")
        
        if date_value and date_value.strip():
            date_str = date_value.strip()
            
            # 尝试不同的日期格式
            for fmt in ['%Y/%m/%d', '%Y-%m-%d', '%Y年%m月%d日']:
                try:
                    actual_date = datetime.strptime(date_str, fmt).date()
                    print(f"✅ 成功解析日期: {actual_date}")
                    break
                except:
                    continue
        
        # 如果解析失败，让用户手动输入
        if not actual_date:
            print(f"⚠️ 无法解析日期格式: {date_value}")
            print("请手动输入您在页面上设置的日期")
            date_input_str = input("请输入日期 (格式: YYYY-MM-DD，例如 2026-02-01): ").strip()
            
            try:
                actual_date = datetime.strptime(date_input_str, '%Y-%m-%d').date()
                print(f"✅ 使用手动输入的日期: {actual_date}")
            except:
                print(f"❌ 日期格式错误，无法继续")
                raise ValueError("无效的日期格式")
            
    except Exception as e:
        print(f"❌ 读取页面日期失败: {e}")
        print("请手动输入您在页面上设置的日期")
        date_input_str = input("请输入日期 (格式: YYYY-MM-DD，例如 2026-02-01): ").strip()
        
        try:
            actual_date = datetime.strptime(date_input_str, '%Y-%m-%d').date()
            print(f"✅ 使用手动输入的日期: {actual_date}")
        except:
            print(f"❌ 日期格式错误，无法继续")
            raise ValueError("无效的日期格式")
    
    print(f"\n📅 最终使用的日期: {actual_date}\n")
    return actual_date



# ===============================
# 4️⃣ 等推广页面加载完成
# ===============================
def wait_promotion_page_ready(driver, timeout=30):
    print("🚀 自动进入推广页面")
    driver.get("https://yingxiao.pinduoduo.com/goods/promotion/list")
    
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "odinTable"))
    )
    
    print("✅ 推广页面已打开")
    time.sleep(2)


# ===============================
# 5️⃣ 解析 promotion 响应（支持 gzip）
# ===============================
def parse_promotion_response(req):
    body = req.response.body
    encoding = req.response.headers.get("Content-Encoding", "")

    if "gzip" in encoding:
        body = gzip.GzipFile(fileobj=BytesIO(body)).read()

    return json.loads(body.decode("utf-8"))


# 获取最后一个promotion
def get_latest_promotion_from_requests(driver):
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
# 6️⃣ 等"下一次新的 promotion 请求"
# ===============================
def wait_next_promotion(driver, since_ts, timeout=20):
    start = time.time()
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
# 7️⃣ 点击"下一页"
# ===============================
def click_next_page(driver):
    try:
        next_li = driver.find_elements(
            By.XPATH,
            "//li[contains(@class,'anq-pagination-next')]"
        )

        if not next_li:
            return False

        if next_li[0].get_attribute("aria-disabled") == "true":
            return False

        btn = next_li[0].find_element(By.TAG_NAME, "button")
        driver.execute_script("arguments[0].click();", btn)
        return True

    except Exception:
        return False


# ===============================
# 8️⃣ 从当前页面状态开始爬
# ===============================
def crawl_from_current_page(driver):
    all_items = []
    seen_ids = set()

    print("⏳ 读取当前页 promotion 请求（第一页）")

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
        time.sleep(1)

        since_ts = time.time()

        if not click_next_page(driver):
            print("✅ 已到最后一页，结束")
            break

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
# 9️⃣ 保存推广数据到数据库
# ===============================
def save_promotion_to_db(items, store_id=None, data_date=None):
    """
    将推广数据保存到PddTable
    items: 推广数据列表
    store_id: 店铺ID
    data_date: 数据日期（date对象）
    """
    if not items:
        print("⚠️ 没有数据需要保存")
        return 0
    
    if not data_date:
        print("⚠️ 未提供数据日期")
        return 0
    
    print(f"\n💾 开始保存推广数据...")
    print(f"   店铺ID: {store_id}")
    print(f"   数据日期: {data_date}")
    print(f"   数据条数: {len(items)}")
    
    with database.atomic():
        # 1. 先删除该店铺该日期的所有旧记录
        deleted_count = PddTable.delete().where(
            (PddTable.store_id == store_id) &
            (PddTable.data_date == data_date)
        ).execute()
        print(f"🗑️  删除旧记录: {deleted_count} 条")
        
        # 2. 插入新记录
        saved_count = 0
        error_count = 0
        
        for item in items:
            try:
                # 准备数据
                data = {
                    "ad_id": str(item.get("adId")),
                    "ad_name": item.get("adName"),
                    "goods_id": str(item.get("goodsId")) if item.get("goodsId") else None,
                    "store_id": store_id,
                    "goods_name": item.get("goodsName"),
                    "orderSpendNetCostPerOrder": item.get("reportInfo", {}).get("orderSpendNetCostPerOrder"),
                    "data_date": data_date,  # 添加数据日期
                    "raw_data": json.dumps(item, ensure_ascii=False),
                    "updated_at": datetime.now()
                }
                
                # 创建新记录
                PddTable.create(**data)
                saved_count += 1
                    
            except Exception as e:
                error_count += 1
                print(f"❌ 保存数据失败: {e}")
                print(f"   数据: {item.get('adId')}")
                continue
    
    # 显示统计信息
    print(f"\n{'='*60}")
    print(f"💾 推广数据保存完成:")
    print(f"   🗑️  删除旧数据: {deleted_count} 条")
    print(f"   ✅ 新增数据: {saved_count} 条")
    print(f"   ❌ 失败: {error_count} 条")
    print(f"{'='*60}\n")
    
    return saved_count


# ===============================
# 🔟 访问账单页面并获取退款金额
# ===============================
def get_bill_outcome_amount(driver, shop_id, begin_time, end_time):
    """
    访问账单页面，设置筛选条件，获取outcomeAmount
    begin_time: 开始时间戳（秒）
    end_time: 结束时间戳（秒）
    返回: (outcome_amount, raw_data)
    """
    print("\n🚀 开始获取账单数据...")
    
    # 访问账单页面
    driver.get("https://mms.pinduoduo.com/orders/list?tab=0")
    time.sleep(2)

    driver.get("https://mms.pinduoduo.com/finance/balance?q=1&msfrom=mms_globalsearch")
    time.sleep(2)


    # 点击进入对账中心
    try:
        duizhang_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div[1]/div/div[1]/span[2]'))
        )
        driver.execute_script("arguments[0].click();", duizhang_btn)
        print("✅ 已进入对账中心")
        time.sleep(3)
        
        # 等待对账中心页面加载完成
        print("⏳ 等待对账中心页面加载...")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#root > div > div.Container_container__6H_RU > div > div:nth-child(1) > div > div:nth-child(3) > div"))
        )

        print("✅ 对账中心页面已加载")
        time.sleep(2)
        
    except Exception as e:
        print(f"⚠️ 进入对账中心失败: {e}")
        print("请手动进入对账中心页面后按回车继续...")
        input()

    try:
        
        print("📅 自动设置筛选条件...")
        
        # 1. 设置时间范围
        try:
            # 格式化日期字符串
            date_str = datetime.fromtimestamp(begin_time).strftime('%Y-%m-%d')
            start_datetime = f"{date_str} 00:00:00"
            end_datetime = f"{date_str} 23:59:59"
            date_range_value = f"{start_datetime} ~ {end_datetime}"
            
            print(f"📅 设置时间范围: {date_range_value}")
            
            # 找到时间输入框
            time_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[2]/div/div[1]/div/div[3]/div/div[2]/div[2]/div/div[1]/div/div/div[1]/div/div/div/div/div/div[1]/input'))
            )
            
            # 尝试多种方法设置日期
            success = False
            
            # 方法1: 模拟用户输入
            try:
                print("   尝试方法1: 模拟键盘输入...")
                from selenium.webdriver.common.keys import Keys
                
                # 点击激活输入框
                driver.execute_script("arguments[0].focus();", time_input)
                time.sleep(0.3)
                
                # 清空
                time_input.send_keys(Keys.CONTROL + "a")
                time.sleep(0.2)
                time_input.send_keys(Keys.DELETE)
                time.sleep(0.2)
                
                # 输入新值
                time_input.send_keys(date_range_value)
                time.sleep(0.5)
                
                # 触发事件
                driver.execute_script("""
                    var element = arguments[0];
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                    element.dispatchEvent(new Event('blur', { bubbles: true }));
                """, time_input)
                
                # 按回车确认
                time_input.send_keys(Keys.ENTER)
                time.sleep(1)
                
                # 验证
                current_value = time_input.get_attribute('value')
                if date_str in current_value:
                    print(f"   ✅ 方法1成功: {current_value}")
                    success = True
                else:
                    print(f"   ⚠️ 方法1未生效，当前值: {current_value}")
            except Exception as e:
                print(f"   ⚠️ 方法1失败: {e}")
            
            # 方法2: 使用 React 的方式设置
            if not success:
                try:
                    print("   尝试方法2: React 组件方式...")
                    driver.execute_script("""
                        var input = arguments[0];
                        var value = arguments[1];
                        
                        // 设置值
                        var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                        nativeInputValueSetter.call(input, value);
                        
                        // 触发 React 事件
                        var event = new Event('input', { bubbles: true});
                        input.dispatchEvent(event);
                        
                        var changeEvent = new Event('change', { bubbles: true});
                        input.dispatchEvent(changeEvent);
                    """, time_input, date_range_value)
                    time.sleep(1)
                    
                    # 验证
                    current_value = time_input.get_attribute('value')
                    if date_str in current_value:
                        print(f"   ✅ 方法2成功: {current_value}")
                        success = True
                    else:
                        print(f"   ⚠️ 方法2未生效，当前值: {current_value}")
                except Exception as e:
                    print(f"   ⚠️ 方法2失败: {e}")
            
            # 如果都失败，提示手动操作
            if not success:
                print(f"\n⚠️ 自动设置时间失败")
                print(f"   目标时间: {date_range_value}")
                print(f"   当前时间: {time_input.get_attribute('value')}")
                print("\n   请手动设置时间范围后按回车继续...")
                input()
            else:
                print(f"✅ 时间范围设置成功")
                time.sleep(1)
        except Exception as e:
            print(f"⚠️ 设置时间范围失败: {e}")
            print("   请手动操作后按回车继续...")
            print("\n   提示：如果输入框无法直接输入，可能需要：")
            print("   1. 点击输入框旁边的日历图标")
            print("   2. 在弹出的日期选择器中选择日期")
            print("   3. 点击确定按钮")
            input()
        
        # 2. 点击【展开高级选项】
        try:
            advanced_option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div[2]/div/div[1]/div/div[3]/div/div[2]/div[2]/div/div[1]/div/div/div[2]/div/a'))
            )
            driver.execute_script("arguments[0].click();", advanced_option)
            print("✅ 已展开高级选项")
            time.sleep(1)
        except Exception as e:
            print(f"⚠️ 展开高级选项失败: {e}")
            print("   请手动操作后按回车继续...")
            input()
        
        # 3. 勾选【优惠券结算】
        try:
            coupon_checkbox = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div[2]/div/div[1]/div/div[3]/div/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/label[3]'))
            )
            driver.execute_script("arguments[0].click();", coupon_checkbox)
            print("✅ 已勾选【优惠券结算】")
            time.sleep(0.5)
        except Exception as e:
            print(f"⚠️ 勾选优惠券结算失败: {e}")
            print("   请手动操作后按回车继续...")
            input()
        
        # 4. 勾选【退款】
        try:
            refund_checkbox = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div[2]/div/div[1]/div/div[3]/div/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/label[8]'))
            )
            driver.execute_script("arguments[0].click();", refund_checkbox)
            print("✅ 已勾选【退款】")
            time.sleep(0.5)
        except Exception as e:
            print(f"⚠️ 勾选退款失败: {e}")
            print("   请手动操作后按回车继续...")
            input()
        
        # 5. 点击【支出】按钮
        try:
            query_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div[2]/div/div[1]/div/div[3]/div/div[2]/div[2]/div/div[1]/div/div[2]/div[1]/div/label[2]'))
            )
            driver.execute_script("arguments[0].click();", query_button)
            print("✅ 已点击支出按钮")
            time.sleep(3)
        except Exception as e:
            print(f"⚠️ 点击支出按钮失败: {e}")
            print("   请手动点击支出按钮后按回车继续...")
            input()

        # 6. 点击【查询】按钮
        try:
            query_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div[2]/div/div[1]/div/div[3]/div/div[2]/div[2]/div/div[1]/div/div[1]/div[2]/button[1]'))
            )
            driver.execute_script("arguments[0].click();", query_button)
            print("✅ 已点击查询按钮")
            time.sleep(3)
        except Exception as e:
            print(f"⚠️ 点击查询按钮失败: {e}")
            print("   请手动点击查询按钮后按回车继续...")
            input()
        
        # 7. 设置每页显示100条
        try:
            print("📋 设置每页显示100条...")
            # 直接设置input的value为100
            page_size_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[2]/div/div[1]/div/div[3]/div/div[2]/div[2]/div/div[4]/div/ul/li[2]/div/div/div/div/div/div/div/div[1]/input'))
            )
            
            # 清空并设置新值
            driver.execute_script("arguments[0].value = '100';", page_size_input)
            
            # 触发change事件
            driver.execute_script("""
                var element = arguments[0];
                element.dispatchEvent(new Event('input', { bubbles: true }));
                element.dispatchEvent(new Event('change', { bubbles: true }));
            """, page_size_input)
            
            # 按回车确认
            from selenium.webdriver.common.keys import Keys
            page_size_input.send_keys(Keys.ENTER)
            
            print("✅ 已设置每页100条")
            time.sleep(3)
        except Exception as e:
            print(f"⚠️ 设置每页条数失败: {e}")
            print("   将使用默认条数继续...")
        
        # 8. 获取实际设置的日期范围
        actual_bill_date = None
        try:
            # 从时间输入框获取实际设置的日期
            time_input = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div/div[1]/div/div[3]/div/div[2]/div[2]/div/div[1]/div/div/div[1]/div/div/div/div/div/div[1]/input')
            date_range_value = time_input.get_attribute('value')
            
            if date_range_value:
                # 解析日期字符串，格式如: "2026-01-01 00:00:00 ~ 2026-01-01 23:59:59"
                date_str = date_range_value.split(' ')[0]  # 获取 "2026-01-01"
                actual_bill_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                print(f"📅 实际查询日期: {actual_bill_date}")
            else:
                # 如果获取不到，使用传入的日期
                actual_bill_date = date.fromtimestamp(begin_time)
                print(f"⚠️ 未能获取实际日期，使用默认日期: {actual_bill_date}")
        except Exception as e:
            # 如果获取失败，使用传入的日期
            actual_bill_date = date.fromtimestamp(begin_time)
            print(f"⚠️ 获取实际日期失败，使用默认日期: {actual_bill_date}")
        
        # 9. 循环翻页获取所有数据
        all_bill_details = []
        current_page = 1
        max_pages = 50  # 最多翻50页，防止无限循环
        
        print(f"\n📄 开始翻页获取数据...")
        
        while current_page <= max_pages:
            print(f"\n正在获取第 {current_page} 页数据...")
            time.sleep(3)  # 增加等待时间
            
            # 查找当前页的API响应
            found_page_data = False
            page_total = 0
            
            # 打印当前请求数量（调试用）
            print(f"   当前捕获的请求数: {len(driver.requests)}")
            
            for req in reversed(driver.requests):
                if not req.response:
                    continue
                    
                try:
                    if "pagingQueryMallBalanceBillListForMms" in req.url:
                        body = req.response.body
                        encoding = req.response.headers.get("Content-Encoding", "")
                        
                        if "gzip" in encoding:
                            body = gzip.GzipFile(fileobj=BytesIO(body)).read()
                        
                        data = json.loads(body.decode("utf-8"))
                        
                        if data.get("success"):
                            result = data.get("result", {})
                            bill_list = result.get("billList", [])
                            page_total = result.get("total", 0)
                            
                            if bill_list:
                                print(f"✅ 第 {current_page} 页: 获取到 {len(bill_list)} 条数据")
                                all_bill_details.extend(bill_list)
                                found_page_data = True
                                break  # 找到当前页数据，跳出 for 循环
                            else:
                                print(f"⚠️ 第 {current_page} 页没有数据")
                                break
                            
                except Exception as e:
                    continue
            
            if not found_page_data:
                print(f"⚠️ 未找到第 {current_page} 页的数据")
                
                # 如果是第一页就没找到，直接退出
                if current_page == 1:
                    break
                
                # 如果不是第一页，可能是网络延迟，再等待一下
                print(f"   等待 5 秒后重试...")
                time.sleep(5)
                
                # 再次尝试查找
                for req in reversed(driver.requests):
                    if not req.response:
                        continue
                    try:
                        if "pagingQueryMallBalanceBillListForMms" in req.url:
                            body = req.response.body
                            encoding = req.response.headers.get("Content-Encoding", "")
                            if "gzip" in encoding:
                                body = gzip.GzipFile(fileobj=BytesIO(body)).read()
                            data = json.loads(body.decode("utf-8"))
                            if data.get("success"):
                                result = data.get("result", {})
                                bill_list = result.get("billList", [])
                                if bill_list:
                                    print(f"✅ 重试成功: 第 {current_page} 页获取到 {len(bill_list)} 条数据")
                                    all_bill_details.extend(bill_list)
                                    found_page_data = True
                                    page_total = result.get("total", 0)
                                    break
                    except:
                        continue
                
                # 如果重试还是失败，退出循环
                if not found_page_data:
                    print(f"⚠️ 重试失败，停止翻页")
                    break
            
            # 检查是否还有下一页
            if len(all_bill_details) >= page_total:
                print(f"✅ 已获取全部数据，共 {len(all_bill_details)} 条（总计 {page_total} 条）")
                break
            
            # 点击下一页
            try:
                print(f"👉 尝试点击下一页...")
                
                # 方法1: 使用 data-testid 查找下一页按钮（最可靠）
                try:
                    next_button = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'li[data-testid="beast-core-pagination-next"]'))
                    )
                    print(f"   找到下一页按钮（方法1: data-testid）")
                except:
                    # 方法2: 使用 class 前缀查找
                    try:
                        next_button = driver.find_element(By.CSS_SELECTOR, 'li[class*="PGT_next_"]')
                        print(f"   找到下一页按钮（方法2: class）")
                    except:
                        # 方法3: 使用 arco-pagination（旧版本）
                        try:
                            next_button = driver.find_element(By.CSS_SELECTOR, 'li.arco-pagination-item-next:not(.arco-pagination-item-disabled) button')
                            print(f"   找到下一页按钮（方法3: arco）")
                        except:
                            raise Exception("未找到下一页按钮")
                
                # 检查按钮是否禁用
                button_class = next_button.get_attribute("class") or ""
                is_disabled = "disabled" in button_class.lower() or next_button.get_attribute("disabled")
                
                if is_disabled:
                    print(f"⚠️ 下一页按钮已禁用，已到最后一页")
                    break
                
                # 清空之前的请求，避免重复读取
                print(f"   清空旧请求...")
                del driver.requests
                
                # 点击按钮
                driver.execute_script("arguments[0].click();", next_button)
                print(f"✅ 已点击下一页")
                current_page += 1
                
                # 等待页面加载和API响应
                print(f"   等待页面加载...")
                time.sleep(5)  # 增加等待时间到5秒
                
            except Exception as e:
                print(f"⚠️ 没有下一页了或点击失败: {e}")
                import traceback
                traceback.print_exc()
                break
        
        print(f"\n{'='*60}")
        print(f"📊 数据获取完成: 共 {len(all_bill_details)} 条账单")
        print(f"{'='*60}\n")
        
        # 只查找账单明细API
        found_details = len(all_bill_details) > 0
        bill_details = all_bill_details
        
        # 如果找到明细数据，保存到数据库
        if found_details and bill_details:
            try:
                print(f"\n💾 开始处理 {len(bill_details)} 条账单数据...")
                
                # 先按订单号聚合金额（只统计负数，即退款）
                order_amounts = {}  # {order_sn: total_amount}
                total_bills = 0
                negative_bills = 0
                
                for bill in bill_details:
                    order_sn = bill.get("orderSn")
                    amount_fen = bill.get("amount", 0)
                    amount_yuan = amount_fen / 100.0
                    total_bills += 1
                    
                    # 只统计负数金额（退款）
                    if amount_yuan < 0:
                        negative_bills += 1
                        if order_sn in order_amounts:
                            order_amounts[order_sn] += amount_yuan
                        else:
                            order_amounts[order_sn] = amount_yuan
                
                print(f"📊 总账单: {total_bills} 条")
                print(f"📊 退款账单: {negative_bills} 条")
                print(f"📊 聚合后共 {len(order_amounts)} 个不同订单")
                
                # 保存到数据库 - 先删除旧数据，再插入新数据
                with database.atomic():
                    # 1. 删除该店铺该日期的所有旧记录
                    deleted_count = PddBillRecord.delete().where(
                        (PddBillRecord.shop_id == shop_id) &
                        (PddBillRecord.bill_date == actual_bill_date)
                    ).execute()
                    print(f"🗑️  删除时间为: {actual_bill_date} 的旧记录")
                    print(f"🗑️  删除旧记录: {deleted_count} 条")
                    
                    # 2. 插入新的聚合数据
                    saved_count = 0
                    error_count = 0
                    for order_sn, total_amount in order_amounts.items():
                        try:
                            PddBillRecord.create(
                                shop_id=shop_id,
                                order_sn=order_sn,
                                amount=total_amount,
                                bill_date=actual_bill_date
                            )
                            saved_count += 1
                        except Exception as e:
                            error_count += 1
                            print(f"❌ 保存失败: {order_sn} - {e}")
                            continue
                
                # 显示统计信息
                print(f"\n{'='*60}")
                print(f"💾 保存完成:")
                print(f"   🗑️  删除旧数据: {deleted_count} 条")
                print(f"   ✅ 新增数据: {saved_count} 条")
                print(f"   ❌ 失败: {error_count} 条")
                print(f"{'='*60}\n")
                
            except Exception as e:
                print(f"❌ 保存失败: {e}")
                import traceback
                traceback.print_exc()
        
        if not found_details:
            print("❌ 未找到账单明细API")
            print("   可能原因:")
            print("   1. 页面未正确加载")
            print("   2. 筛选条件未正确设置")
            print("   3. 查询按钮未成功点击")
            print("\n   请手动完成操作后按回车继续...")
            input()
            
            # 再次尝试查找
            for req in reversed(driver.requests):
                if req.response and "pagingQueryMallBalanceBillListForMms" in req.url:
                    try:
                        body = req.response.body
                        encoding = req.response.headers.get("Content-Encoding", "")
                        
                        if "gzip" in encoding:
                            body = gzip.GzipFile(fileobj=BytesIO(body)).read()
                        
                        data = json.loads(body.decode("utf-8"))
                        
                        if data.get("success"):
                            result = data.get("result", {})
                            bill_list = result.get("billList", [])
                            print(f"✅ 获取到 {len(bill_list)} 条账单明细")
                            bill_details = bill_list
                            found_details = True
                            
                            # 保存数据 - 按订单号聚合金额
                            if bill_details:
                                # 聚合相同订单号的金额
                                order_amounts = {}
                                for bill in bill_details:
                                    order_sn = bill.get("orderSn")
                                    amount_fen = bill.get("amount", 0)
                                    amount_yuan = amount_fen / 100.0
                                    
                                    if order_sn in order_amounts:
                                        order_amounts[order_sn] += amount_yuan
                                    else:
                                        order_amounts[order_sn] = amount_yuan
                                
                                print(f"📊 聚合后共 {len(order_amounts)} 个不同订单")
                                
                                # 先删除旧数据，再插入新数据
                                print(f'删除 时间为：{actual_bill_date} 的旧数据')
                                with database.atomic():
                                    # 删除该店铺该日期的所有旧记录
                                    deleted_count = PddBillRecord.delete().where(
                                        (PddBillRecord.shop_id == shop_id) &
                                        (PddBillRecord.bill_date == actual_bill_date)
                                    ).execute()
                                    print(f"🗑️  删除旧记录: {deleted_count} 条")
                                    
                                    # 插入新记录
                                    saved_count = 0
                                    for order_sn, total_amount in order_amounts.items():
                                        try:
                                            PddBillRecord.create(
                                                shop_id=shop_id,
                                                order_sn=order_sn,
                                                amount=total_amount,
                                                bill_date=actual_bill_date
                                            )
                                            saved_count += 1
                                        except:
                                            continue
                                    print(f"✅ 保存了 {saved_count} 条数据")
                            break
                            
                    except Exception as e:
                        continue
        
        if found_details:
            return True
        
        print("❌ 未找到账单数据")
        return False
        
    except Exception as e:
        print(f"❌ 获取账单数据失败: {e}")
        return False


# ===============================
# ===============================
# 1️⃣1️⃣ 主入口
# ===============================
if __name__ == "__main__":
    
    # 店铺配置
    SHOP_PROFILES = pdddata # 数据来自于 pdddata.py
    
    # 设置查询日期（默认昨天）
    target_date = datetime.now() - timedelta(days=1)
    
    # 计算时间戳（用于账单查询）
    begin_time = int(datetime(target_date.year, target_date.month, target_date.day).timestamp())
    end_time = int(datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59).timestamp())
    
    for shop in SHOP_PROFILES:
        shop_id = shop.get("shopid", "")
        shop_name = shop.get("shopname", "")
        username = shop.get("username", "")
        password = shop.get("password", "")
        
        print(f"\n{'='*60}")
        print(f"🚀 处理店铺: {shop_name} (ID: {shop_id})")
        print(f"{'='*60}")
        
        driver = create_driver(shop_id)
        
        try:
            # 1. 登录（wait_for_login内部已包含清除cookies和强制退出的逻辑）
            wait_for_login(driver, username=username, password=password)
            
            # 2. 进入推广页面
            wait_promotion_page_ready(driver)
            
            # 3. 选择日期（返回用户实际选择的日期，内部已包含确认步骤）
            selected_date = select_date_range(driver, target_date)
            
            # 4. 爬取推广数据
            data = crawl_from_current_page(driver)
            print(f"\n🎉 抓取完成，共 {len(data)} 条 promotion 数据")
            
            # 5. 保存到数据库（传递日期参数）
            if data:
                save_promotion_to_db(data, store_id=shop_id, data_date=selected_date)
            
            # 6. 获取账单数据
            get_bill_outcome_amount(
                driver, 
                shop_id=shop_id,
                begin_time=begin_time, 
                end_time=end_time
            )
            
        except Exception as e:
            print(f"❌ 处理失败: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            driver.quit()
            print(f"\n✅ 店铺 {shop_name} 处理完成\n")





