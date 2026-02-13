import time
from datetime import datetime, timedelta
import json
import gzip
from io import BytesIO
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import os

# 添加父目录到路径以导入数据库模型
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.database import PddTable, PddBillRecord, database


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
# 3️⃣ 选择日期范围
# ===============================
def select_date_range(driver, target_date=None):
    """
    在推广页面选择日期
    target_date: datetime对象，默认为昨天
    """
    if target_date is None:
        target_date = datetime.now() - timedelta(days=1)
    
    print(f"📅 选择日期: {target_date.strftime('%Y-%m-%d')}")
    
    try:
        # 等待日期选择器出现
        date_picker = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".anq-picker-input"))
        )
        
        # 点击日期选择器
        driver.execute_script("arguments[0].click();", date_picker)
        time.sleep(1)
        
        # 查找并点击目标日期
        # 这里需要根据实际页面结构调整选择器
        date_cells = driver.find_elements(By.CSS_SELECTOR, ".anq-picker-cell")
        target_day = target_date.day
        
        for cell in date_cells:
            if cell.text == str(target_day):
                driver.execute_script("arguments[0].click();", cell)
                time.sleep(1)
                break
        
        print(f"✅ 日期已选择: {target_date.strftime('%Y-%m-%d')}")
        time.sleep(2)
        
    except Exception as e:
        print(f"⚠️ 日期选择失败: {e}")
        print("请手动选择日期后按回车继续...")
        input()


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
def save_promotion_to_db(items):
    """
    将推广数据保存到PddTable
    """
    if not items:
        print("⚠️ 没有数据需要保存")
        return 0
    
    saved_count = 0
    updated_count = 0
    
    with database.atomic():
        for item in items:
            try:
                # 提取报表数据
                report = item.get("report", {})
                
                # 辅助函数：安全转换数值
                def safe_float(value, default=0.0):
                    if value is None:
                        return default
                    if isinstance(value, (int, float)):
                        return float(value)
                    if isinstance(value, str):
                        try:
                            return float(value)
                        except:
                            return default
                    return default
                
                def safe_int(value, default=0):
                    if value is None:
                        return default
                    if isinstance(value, int):
                        return value
                    if isinstance(value, (float, str)):
                        try:
                            return int(value)
                        except:
                            return default
                    return default
                
                # 准备数据
                data = {
                    "ad_id": str(item.get("adId")),
                    "ad_name": item.get("adName"),
                    "goods_id": str(item.get("goodsId")) if item.get("goodsId") else None,
                    "store_id": store_id,
                    "goods_name": item.get("goodsName"),
                    "orderSpendNetCostPerOrder": item.get("reportInfo").get("orderSpendNetCostPerOrder"),
                    
                    # 原始数据
                    "raw_data": json.dumps(item, ensure_ascii=False),
                    "updated_at": datetime.now()
                }
                
                # 尝试更新或创建
                existing = PddTable.get_or_none(PddTable.ad_id == data["ad_id"])
                
                if existing:
                    # 更新现有记录
                    for key, value in data.items():
                        setattr(existing, key, value)
                    existing.save()
                    updated_count += 1
                else:
                    # 创建新记录
                    PddTable.create(**data)
                    saved_count += 1
                    
            except Exception as e:
                print(f"❌ 保存数据失败: {e}")
                print(f"   数据: {item.get('adId')}")
                # 打印问题字段用于调试
                import traceback
                traceback.print_exc()
                continue
    
    print(f"✅ 数据保存完成: 新增 {saved_count} 条, 更新 {updated_count} 条")
    return saved_count + updated_count


