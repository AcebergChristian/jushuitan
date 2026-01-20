from ast import Dict
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException

import time
import json
from dataclasses import dataclass
from typing import List, Optional
import re
import hashlib
from datetime import datetime, timedelta
import sys
import os


# 添加项目根目录到系统路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from backend.utils.datatodb import DataToDB
except ImportError:
    # 如果直接导入失败，尝试另一种方式
    import importlib.util
    datatodb_path = os.path.join(project_root, 'utils', 'datatodb.py')  # 修正路径，不需要重复backend
    spec = importlib.util.spec_from_file_location("datatodb", datatodb_path)
    datatodb_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(datatodb_module)
    DataToDB = datatodb_module.DataToDB


@dataclass
class ProductInfo:
    """商品信息数据类"""
    goods_id: str
    name: str
    price: float
    stock: int
    order_number: Optional[str] = None  # 订单号
    online_order_number: Optional[str] = None  # 线上订单号
    shop_name: Optional[str] = None  # 店铺名称
    label: Optional[str] = None  # 标签
    buyer_nickname: Optional[str] = None  # 买家昵称
    supplier: Optional[str] = None  # 供应商
    purchase_amount: Optional[float] = None  # 采购金额
    status: Optional[str] = None  # 状态
    shipping_company: Optional[str] = None  # 快递公司
    solution: Optional[str] = None  # 解决方案
    distributor_push_time: Optional[str] = None  # 分销商推单时间
    customer_quantity: Optional[int] = None  # 客户下单数量
    customer_amount: Optional[float] = None  # 客户下单金额
    weight: Optional[float] = None  # 重量
    actual_weight: Optional[float] = None  # 实际称重重量
    buyer_message: Optional[str] = None  # 买家留言
    seller_remark: Optional[str] = None  # 卖家备注
    offline_remark: Optional[str] = None  # 线下备注
    placing_time: Optional[str] = None  # 下单时间
    payment_time: Optional[str] = None  # 付款时间
    shipping_time: Optional[str] = None  # 发货时间
    distributor: Optional[str] = None  # 分销商
    shipping_warehouse: Optional[str] = None  # 发货仓库
    description: Optional[str] = None
    image_url: Optional[str] = None
    platform: str = ""  # 平台标识：jushuitan 或 pinduoduo

