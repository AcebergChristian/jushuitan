from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time
import json
from dataclasses import dataclass
from typing import List, Optional

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

    def get_products(self) -> List[ProductInfo]:
        """获取商品列表"""
        # 导航到商品页面
        self.driver.get("https://sc.scm121.com/tradeManage/tower/distribute")
        time.sleep(5)  # 等待页面加载
        
        # 切换到iframe（如果存在）
        try:
            iframe = self.wait.until(EC.presence_of_element_located((By.ID, "tradeManage1")))
            self.driver.switch_to.frame(iframe)
            print("已切换到iframe")
        except:
            print("未找到iframe，继续在主页面操作")
        
        # 找到表格主体
        tbody_selector = '#channelOrder-table-wrap > div:nth-child(3) > div.react-contextmenu-wrapper > div > div > div > div.art-table > div.art-table-body.art-horizontal-scroll-container > table > tbody'
        
        # 等待表格加载
        tbody = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, tbody_selector)))
        
        # 找到滚动容器
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
        
        if not scroll_container:
            print("未找到滚动容器")
            # 尝试获取当前页面上的所有行
            rows = self.driver.find_elements(By.CSS_SELECTOR, f"{tbody_selector} tr")
            print(f"找到 {len(rows)} 行数据（无滚动）")
        else:
            print("开始滚动加载更多数据...")
            
            # 滚动加载所有数据
            last_height = self.driver.execute_script("return arguments[0].scrollHeight", scroll_container)
            consecutive_no_new = 0
            max_consecutive_no_new = 3
            max_scrolls = 20
            

            data_rows = []
            for i in range(max_scrolls):
                if consecutive_no_new >= max_consecutive_no_new:
                    print("连续多次未发现新数据，停止滚动")
                    break
                
                # 获取滚动容器的当前状态
                current_scroll_top = self.driver.execute_script("return arguments[0].scrollTop", scroll_container)
                scroll_height = self.driver.execute_script("return arguments[0].scrollHeight", scroll_container)
                client_height = self.driver.execute_script("return arguments[0].clientHeight", scroll_container)
                
                # 计算滚动步长（大致相当于5行数据的高度）
                # 先获取当前可见的行数来估算每行高度
                current_visible_rows = self.driver.find_elements(By.CSS_SELECTOR, f"{tbody_selector} tr")
                if len(current_visible_rows) > 0:
                    # 估算每行高度，使用第一行来计算
                    try:
                        first_row = current_visible_rows[0]
                        row_height = self.driver.execute_script("""
                            var rect = arguments[0].getBoundingClientRect();
                            return rect.height;
                        """, first_row)
                        step_height = int(row_height * 5)  # 每次滚动大约5行的高度
                    except:
                        step_height = 200  # 默认步长
                else:
                    step_height = 200  # 默认步长
                
                # 滚动指定的距离
                new_scroll_top = min(current_scroll_top + step_height, scroll_height - client_height)
                
                # 如果已经到达底部，跳出循环
                if current_scroll_top >= scroll_height - client_height - 10:  # 10是容差
                    print("已到达底部")
                    break
                
                # 执行滚动
                self.driver.execute_script("arguments[0].scrollTop = arguments[1];", scroll_container, new_scroll_top)
                
                time.sleep(2)  # 等待新数据加载
                
                # 检查新的滚动高度和位置
                updated_scroll_top = self.driver.execute_script("return arguments[0].scrollTop", scroll_container)
                updated_scroll_height = self.driver.execute_script("return arguments[0].scrollHeight", scroll_container)
                
                if updated_scroll_top == current_scroll_top:
                    consecutive_no_new += 1
                    print(f"滚动 {i+1}: 没有新数据加载 (连续 {consecutive_no_new} 次)")
                else:
                    consecutive_no_new = 0
                    print(f"滚动 {i+1}: 位置从 {current_scroll_top} 移动到 {updated_scroll_top}, 总高度 {updated_scroll_height}")


                data_rows.extend(self.driver.find_elements(By.CSS_SELECTOR, f"{tbody_selector} tr"))

        
        # 获取所有行数据
        print(f"总共找到 {len(data_rows)} 行数据")

        # 去重
        data_rows = list(set(data_rows))
        # 去重后数据
        print(f"去重后 {len(data_rows)} 行数据")
        
        products = []
        # 重新获取所有的行，以确保元素引用是最新的
        all_current_rows = self.driver.find_elements(By.CSS_SELECTOR, f"{tbody_selector} tr")
        
        for row in all_current_rows:
            try:
                # 获取行中的所有单元格
                cells = row.find_elements(By.TAG_NAME, "td")
                
                if len(cells) >= 5:  # 确保有足够的列
                    cell_texts = [cell.text.strip() for cell in cells]
                    
                    # 根据表格列的定义映射数据
                    # 索引1-33 对应不同字段，跳过索引0
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
                    import re
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
                    
                    products.append(product)
                    
            except Exception as e:
                print(f"解析行数据时出错: {e}")
                continue
        
        print(f"成功解析 {len(products)} 个商品")
        return products

    def close(self):
        """关闭浏览器"""
        self.driver.quit()

# 使用示例
if __name__ == "__main__":
    crawler = SeleniumCrawler()
    try:
        crawler.login()
        products = crawler.get_products()
        print(f"jushuitan 平台商品数量: {len(products)}")
        for product in products[:5]:  # 显示前5个商品
            print(f"商品ID: {product.goods_id}, 名称: {product.name}, 价格: {product.price}, 库存: {product.stock}")
    finally:
        crawler.close()