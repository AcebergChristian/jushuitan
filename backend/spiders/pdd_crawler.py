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
import requests


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
    # 拼多多推广相关字段
    promotion_status: Optional[str] = None  # 推广状态
    budget_bidding: Optional[str] = None  # 预算及出价
    total_cost: Optional[float] = None  # 总花费(元)
    transaction_cost: Optional[float] = None  # 成交花费(元)
    actual_transaction_cost: Optional[float] = None  # 实际成交花费(元)
    transaction_amount: Optional[float] = None  # 交易额(元)
    actual_roi: Optional[float] = None  # 实际投产比
    exposure: Optional[int] = None  # 曝光量
    net_transaction_amount: Optional[float] = None  # 净交易额(元)
    net_actual_roi: Optional[float] = None  # 净实际投产比
    net_transaction_count: Optional[int] = None  # 净成交笔数
    cost_per_net_transaction: Optional[float] = None  # 每笔净成交花费(元)
    net_transaction_ratio: Optional[float] = None  # 净交易额占比
    settlement_amount: Optional[float] = None  # 结算金额(元)
    settlement_roi: Optional[float] = None  # 结算投产比
    settlement_count: Optional[int] = None  # 结算笔数
    refund_rate: Optional[float] = None  # 退款率
    refund_order_rate: Optional[float] = None  # 退单率
    refund_exemption_rate: Optional[float] = None  # 退款豁免率
    refund_order_exemption_rate: Optional[float] = None  # 退单豁免率
    transaction_settlement_rate: Optional[float] = None  # 交易额结算率
    order_settlement_rate: Optional[float] = None  # 订单结算率
    settlement_order_cost: Optional[float] = None  # 结算订单成本(元)
    transaction_count: Optional[int] = None  # 成交笔数
    cost_per_transaction: Optional[float] = None  # 每笔成交花费(元)
    amount_per_transaction: Optional[float] = None  # 每笔成交金额(元)
    direct_transaction_amount: Optional[float] = None  # 直接交易额(元)
    indirect_transaction_amount: Optional[float] = None  # 间接交易额(元)
    direct_transaction_count: Optional[int] = None  # 直接成交笔数
    indirect_transaction_count: Optional[int] = None  # 间接成交笔数
    amount_per_direct_transaction: Optional[float] = None  # 每笔直接成交金额(元)
    amount_per_indirect_transaction: Optional[float] = None  # 每笔间接成交金额(元)
    clicks: Optional[int] = None  # 点击量
    inquiry_cost: Optional[float] = None  # 询单花费(元)
    inquiries: Optional[int] = None  # 询单量
    avg_inquiry_cost: Optional[float] = None  # 平均询单成本(元)
    favorite_cost: Optional[float] = None  # 收藏花费(元)
    favorites: Optional[int] = None  # 收藏量
    avg_favorite_cost: Optional[float] = None  # 平均收藏成本(元)
    follow_cost: Optional[float] = None  # 关注花费(元)
    follows: Optional[int] = None  # 关注量
    avg_follow_cost: Optional[float] = None  # 平均关注成本(元)


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
        # 昨日筛选按钮
        self.yesterday_filter_btn = "#page-container > div > div.ScenesHeader_wrapper__BdcwT > div:nth-child(2) > div > div.DateAreaV2_quickWrapper__fXxpZ > div.DateAreaV2_item__EDE2y.DateAreaV2_isActive__tFhA4"
        
        # 滚动的tbody
        self.tbody_selector = "#odinTable > div.anq-table-box.anq-table-isEnableScroll.anq-table-summaryFixed > div.anq-table-wrapper.CustomTable_table__yYI2o.GoodsTable_promotionListTable__R6hhv.CustomTable_isFilterPanelRender__Krt_r.CustomTable_hasFixedColumn__rMxS6.CustomTable_compact__xrgek.CustomTable_whiteHeader__DkWx1 > div > div > div > div > div.anq-table-body > div > table > tbody"

        # 总数据条数的selector
        self.total_count_selector = '#odinTable > div.anq-pagination-wrapper.CustomPagination_pagination__mBw_4 > ul > li.anq-pagination-total-text'

        # 下一页
        self.nextpage = "#odinTable > div.anq-pagination-wrapper.CustomPagination_pagination__mBw_4 > ul > li.anq-pagination-next > button"


    def login(self):
        """登录拼多多推广系统"""
        self.driver.get("https://mms.pinduoduo.com/login/sso?redirectUrl=https%3A%2F%2Fyingxiao.pinduoduo.com%2Fgoods%2Fpromotion%2Flist%3Fmsfrom%3Dmms_sidenav&platform=yingxiao&accessType=auto")
        
        # 这里需要根据实际登录页面填写用户名和密码
        # 由于拼多多登录页面结构复杂，可能需要手动登录或者使用其他方式
        time.sleep(10)
        print("请手动登录拼多多推广后台，然后按Enter键继续...")
        input()


    def click_yesterday_filter(self):
        """点击昨日筛选按钮"""
        try:
            yesterday_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.yesterday_filter_btn)))
            yesterday_btn.click()
            print("已点击昨日筛选按钮")
            time.sleep(3)  # 等待数据加载
        except Exception as e:
            print(f"点击昨日筛选按钮失败: {e}")


    def get_scroll_container(self, tbody_selector):
        """获取滚动容器"""
        scroll_containers = [
            self.driver.find_element(By.CSS_SELECTOR, ".anq-table-body"),
            self.driver.find_element(By.CSS_SELECTOR, ".anq-table-wrapper"),
            self.driver.find_element(By.CSS_SELECTOR, "#odinTable .anq-table-body")
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
                    '.anq-table-body',
                    '.anq-table-wrapper',
                    '#odinTable .anq-table-body'
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
        STEP = 1000  # 大步长，因为是拼多多推广数据
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
        self.driver.get("https://yingxiao.pinduoduo.com/goods/promotion/list")
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
                all_products[p.name] = p  # 使用商品名称作为key

            print(f"第 {page} 页累计 {len(all_products)} 条")

            if page < total_pages:
                self.click_next_page()
                time.sleep(2)

        return list(all_products.values())


    def parse_product_data(self, cell_texts):
        """解析单行产品数据"""
        if len(cell_texts) < 5:  # 确保有足够的列
            return None
            
        cell_texts = [cell.text.strip() for cell in cell_texts]
        
        # 根据拼多多推广表格列的定义映射数据
        # 第一列是商品信息（包含商品ID和名称）
        goods_info = cell_texts[0] if len(cell_texts) > 0 else ""
        promotion_status = cell_texts[1] if len(cell_texts) > 1 else ""  # 推广状态
        budget_bidding = cell_texts[2] if len(cell_texts) > 2 else ""  # 预算及出价
        total_cost_str = cell_texts[4] if len(cell_texts) > 4 else ""  # 总花费(元)
        transaction_cost_str = cell_texts[5] if len(cell_texts) > 5 else ""  # 成交花费(元)
        actual_transaction_cost_str = cell_texts[6] if len(cell_texts) > 6 else ""  # 实际成交花费(元)
        transaction_amount_str = cell_texts[7] if len(cell_texts) > 7 else ""  # 交易额(元)
        actual_roi_str = cell_texts[8] if len(cell_texts) > 8 else ""  # 实际投产比
        exposure_str = cell_texts[9] if len(cell_texts) > 9 else ""  # 曝光量
        net_transaction_amount_str = cell_texts[10] if len(cell_texts) > 10 else ""  # 净交易额(元)
        net_actual_roi_str = cell_texts[11] if len(cell_texts) > 11 else ""  # 净实际投产比
        net_transaction_count_str = cell_texts[12] if len(cell_texts) > 12 else ""  # 净成交笔数
        cost_per_net_transaction_str = cell_texts[13] if len(cell_texts) > 13 else ""  # 每笔净成交花费(元)
        net_transaction_ratio_str = cell_texts[14] if len(cell_texts) > 14 else ""  # 净交易额占比
        settlement_amount_str = cell_texts[15] if len(cell_texts) > 15 else ""  # 结算金额(元)
        settlement_roi_str = cell_texts[16] if len(cell_texts) > 16 else ""  # 结算投产比
        settlement_count_str = cell_texts[17] if len(cell_texts) > 17 else ""  # 结算笔数
        refund_rate_str = cell_texts[18] if len(cell_texts) > 18 else ""  # 退款率
        refund_order_rate_str = cell_texts[19] if len(cell_texts) > 19 else ""  # 退单率
        refund_exemption_rate_str = cell_texts[20] if len(cell_texts) > 20 else ""  # 退款豁免率
        refund_order_exemption_rate_str = cell_texts[21] if len(cell_texts) > 21 else ""  # 退单豁免率
        transaction_settlement_rate_str = cell_texts[22] if len(cell_texts) > 22 else ""  # 交易额结算率
        order_settlement_rate_str = cell_texts[23] if len(cell_texts) > 23 else ""  # 订单结算率
        settlement_order_cost_str = cell_texts[24] if len(cell_texts) > 24 else ""  # 结算订单成本(元)
        transaction_count_str = cell_texts[25] if len(cell_texts) > 25 else ""  # 成交笔数
        cost_per_transaction_str = cell_texts[26] if len(cell_texts) > 26 else ""  # 每笔成交花费(元)
        amount_per_transaction_str = cell_texts[27] if len(cell_texts) > 27 else ""  # 每笔成交金额(元)
        direct_transaction_amount_str = cell_texts[28] if len(cell_texts) > 28 else ""  # 直接交易额(元)
        indirect_transaction_amount_str = cell_texts[29] if len(cell_texts) > 29 else ""  # 间接交易额(元)
        direct_transaction_count_str = cell_texts[30] if len(cell_texts) > 30 else ""  # 直接成交笔数
        indirect_transaction_count_str = cell_texts[31] if len(cell_texts) > 31 else ""  # 间接成交笔数
        amount_per_direct_transaction_str = cell_texts[32] if len(cell_texts) > 32 else ""  # 每笔直接成交金额(元)
        amount_per_indirect_transaction_str = cell_texts[33] if len(cell_texts) > 33 else ""  # 每笔间接成交金额(元)
        clicks_str = cell_texts[34] if len(cell_texts) > 34 else ""  # 点击量
        inquiry_cost_str = cell_texts[35] if len(cell_texts) > 35 else ""  # 询单花费(元)
        inquiries_str = cell_texts[36] if len(cell_texts) > 36 else ""  # 询单量
        avg_inquiry_cost_str = cell_texts[37] if len(cell_texts) > 37 else ""  # 平均询单成本(元)
        favorite_cost_str = cell_texts[38] if len(cell_texts) > 38 else ""  # 收藏花费(元)
        favorites_str = cell_texts[39] if len(cell_texts) > 39 else ""  # 收藏量
        avg_favorite_cost_str = cell_texts[40] if len(cell_texts) > 40 else ""  # 平均收藏成本(元)
        follow_cost_str = cell_texts[41] if len(cell_texts) > 41 else ""  # 关注花费(元)
        follows_str = cell_texts[42] if len(cell_texts) > 42 else ""  # 关注量
        avg_follow_cost_str = cell_texts[43] if len(cell_texts) > 43 else ""  # 平均关注成本(元)

        # 解析商品名称和ID
        goods_id = ""
        name = goods_info
        
        if '-' in goods_info:
            parts = goods_info.split('-', 1)
            if len(parts) == 2:
                goods_id = parts[0].strip()
                name = parts[1].strip()
        else:
            name = goods_info

        # 解析数值
        total_cost = self.parse_float_value(total_cost_str)
        transaction_cost = self.parse_float_value(transaction_cost_str)
        actual_transaction_cost = self.parse_float_value(actual_transaction_cost_str)
        transaction_amount = self.parse_float_value(transaction_amount_str)
        actual_roi = self.parse_float_value(actual_roi_str)
        exposure = self.parse_int_value(exposure_str)
        net_transaction_amount = self.parse_float_value(net_transaction_amount_str)
        net_actual_roi = self.parse_float_value(net_actual_roi_str)
        net_transaction_count = self.parse_int_value(net_transaction_count_str)
        cost_per_net_transaction = self.parse_float_value(cost_per_net_transaction_str)
        net_transaction_ratio = self.parse_float_value(net_transaction_ratio_str)
        settlement_amount = self.parse_float_value(settlement_amount_str)
        settlement_roi = self.parse_float_value(settlement_roi_str)
        settlement_count = self.parse_int_value(settlement_count_str)
        refund_rate = self.parse_float_value(refund_rate_str)
        refund_order_rate = self.parse_float_value(refund_order_rate_str)
        refund_exemption_rate = self.parse_float_value(refund_exemption_rate_str)
        refund_order_exemption_rate = self.parse_float_value(refund_order_exemption_rate_str)
        transaction_settlement_rate = self.parse_float_value(transaction_settlement_rate_str)
        order_settlement_rate = self.parse_float_value(order_settlement_rate_str)
        settlement_order_cost = self.parse_float_value(settlement_order_cost_str)
        transaction_count = self.parse_int_value(transaction_count_str)
        cost_per_transaction = self.parse_float_value(cost_per_transaction_str)
        amount_per_transaction = self.parse_float_value(amount_per_transaction_str)
        direct_transaction_amount = self.parse_float_value(direct_transaction_amount_str)
        indirect_transaction_amount = self.parse_float_value(indirect_transaction_amount_str)
        direct_transaction_count = self.parse_int_value(direct_transaction_count_str)
        indirect_transaction_count = self.parse_int_value(indirect_transaction_count_str)
        amount_per_direct_transaction = self.parse_float_value(amount_per_direct_transaction_str)
        amount_per_indirect_transaction = self.parse_float_value(amount_per_indirect_transaction_str)
        clicks = self.parse_int_value(clicks_str)
        inquiry_cost = self.parse_float_value(inquiry_cost_str)
        inquiries = self.parse_int_value(inquiries_str)
        avg_inquiry_cost = self.parse_float_value(avg_inquiry_cost_str)
        favorite_cost = self.parse_float_value(favorite_cost_str)
        favorites = self.parse_int_value(favorites_str)
        avg_favorite_cost = self.parse_float_value(avg_favorite_cost_str)
        follow_cost = self.parse_float_value(follow_cost_str)
        follows = self.parse_int_value(follows_str)
        avg_follow_cost = self.parse_float_value(avg_follow_cost_str)

        # 创建产品对象
        product = ProductInfo(
            goods_id=goods_id,
            name=name,
            price=transaction_amount,  # 使用交易额作为价格参考
            stock=transaction_count,  # 使用成交笔数作为库存参考
            promotion_status=promotion_status,
            budget_bidding=budget_bidding,
            total_cost=total_cost,
            transaction_cost=transaction_cost,
            actual_transaction_cost=actual_transaction_cost,
            transaction_amount=transaction_amount,
            actual_roi=actual_roi,
            exposure=exposure,
            net_transaction_amount=net_transaction_amount,
            net_actual_roi=net_actual_roi,
            net_transaction_count=net_transaction_count,
            cost_per_net_transaction=cost_per_net_transaction,
            net_transaction_ratio=net_transaction_ratio,
            settlement_amount=settlement_amount,
            settlement_roi=settlement_roi,
            settlement_count=settlement_count,
            refund_rate=refund_rate,
            refund_order_rate=refund_order_rate,
            refund_exemption_rate=refund_exemption_rate,
            refund_order_exemption_rate=refund_order_exemption_rate,
            transaction_settlement_rate=transaction_settlement_rate,
            order_settlement_rate=order_settlement_rate,
            settlement_order_cost=settlement_order_cost,
            transaction_count=transaction_count,
            cost_per_transaction=cost_per_transaction,
            amount_per_transaction=amount_per_transaction,
            direct_transaction_amount=direct_transaction_amount,
            indirect_transaction_amount=indirect_transaction_amount,
            direct_transaction_count=direct_transaction_count,
            indirect_transaction_count=indirect_transaction_count,
            amount_per_direct_transaction=amount_per_direct_transaction,
            amount_per_indirect_transaction=amount_per_indirect_transaction,
            clicks=clicks,
            inquiry_cost=inquiry_cost,
            inquiries=inquiries,
            avg_inquiry_cost=avg_inquiry_cost,
            favorite_cost=favorite_cost,
            favorites=favorites,
            avg_favorite_cost=avg_favorite_cost,
            follow_cost=follow_cost,
            follows=follows,
            avg_follow_cost=avg_follow_cost,
            platform="pinduoduo"
        )
        
        return product


    def parse_float_value(self, value_str):
        """解析浮点数字符串"""
        if not value_str or value_str == "-":
            return 0.0
        try:
            # 移除逗号并转换为浮点数
            cleaned_str = value_str.replace(",", "")
            return float(cleaned_str)
        except ValueError:
            return 0.0


    def parse_int_value(self, value_str):
        """解析整数字符串"""
        if not value_str or value_str == "-":
            return 0
        try:
            # 移除逗号并转换为整数
            cleaned_str = value_str.replace(",", "")
            return int(float(cleaned_str))  # 先转为float再转int，以处理小数部分
        except ValueError:
            return 0


    def get_products(self):
        """获取商品列表 - 主入口方法"""
        print("开始获取拼多多推广数据...")
        
        self.navigate_to_page()
        time.sleep(5)
        
        # 点击昨日筛选按钮
        self.click_yesterday_filter()
        
        # 获取所有分页数据
        products = self.get_all_paginated_data(self.tbody_selector)
        
        print(f"拼多多推广数据解析完成，共 {len(products)} 条")
        
        # 返回格式与原函数一致
        all_products = {
            'regular_products': products,
            'return_products': []  # 拼多多推广数据没有退货数据
        }

        return all_products, len(products), 0


    def request(self):

        url = "https://yingxiao.pinduoduo.com/mms-gateway/venus/api/goods/promotion/v1/list"

        headers = {
            "User-Agent": "Mozilla/5.0 ...",
            "Content-Type": "application/json",
            "Referer": "https://yingxiao.pinduoduo.com/goods/promotion/list",
            # 必须带上登录后的 Cookie
            "Cookie": "eyJ0IjoiSFhuNXNjQjhrNDlqNXVKajY3QVJEaVNDU1UySS94czk1NER6cUZRUmFVODEzUS9CMzFkS3c3TG5RdGhuV0p5ZSIsInYiOjEsInMiOjIzLCJtIjoyNjM1NjQ3ODksInUiOjE3MzcwNTUyMn0"
        }

        payload = {
            "crawlerInfo": "0asWtqlygjngygv9Q0cBoh5SHqZ2YXWVBZJZrXiFzd2ZURZaekBBqrlc-JDVA8A1mOwNfwEePw9syPBws947T-1n42BeYqfJowgtszKdex_bON2by8AEWosF3MkCtQElqio6hP5Q6rhD9BMbCeSSSckEewczPglYLJ2YfBTYB7eTmUTEfuAiP7Jc5EJ3VrTHu9EiJoMgoxyP89ha0ZuJWvTydd_eJtpzCGO3njASOo0fOabTK_zxNWabCVgc51RIXZ7bH-rN9ZWQGr2chnGC6vOa4P6k_Vo8P-XnsSRvJRkW_N7bBSkm5wTH35Xn9R-OcJVX6aH8xRkVpoomQP42Xn9A80Gu_IWnvPe-NiO2FCVaCIxhmI3TdrwMHvOaYac4GlgYbawMEKnKIW6GlhWsl7g0Gz1vY2qzGn7KmIVgcnLI3-iX20pl0lZFHp5qNluJC3FIMSoNtLro_K6ufQgtuSS082CoppWaS3CffZsr2EHVPvEx1H5kL1hTtA6qWZVbNZwZsbMI5KXFFAgl_g3_EpXMc-BjGsm5K1e96EJK0U4eVtX4ENcDUenzmMFt0httvZWoNCHwY7ArmsfjyMFFVgscpM19zIXa-S7KpXV2ha_rezL30b3_q1TxMH5ZcDo5h6YIZsSt3Dnyy_H_Lw-3rWLyb1MAsRnG58iGZLNicRkgNCPU1Xl3kN1d-7s2bG_AtOLJ2rBEzJ_urJ_PhBW3FaKl4RhhMbzMYWPoRD8Ep7WPaJ2hPTy9D8JbaP",
            "clientType": 1,
            "blockType": 3,
            "beginDate": "2026-01-20",
            "endDate": "2026-01-20",
            "pageNumber": 1,
            "pageSize": 50,
            "sortBy": 9999,
            "orderBy": 9999,
            "filter": {},
            "scenesMode": 1
        }

        response = requests.post(url, json=payload, headers=headers,
            cookies={
                "_a42": "386ba908-471c-4b9d-af6d-4a6bdb864a66",
                "_bee": "hLBIWqdPbG9KmuR61y1cMuEu1YCxYQ7b",
                "_f77" : "6e928cbe-c1ca-443d-b1f0-b17187327621",
                "_nano_fp" : "Xpmjl0CJlpXJlpTbXo_FIMEr7tOdempOVQeEZl1q",
                "api_uid" : "Ck9MdGlvHC1LLQBZQjvSAg==",
                "rckk" : "hLBIWqdPbG9KmuR61y1cMuEu1YCxYQ7b",
                "ru1k" : "6e928cbe-c1ca-443d-b1f0-b17187327621",
                "ru2k" : "386ba908-471c-4b9d-af6d-4a6bdb864a66",
                "SUB_PASS_ID" : "eyJ0IjoiRmp6SjJQbEg0YWgzQWZYNG9Dbkd6c3MxaERWUkl6N1NSU21kYUNLc29xcUJTV0NnWVRrT0xLbHpZU1YvWTh0VyIsInYiOjEsInMiOjcsIm0iOjI2MzU2NDc4OSwidSI6MTczNzA1NTIyfQ",
                "SUB_SYSTEM_ID" : "7",
                "windows_app_shop_token_23" : "eyJ0IjoiSFhuNXNjQjhrNDlqNXVKajY3QVJEaVNDU1UySS94czk1NER6cUZRUmFVODEzUS9CMzFkS3c3TG5RdGhuV0p5ZSIsInYiOjEsInMiOjIzLCJtIjoyNjM1NjQ3ODksInUiOjE3MzcwNTUyMn0"
                
            }
            )

        print(response.status_code)
        print(response.text)




    def close(self):
        """关闭浏览器"""
        self.driver.quit()



# 使用示例
if __name__ == "__main__":
    crawler = SeleniumCrawler()
    try:
        crawler.request()
        # crawler.login()
        # products, regular_total, return_total = crawler.get_products()
        # print(f"pinduoduo 平台推广商品数量: {regular_total}, 被取消商品数量: {return_total}")
        
        # # 插入数据库
        # db_manager = DataToDB()
        # db_manager.insert_jushuitan_data(products)
    
    except Exception as e:
        print(f"发生错误: {e}")

    finally:
        crawler.close()