# ===============================
# 🔟 访问账单页面并获取退款金额
# ===============================
def get_bill_outcome_amount(driver, begin_time, end_time):
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
            
            # 使用JavaScript直接设置value属性
            driver.execute_script(f"arguments[0].value = '{date_range_value}';", time_input)
            
            # 触发change事件，让页面识别到值的变化
            driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", time_input)
            driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", time_input)
            
            print(f"✅ 时间范围已设置: {date_range_value}")
            time.sleep(1)
        except Exception as e:
            print(f"⚠️ 设置时间范围失败: {e}")
            print("   请手动操作后按回车继续...")
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
        
        # 5. 点击【查询】按钮
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
        
        # 等待API请求
        print("⏳ 等待账单API响应...")
        time.sleep(3)
        
        # 从请求中查找账单统计数据和明细数据
        found_statistics = False
        found_details = False
        outcome_amount = 0
        statistics_data = None
        bill_details = []
        
        # 查找两个API请求
        for req in reversed(driver.requests):
            if not req.response:
                continue
                
            try:
                body = req.response.body
                encoding = req.response.headers.get("Content-Encoding", "")
                
                if "gzip" in encoding:
                    body = gzip.GzipFile(fileobj=BytesIO(body)).read()
                
                data = json.loads(body.decode("utf-8"))
                
                # 1. 查找账单统计API
                if "queryBillStatistics" in req.url and data.get("success"):
                    found_statistics = True
                    print(f"✅ 找到账单统计API: {req.url}")
                    result = data.get("result", {})
                    outcome_amount = result.get("outcomeAmount", 0)
                    statistics_data = data
                    print(f"✅ 获取到退款金额: {outcome_amount / 100:.2f} 元")
                
                # 2. 查找账单明细API
                if "pagingQueryMallBalanceBillListForMms" in req.url and data.get("success"):
                    found_details = True
                    print(f"✅ 找到账单明细API: {req.url}")
                    result = data.get("result", {})
                    bill_list = result.get("billList", [])
                    print(f"✅ 获取到 {len(bill_list)} 条账单明细")
                    bill_details = bill_list
                    
            except Exception as e:
                continue
        
        # 如果找到明细数据，保存到数据库
        if found_details and bill_details:
            try:
                from backend.models.database import PddBillDetail, database
                from datetime import datetime, date
                
                saved_count = 0
                with database.atomic():
                    for bill in bill_details:
                        try:
                            # 检查是否已存在
                            existing = PddBillDetail.select().where(
                                PddBillDetail.bill_id == bill.get("billId")
                            ).first()
                            
                            if existing:
                                print(f"⚠️ 账单 {bill.get('billId')} 已存在，跳过")
                                continue
                            
                            # 创建新记录
                            amount_fen = bill.get("amount", 0)
                            amount_yuan = amount_fen / 100.0
                            
                            PddBillDetail.create(
                                bill_id=bill.get("billId"),
                                mall_id=bill.get("mallId"),
                                order_sn=bill.get("orderSn"),
                                amount=amount_fen,
                                amount_yuan=amount_yuan,
                                created_at_timestamp=bill.get("createdAt"),
                                bill_type=bill.get("type"),
                                class_id=bill.get("classId"),
                                class_id_desc=bill.get("classIdDesc"),
                                finance_id=bill.get("financeId"),
                                finance_id_desc=bill.get("financeIdDesc"),
                                note=bill.get("note"),
                                bill_out_biz_code=bill.get("billOutBizCode"),
                                bill_out_biz_desc=bill.get("billOutBizDesc"),
                                bill_biz_code=bill.get("billBizCode"),
                                shop_profile=profile_name,
                                bill_date=date.fromtimestamp(start_timestamp),
                                raw_data=json.dumps(bill, ensure_ascii=False)
                            )
                            saved_count += 1
                            print(f"✅ 保存账单: {bill.get('orderSn')} - {amount_yuan:.2f}元")
                            
                        except Exception as e:
                            print(f"⚠️ 保存账单失败: {e}")
                            continue
                
                print(f"✅ 成功保存 {saved_count} 条账单明细到数据库")
                
            except Exception as e:
                print(f"⚠️ 保存账单明细到数据库失败: {e}")
                import traceback
                traceback.print_exc()
        
        if not found_statistics and not found_details:
            print("❌ 未找到账单API请求")
            print("   可能原因:")
            print("   1. 页面未正确加载")
            print("   2. 筛选条件未正确设置")
            print("   3. 查询按钮未成功点击")
            print("\n   请手动完成操作后按回车继续...")
            input()
            
            # 再次尝试查找
            for req in reversed(driver.requests):
                if req.response and "queryBillStatistics" in req.url:
                    try:
                        body = req.response.body
                        encoding = req.response.headers.get("Content-Encoding", "")
                        
                        if "gzip" in encoding:
                            body = gzip.GzipFile(fileobj=BytesIO(body)).read()
                        
                        data = json.loads(body.decode("utf-8"))
                        
                        if data.get("success"):
                            result = data.get("result", {})
                            outcome_amount = result.get("outcomeAmount", 0)
                            statistics_data = data
                            print(f"✅ 获取到退款金额: {outcome_amount / 100:.2f} 元")
                            break
                            
                    except Exception as e:
                        continue
        
        if found_statistics or found_details:
            return outcome_amount / 100, statistics_data
        
        print("❌ 未找到账单统计数据")
        return None, None
        
    except Exception as e:
        print(f"❌ 获取账单数据失败: {e}")
        return None, None


