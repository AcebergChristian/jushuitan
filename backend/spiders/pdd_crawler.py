from ast import Dict
# from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.common.exceptions import StaleElementReferenceException
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError



class PddCrawler:
    def __init__(self):
        # 初始化Playwright
        self.playwright = None
        self.browser = None
        self.page = None
        self.context = None

        ######### 元素选择器 登录之外的 #########
        # 昨日筛选按钮
        self.yesterday_filter_btn = 'div.DateAreaV2_item__EDE2y.DateAreaV2_isActive__tFhA4'
        
        # 滚动的tbody
        self.tbody_selector = 'div.anq-table-body'

        # 总数据条数的选择器
        self.total_count_selector = 'li.anq-pagination-total-text'

        # 下一页
        self.nextpage = 'li.anq-pagination-next > button'

    def init_browser(self):
        """初始化浏览器"""
        self.playwright = sync_playwright().start()
        # 可选是否显示浏览器窗口
        self.browser = self.playwright.chromium.launch(headless=False, args=[
            "--no-sandbox",
            "--disable-dev-shm-usage"
        ])
        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        self.page = self.context.new_page()

    def login(self):
        """登录拼多多推广系统"""
        self.init_browser()
        self.page.goto("https://yingxiao.pinduoduo.com/goods/promotion/list?msfrom=mms_sidenav")
        
        # 等待用户手动登录
        print("请在浏览器中手动登录拼多多推广后台，然后按Enter键继续...")
        input()
        
        # 保存cookies以便后续请求使用
        self.cookies = self.page.context.cookies()

    def click_yesterday_filter(self):
        """点击昨日筛选按钮"""
        try:
            # 等待元素可点击
            yesterday_btn = self.page.wait_for_selector(self.yesterday_filter_btn, state='visible')
            yesterday_btn.click()
            print("已点击昨日筛选按钮")
            self.page.wait_for_timeout(3000)  # 等待数据加载
        except PlaywrightTimeoutError:
            print("点击昨日筛选按钮超时")

    def get_scroll_container(self, tbody_selector):
        """获取滚动容器"""
        # 在Playwright中我们直接操作页面元素
        # 尝试找到具有滚动特性的容器
        scroll_selectors = [
            ".anq-table-body",
            ".anq-table-wrapper",
            "#odinTable .anq-table-body"
        ]
        
        for selector in scroll_selectors:
            try:
                element = self.page.query_selector(selector)
                if element:
                    # 检查元素是否可滚动
                    is_scrollable = self.page.evaluate("""
                        (element) => {
                            return element.scrollHeight > element.clientHeight || element.scrollWidth > element.clientWidth;
                        }
                    """, element)
                    if is_scrollable:
                        return element
            except:
                continue
        
        # 如果没找到滚动容器，返回tbody的父元素
        try:
            tbody = self.page.query_selector(tbody_selector)
            if tbody:
                parent = self.page.evaluate("""
                    (tbody) => {
                        let parent = tbody.parentElement;
                        while (parent && parent !== document.body) {
                            if (parent.scrollHeight > parent.clientHeight || parent.scrollWidth > parent.clientWidth) {
                                return parent;
                            }
                            parent = parent.parentElement;
                        }
                        return null;
                    }
                """, tbody)
                if parent:
                    return parent
        except:
            pass
        
        return None

    # 滚动获取tr数据并解析到list
    def scroll_and_parse_data(self, tbody_selector, max_scrolls=200):
        scroll_container = self.get_scroll_container(tbody_selector)
        if not scroll_container:
            return []

        parsed = {}
        STEP = 1000  # 大步长，因为是拼多多推广数据
        last_scroll_top = -1

        for _ in range(max_scrolls):
            # 获取当前页面的所有行
            rows = self.page.query_selector_all(f"{tbody_selector} tr")

            for row in rows:
                try:
                    cells = row.query_selector_all("td")
                    product = self.parse_product_data(cells)
                    if not product:
                        continue

                    # 🔥 行级唯一 key（不依赖业务字段）
                    row_text = "|".join([cell.inner_text() for cell in cells])
                    row_key = hashlib.md5(row_text.encode("utf-8")).hexdigest()
                    parsed[row_key] = product

                except Exception as e:
                    print(f"解析行数据时出错: {e}")
                    continue

            # 获取当前滚动位置
            scroll_position = self.page.evaluate("""
                () => {
                    const container = document.querySelector(arguments[0]);
                    if (container) {
                        return {
                            scrollTop: container.scrollTop,
                            scrollHeight: container.scrollHeight,
                            clientHeight: container.clientHeight
                        };
                    }
                    return null;
                }
            """, self.tbody_selector)

            if not scroll_position:
                break

            scroll_top = scroll_position['scrollTop']
            scroll_height = scroll_position['scrollHeight']
            client_height = scroll_position['clientHeight']

            if scroll_top >= scroll_height - client_height - 5:
                break

            if scroll_top == last_scroll_top:
                break
            last_scroll_top = scroll_top

            # 执行滚动
            self.page.evaluate(f"""
                () => {{
                    const container = document.querySelector('{self.tbody_selector}');
                    if (container) {{
                        container.scrollTop = container.scrollTop + {STEP};
                    }}
                }}
            """)
            self.page.wait_for_timeout(300)

        return list(parsed.values())

    def navigate_to_page(self):
        """导航到目标页面"""
        if not self.page:
            self.init_browser()
        self.page.goto("https://yingxiao.pinduoduo.com/goods/promotion/list")
        self.page.wait_for_timeout(5000)  # 等待页面加载

    def get_total_count(self):
        """获取总记录数和总页数"""
        try:
            # 等待总数元素出现
            total_count_element = self.page.wait_for_selector(self.total_count_selector, state='visible')
            total_count_text = total_count_element.inner_text()
            
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
        except PlaywrightTimeoutError:
            print("获取总记录数超时")
            return 0, 1

    def click_next_page(self):
        """点击下一页"""
        try:
            next_page_btn = self.page.query_selector(self.nextpage)
            if next_page_btn and next_page_btn.is_enabled():
                next_page_btn.click()
                self.page.wait_for_timeout(3000)  # 等待下一页数据加载
                
                # 页面加载后，将tbody滚动到最上面
                try:
                    # 将滚动容器滚动到顶部
                    self.page.evaluate(f"""
                        () => {{
                            const container = document.querySelector('{self.tbody_selector}');
                            if (container) {{
                                container.scrollTop = 0;
                            }}
                        }}
                    """)
                    print("已将滚动容器滚动到顶部")
                except Exception as scroll_error:
                    print(f"滚动到顶部时出错: {scroll_error}")
                
                return True
            else:
                print("已经是最后一页")
                return False
        except Exception as e:
            print(f"点击下一页时出错: {e}")
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
                self.page.wait_for_timeout(2000)

        return list(all_products.values())

    def parse_product_data(self, cell_texts):
        """解析单行产品数据"""
        if len(cell_texts) < 5:  # 确保有足够的列
            return None
            
        cell_texts = [cell.inner_text().strip() for cell in cell_texts]
        
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

    def get_products(self):
        """获取商品列表 - 主入口方法"""
        print("开始获取拼多多推广数据...")
        
        self.navigate_to_page()
        self.page.wait_for_timeout(5000)
        
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

    def close(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()


if __name__ == '__main__':
    crawler = PddCrawler()
    crawler.get_products()