class SeleniumCrawler:
    def __init__(self):
        # 配置Chrome选项
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        # 如果不需要显示浏览器，取消下面一行的注释
        # chrome_options.add_argument("--headless")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)

        ######### 元素初始化 登录之外的 #########
        # 前一日时间
        self.starttime_ele = "#supplierManageQuery_time > span > div.antd-pro-components-query-widgets-select-component-index-right > div > span > div.ant-picker.antd-pro-components-query-widgets-range-date-picker-v2-index-leftPicker > div > input"
        self.endtime_ele = "#supplierManageQuery_time > span > div.antd-pro-components-query-widgets-select-component-index-right > div > span > div.ant-picker.antd-pro-components-query-widgets-range-date-picker-v2-index-rightPicker > div > input"
        
        # 日期确定按钮
        self.startdate_confirm_btn = "#real-root > div:nth-child(3) > div > div > div > div > div.ant-picker-footer > ul > li > button"
        self.enddate_confirm_btn = "#real-root > div:nth-child(4) > div > div > div > div > div.ant-picker-footer > ul > li > button"
        # 查询按钮
        self.serch_btn = "#supplierManageQuery_queryFilter > div:nth-child(3) > div > div:nth-child(2) > div > div.ant-space.ant-space-horizontal.ant-space-align-center.antd-pro-components-query-filter-with-config-index-right > div:nth-child(1) > button"

        # 总数据条数的selector
        self.total_count_selector = '#channelOrder-table-wrap > div:nth-child(3) > div.antd-pro-components-antd-base-table-index-stickyFootBar > div.antd-pro-components-antd-base-table-index-rt > ul > li.ant-pagination-total-text'

        # 下一页
        self.nextpage = "#channelOrder-table-wrap > div:nth-child(3) > div.antd-pro-components-antd-base-table-index-stickyFootBar > div.antd-pro-components-antd-base-table-index-rt > ul > li.ant-pagination-next > button"

        # 滚动容器的selector
        self.tbody_selector = '#channelOrder-table-wrap > div:nth-child(3) > div.react-contextmenu-wrapper > div > div > div > div.art-table > div.art-table-body.art-horizontal-scroll-container > table > tbody'

        # 取消btn
        self.cancelled_btn = "#supplierManageQuery_queryFilter > div.antd-pro-components-query-filter-with-config-index-queryFilter.antd-pro-components-query-filter-with-config-index-topNoCollapsedStyles.antd-pro-components-query-filter-with-config-index-normalVerticalSize > div > div:nth-child(2) > div > div > div > div > div > div:nth-child(8)"


    def login(self):
        """登录聚水潭系统"""
        self.driver.get("https://sc.scm121.com/login")
        
        # 这里需要根据实际登录页面填写用户名和密码
        username_input = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
        password_input = self.driver.find_element(By.ID, "password")
        checkbox = self.driver.find_element(By.CSS_SELECTOR, "#real-root > section > main > div > div > div > form > div.antd-pro-pages-account-styles-index-container > div.antd-pro-pages-account-components-agreement-checked-index-remember > label > span.ant-checkbox > input")
        login_button = self.driver.find_element(By.CSS_SELECTOR, "#real-root > section > main > div > div > div > form > div.antd-pro-pages-account-login-style-submit > button")
        
        # 填入您的登录凭据
        username_input.send_keys("17607992526")
        password_input.send_keys("Aa12345600.")
        checkbox.click()
        login_button.click()
        
        # 等待登录完成
        self.wait.until(EC.url_changes("https://sc.scm121.com/login"))
        time.sleep(3)  # 额外等待页面完全加载

    def get_yesterday(self):
        """获取昨天的00点到今天的00点的数据"""
        
        # 获取昨天的日期
        yesterday_start = datetime.combine(datetime.now().date() - timedelta(days=21), datetime.min.time())
        today_start = datetime.combine(datetime.now().date() - timedelta(days=20), datetime.min.time())
        # today_start = datetime.combine(datetime.now().date(), datetime.min.time())
        
        # 格式化为字符串（根据API需要的格式调整）
        start_time = yesterday_start.strftime('%Y-%m-%d %H:%M:%S')
        end_time = today_start.strftime('%Y-%m-%d %H:%M:%S')
        
        return start_time, end_time

    def set_date_range(self, start_time: str, end_time: str):
        """
        聚水潭新版 Ant Design DatePicker 专用设置日期方法
        start_time / end_time 格式必须是：YYYY-MM-DD 或 YYYY-MM-DD HH:mm:ss
        """
        wait = WebDriverWait(self.driver, 10)

        # 1. 找到两个输入框（一定等可点击）
        start_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.starttime_ele)))
        end_input   = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.endtime_ele)))

        # 2. 清空 + 输入开始日期（推荐方式）
        start_input.click()
        start_input.send_keys(Keys.CONTROL + "a")   # 全选
        start_input.send_keys(Keys.DELETE)         # 删除
        start_input.send_keys(start_time)          # 输入新日期
        start_input.send_keys(Keys.ENTER)          # 直接回车确认（最关键！）

        # 3. 同理处理结束日期
        end_input.click()
        end_input.send_keys(Keys.CONTROL + "a")
        end_input.send_keys(Keys.DELETE)
        end_input.send_keys(end_time)
        end_input.send_keys(Keys.ENTER)            # 回车确认

        # 4. 再加个小小的等待，确保请求发出（聚水潭会自动触发搜索）
        time.sleep(1)

    def click_search_button(self):
        """点击查询按钮"""
        query_button = self.driver.find_element(By.CSS_SELECTOR, self.serch_btn)
        query_button.click()
        time.sleep(3)  # 等待查询结果加载

    def switch_to_iframe(self):
        """切换到iframe（如果存在）"""
        try:
            iframe = self.wait.until(EC.presence_of_element_located((By.ID, "tradeManage1")))
            self.driver.switch_to.frame(iframe)
            print("已切换到iframe")
        except:
            print("未找到iframe，继续在主页面操作")

    def get_scroll_container(self, tbody_selector):
        """获取滚动容器"""
        scroll_containers = [
            self.driver.find_element(By.CSS_SELECTOR, ".art-table-body"),
            self.driver.find_element(By.CSS_SELECTOR, ".art-horizontal-scroll-container"),
            self.driver.find_element(By.CSS_SELECTOR, "#channelOrder-table-wrap .art-table-body")
        ]
        
        scroll_container = None
        for container in scroll_containers:
            try:
                if container.size['height'] < container.get_property('scrollHeight'):
                    scroll_container = container
                    break
            except:
                continue
        
        if not scroll_container:
            # 尝试通过JavaScript找到滚动容器
            scroll_container = self.driver.execute_script("""
                const selectors = [
                    '.art-table-body',
                    '.art-horizontal-scroll-container',
                    '#channelOrder-table-wrap .art-table-body'
                ];
                
                for (let selector of selectors) {
                    const element = document.querySelector(selector);
                    if (element && element.scrollHeight > element.clientHeight) {
                        return element;
                    }
                }
                
                // 如果以上都没找到，尝试tbody的父元素
                const tbody = document.querySelector(arguments[0]);
                if (tbody) {
                    let parent = tbody.parentElement;
                    while (parent && parent !== document.body) {
                        if (parent.scrollHeight > parent.clientHeight) {
                            return parent;
                        }
                        parent = parent.parentElement;
                    }
                }
                return null;
            """, tbody_selector)
        
        return scroll_container


    # 滚动获取tr数据并解析到list
    def scroll_and_parse_data(self, tbody_selector, max_scrolls=200):
        scroll_container = self.get_scroll_container(tbody_selector)
        if not scroll_container:
            return []

        parsed = {}
        STEP = 300  # 小步长，接近一行高度
        last_scroll_top = -1

        for _ in range(max_scrolls):
            rows = self.driver.find_elements(By.CSS_SELECTOR, f"{tbody_selector} tr")

            for row in rows:
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    product = self.parse_product_data(cells)
                    if not product:
                        continue

                    # 🔥 行级唯一 key（不依赖业务字段）
                    row_text = "|".join(c.text for c in cells)
                    row_key = hashlib.md5(row_text.encode("utf-8")).hexdigest()
                    parsed[row_key] = product

                except Exception:
                    continue

            scroll_top = self.driver.execute_script(
                "return arguments[0].scrollTop", scroll_container
            )
            scroll_height = self.driver.execute_script(
                "return arguments[0].scrollHeight", scroll_container
            )
            client_height = self.driver.execute_script(
                "return arguments[0].clientHeight", scroll_container
            )

            if scroll_top >= scroll_height - client_height - 5:
                break

            if scroll_top == last_scroll_top:
                break
            last_scroll_top = scroll_top

            self.driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollTop + arguments[1];",
                scroll_container,
                STEP
            )
            time.sleep(0.3)

        return list(parsed.values())

    def navigate_to_page(self):
        """导航到目标页面"""
        self.driver.get("https://sc.scm121.com/tradeManage/tower/distribute")
        time.sleep(5)  # 等待页面加载

    def get_total_count(self):
        """获取总记录数和总页数"""
        # 正则提取这个selector里的数字
        total_count_element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.total_count_selector)))
        total_count_text = total_count_element.text
        
        # 使用正则表达式提取文本中的数字
        match = re.search(r'(\d+)', total_count_text)
        if match:
            total_count = int(match.group(1))
        else:
            total_count = 0  # 如果没有找到数字，则默认为0
        
        # 计算总页数，每页50条记录
        items_per_page = 50
        if total_count == 0:
            total_pages = 1  # 当总数为0时，显示1页
        elif total_count <= items_per_page:
            total_pages = 1  # 当总数小于等于每页数量时，显示1页
        else:
            total_pages = (total_count + items_per_page - 1) // items_per_page  # 向上取整
        
        return total_count, total_pages

    def click_next_page(self):
        """点击下一页"""
        try:
            next_page_btn = self.driver.find_element(By.CSS_SELECTOR, self.nextpage)
            if next_page_btn.is_enabled():
                next_page_btn.click()
                time.sleep(3)  # 等待下一页数据加载
                
                # 页面加载后，将tbody滚动到最上面
                try:
                    # 获取tbody元素
                    tbody_element = self.driver.find_element(By.CSS_SELECTOR, self.tbody_selector)
                    
                    # 获取对应的滚动容器
                    scroll_container = self.get_scroll_container(self.tbody_selector)
                    
                    if scroll_container:
                        # 将滚动容器滚动到顶部
                        self.driver.execute_script("arguments[0].scrollTop = 0;", scroll_container)
                        print("已将滚动容器滚动到顶部")
                    else:
                        print("未找到滚动容器，无法滚动到顶部")
                        
                except Exception as scroll_error:
                    print(f"滚动到顶部时出错: {scroll_error}")
                
                return True
            else:
                print("已经是最后一页")
                return False
        except:
            print("找不到下一页按钮或已是最后一页")
            return False

    def get_all_paginated_data(self, tbody_selector):
        all_products = {}

        total_count, total_pages = self.get_total_count()
        print(f"总记录数: {total_count}, 总页数: {total_pages}")

        for page in range(1, total_pages + 1):
            page_products = self.scroll_and_parse_data(tbody_selector)

            for p in page_products:
                all_products[p.order_number] = p

            print(f"第 {page} 页累计 {len(all_products)} 条")

            if page < total_pages:
                self.click_next_page()
                self.switch_to_iframe()
                time.sleep(2)

        return list(all_products.values())

    def parse_product_data(self, cell_texts):
        """解析单行产品数据"""
        if len(cell_texts) < 5:  # 确保有足够的列
            return None
            
        cell_texts = [cell.text.strip() for cell in cell_texts]
        
        # 根据表格列的定义映射数据
        order_number = cell_texts[1] if len(cell_texts) > 1 else ""
        online_order_number = cell_texts[2] if len(cell_texts) > 2 else ""
        shop_name = cell_texts[3] if len(cell_texts) > 3 else ""
        label = cell_texts[4] if len(cell_texts) > 4 else ""
        name_candidate = cell_texts[5] if len(cell_texts) > 5 else ""
        buyer_nickname = cell_texts[6] if len(cell_texts) > 6 else ""
        supplier = cell_texts[7] if len(cell_texts) > 7 else ""
        purchase_amount_candidate = cell_texts[8] if len(cell_texts) > 8 else ""
        status = cell_texts[9] if len(cell_texts) > 9 else ""
        shipping_company = cell_texts[10] if len(cell_texts) > 10 else ""
        solution = cell_texts[11] if len(cell_texts) > 11 else ""
        distributor_push_time = cell_texts[12] if len(cell_texts) > 12 else ""
        customer_quantity_candidate = cell_texts[20] if len(cell_texts) > 20 else ""  # 索引21
        customer_amount_candidate = cell_texts[21] if len(cell_texts) > 21 else ""   # 索引22
        weight_candidate = cell_texts[23] if len(cell_texts) > 23 else ""           # 索引24
        actual_weight_candidate = cell_texts[24] if len(cell_texts) > 24 else ""    # 索引25
        buyer_message = cell_texts[27] if len(cell_texts) > 27 else ""             # 索引28
        seller_remark = cell_texts[28] if len(cell_texts) > 28 else ""             # 索引29
        offline_remark = cell_texts[29] if len(cell_texts) > 29 else ""            # 索引30
        placing_time = cell_texts[30] if len(cell_texts) > 30 else ""              # 索引31
        payment_time = cell_texts[31] if len(cell_texts) > 31 else ""              # 索引32
        shipping_time = cell_texts[32] if len(cell_texts) > 32 else ""             # 索引33
        distributor = cell_texts[33] if len(cell_texts) > 33 else ""               # 索引34
        shipping_warehouse = cell_texts[34] if len(cell_texts) > 34 else ""        # 索引35
        
        # 解析数值
        purchase_amount_match = re.search(r'[\d,]+\.?\d*', purchase_amount_candidate.replace(',', ''))
        purchase_amount = float(purchase_amount_match.group()) if purchase_amount_match else 0.0
        
        customer_amount_match = re.search(r'[\d,]+\.?\d*', customer_amount_candidate.replace(',', ''))
        customer_amount = float(customer_amount_match.group()) if customer_amount_match else 0.0
        
        customer_quantity_match = re.search(r'\d+', customer_quantity_candidate)
        customer_quantity = int(customer_quantity_match.group()) if customer_quantity_match else 0
        
        weight_match = re.search(r'[\d.]+', weight_candidate)
        weight = float(weight_match.group()) if weight_match else 0.0
        
        actual_weight_match = re.search(r'[\d.]+', actual_weight_candidate)
        actual_weight = float(actual_weight_match.group()) if actual_weight_match else 0.0
        
        # 解析商品名称和ID
        goods_id = ""
        name = name_candidate
        
        if '-' in name_candidate:
            parts = name_candidate.split('-', 1)
            if len(parts) == 2:
                goods_id = parts[0].strip()
                name = parts[1].strip()
        
        # 创建产品对象
        product = ProductInfo(
            goods_id=goods_id,
            name=name,
            price=purchase_amount,
            stock=customer_quantity,
            order_number=order_number,
            online_order_number=online_order_number,
            shop_name=shop_name,
            label=label,
            buyer_nickname=buyer_nickname,
            supplier=supplier,
            purchase_amount=purchase_amount,
            status=status,
            shipping_company=shipping_company,
            solution=solution,
            distributor_push_time=distributor_push_time,
            customer_quantity=customer_quantity,
            customer_amount=customer_amount,
            weight=weight,
            actual_weight=actual_weight,
            buyer_message=buyer_message,
            seller_remark=seller_remark,
            offline_remark=offline_remark,
            placing_time=placing_time,
            payment_time=payment_time,
            shipping_time=shipping_time,
            distributor=distributor,
            shipping_warehouse=shipping_warehouse,
            platform="jushuitan"
        )
        
        return product

    def process_regular_orders(self):
        print("开始获取常规订单数据...")

        self.navigate_to_page()
        time.sleep(5)
        self.switch_to_iframe()

        start_time, end_time = self.get_yesterday()
        print(f"时间范围: {start_time} 到 {end_time}")
        self.set_date_range(start_time, end_time)
        self.click_search_button()

        # 🔥 现在这里直接拿到的就是 ProductInfo 列表
        products = self.get_all_paginated_data(self.tbody_selector)

        print(f"常规订单数据解析完成，共 {len(products)} 条")
        return products

    def process_return_orders(self):
        """处理退货订单数据"""
        print("开始获取退货订单数据...")

        self.navigate_to_page()
        time.sleep(5)
        self.switch_to_iframe()
        
        # 点击"已取消"按钮（这里需要根据实际页面结构调整选择器
        try:
            cancelled_btn = self.driver.find_element(By.CSS_SELECTOR, self.cancelled_btn)
            # 这里需要替换为实际的选择器
            cancelled_btn.click()
            time.sleep(2)
        except:
            print("未找到'已取消'按钮，跳过此步骤")

        # 获取前一日的时间，并设置到时间选择器中
        start_time, end_time = self.get_yesterday()
        self.set_date_range(start_time, end_time)
        
        # 点击查询按钮
        self.click_search_button()
        
        # 获取所有分页数据
        products = self.get_all_paginated_data(self.tbody_selector)
        
        print(f"退货订单数据解析完成，共 {len(products)} 条")
        return products

    def get_products(self):
        """获取商品列表 - 主入口方法"""

        # 获取常规订单数据
        regular_products = self.process_regular_orders()
        
        # 获取退货订单数据
        return_products = self.process_return_orders()
        
        # 合并所有数据
        all_products = {
            'regular_products' : regular_products,
            'return_products' : return_products
        }

        return all_products, len(regular_products), len(return_products)

    def close(self):
        """关闭浏览器"""
        self.driver.quit()

# 使用示例
if __name__ == "__main__":
    time1 = time.time()
    crawler = SeleniumCrawler()
    try:
        crawler.login()
        products, regular_total, return_total = crawler.get_products()
        print(f"jushuitan 平台商品数量: {regular_total}, 被取消商品数量: {return_total}")
        db_manager = DataToDB()
    

        # 插入数据库
        db_manager = DataToDB()
        db_manager.insert_jushuitan_data(products)

        print("数据插入完成", time.time() - time1)
    
    except Exception as e:
        print(f"发生错误: {e}")

    finally:
        crawler.close()