# ===============================
# 1️⃣1️⃣ 保存账单数据到数据库
# ===============================
def save_bill_to_db(shop_profile, bill_date, outcome_amount, begin_time, end_time, raw_data):
    """
    保存账单数据到数据库
    """
    try:
        with database.atomic():
            # 尝试查找现有记录
            existing = PddBillRecord.get_or_none(
                (PddBillRecord.shop_profile == shop_profile) &
                (PddBillRecord.bill_date == bill_date)
            )
            
            if existing:
                # 更新现有记录
                existing.outcome_amount = outcome_amount
                existing.begin_time = begin_time
                existing.end_time = end_time
                existing.raw_data = json.dumps(raw_data, ensure_ascii=False) if raw_data else None
                existing.updated_at = datetime.now()
                existing.save()
                print(f"✅ 账单数据已更新")
            else:
                # 创建新记录
                PddBillRecord.create(
                    shop_profile=shop_profile,
                    bill_date=bill_date,
                    outcome_amount=outcome_amount,
                    begin_time=begin_time,
                    end_time=end_time,
                    raw_data=json.dumps(raw_data, ensure_ascii=False) if raw_data else None
                )
                print(f"✅ 账单数据已保存")
                
        return True
        
    except Exception as e:
        print(f"❌ 保存账单数据失败: {e}")
        import traceback
        traceback.print_exc()
        return False


# ===============================
# 1️⃣1️⃣ 主入口
# ===============================
if __name__ == "__main__":
    
    SHOP_PROFILES = [
        "19250015",
    ]
    
    # 设置查询日期（默认昨天）
    target_date = datetime.now() - timedelta(days=1)
    
    # 计算时间戳（用于账单查询）
    begin_time = int(datetime(target_date.year, target_date.month, target_date.day).timestamp())
    end_time = int(datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59).timestamp())
    
    for shop in SHOP_PROFILES:
        print(f"\n🚀 处理店铺 {shop}")
        driver = create_driver(shop)
        
        try:
            # 1. 登录
            wait_for_login(driver)
            
            # 2. 进入推广页面
            wait_promotion_page_ready(driver)
            
            # # 3. 选择日期
            # select_date_range(driver, target_date)
            
            # # 4. 爬取推广数据
            # print("\n👉 确认日期选择正确后按回车开始抓取...")
            # input()
            
            # data = crawl_from_current_page(driver)
            # print(f"\n🎉 抓取完成，共 {len(data)} 条 promotion 数据")
            
            # # 5. 保存到数据库
            # if data:
            #     save_promotion_to_db(data)
            
            # 6. 获取账单退款金额
            outcome_amount, raw_data = get_bill_outcome_amount(driver, begin_time, end_time)
            
            if outcome_amount is not None:
                print(f"\n📊 {target_date.strftime('%Y-%m-%d')} 退款金额: {outcome_amount:.2f} 元")
                
                # 保存账单数据到数据库
                save_bill_to_db(
                    shop_profile=shop,
                    bill_date=target_date.date(),
                    outcome_amount=outcome_amount,
                    begin_time=begin_time,
                    end_time=end_time,
                    raw_data=raw_data
                )
            
        except Exception as e:
            print(f"❌ 处理失败: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            driver.quit()





