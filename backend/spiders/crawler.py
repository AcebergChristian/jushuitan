"""
聚水潭和拼多多数据爬虫服务
使用Playwright进行网页自动化操作
"""
import asyncio
from typing import Dict, List, Optional
from playwright.async_api import async_playwright
from dataclasses import dataclass
from bs4 import BeautifulSoup


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


class JushuitanSpider:
    """聚水潭平台爬虫"""
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.browser = None
        
    async def init_browser(self):
        """初始化浏览器"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=False)
        
    async def login(self):
        """登录聚水潭"""
        if not self.browser:
            await self.init_browser()
            
        page = await self.browser.new_page()
        await page.goto("https://account.scm121.com/user/login")  # 实际URL可能不同
        
        # 输入用户名和密码
        await page.fill("#username", self.username)
        await page.fill("#password", self.password)
        
        # 点击checkout按钮
        await page.click("#real-root > section > main > div > div > div > form > div.antd-pro-pages-account-styles-index-container > div.antd-pro-pages-account-components-agreement-checked-index-remember > label > span.ant-checkbox > input")
        

        # 点击登录按钮
        await page.click("#real-root > section > main > div > div > div > form > div.antd-pro-pages-account-login-style-submit > button")
        
        # 等待登录成功
        await page.wait_for_url("**/dashboard**")
        
        return page
    
    async def get_products(self) -> List[ProductInfo]:
        """获取商品列表"""
        page = await self.login()
        
        # 导航到商品页面（示例）
        await page.goto("https://sc.scm121.com/tradeManage/tower/distribute")
        
        # 先等待页面加载完成
        await page.wait_for_load_state('networkidle')
        
        # 等待特定时间让JavaScript渲染完成
        await page.wait_for_timeout(5000)
        
        # 查找并切换到可能包含商品数据的 iframe
        # 通过 iframe 的 ID 或 name
        try:
            # 等待 iframe 元素出现
            iframe_locator = page.locator("#tradeManage1")          # 或 page.frame_locator("#tradeManage1") 也可以
            await iframe_locator.wait_for(state="visible", timeout=20000)

            # 获取 iframe 的 element handle
            iframe_element = await iframe_locator.element_handle()

            # 从 element handle 获取真正的 Frame 对象
            frame = await iframe_element.content_frame()
            
            # 用于存储所有收集到的行数据
            collected_rows = []
            seen_row_keys = set()
            
            # 执行增量滚动
            max_attempts = 15
            consecutive_empty_attempts = 0
            attempts = 0
            
            # 首先获取初始数据量
            initial_data_check = await frame.evaluate("""() => {
                const tbodySelector = '#channelOrder-table-wrap > div:nth-child(3) > div.react-contextmenu-wrapper > div > div > div > div.art-table > div.art-table-body.art-horizontal-scroll-container > table > tbody';
                const tbody = document.querySelector(tbodySelector);
                
                if (!tbody) {
                    console.error("tbody not found initially");
                    return {has_tbody: false, row_count: 0};
                }
                
                const rows = tbody.querySelectorAll('tr');
                console.log("初始行数:", rows.length);
                return {has_tbody: true, row_count: rows.length};
            }""")
            
            print(f"初始数据检查 - 有tbody: {initial_data_check['has_tbody']}, 行数: {initial_data_check['row_count']}")
            
            while attempts < max_attempts and consecutive_empty_attempts < 3:
                attempts += 1
                
                # 调用JS函数执行一次滚动并获取新行
                scroll_result = await frame.evaluate("""() => {
                    const tbodySelector = '#channelOrder-table-wrap > div:nth-child(3) > div.react-contextmenu-wrapper > div > div > div > div.art-table > div.art-table-body.art-horizontal-scroll-container > table > tbody';
                    const tbody = document.querySelector(tbodySelector);
                    
                    if (!tbody) {
                        console.error("tbody not found");
                        return {status: "no_tbody", new_rows: [], total_rows: 0};
                    }

                    // 尝试多种可能的滚动容器
                    let scrollContainers = [
                        tbody.closest('.art-table-body'),
                        tbody.closest('.art-horizontal-scroll-container'),
                        document.querySelector('.art-table-body'),
                        document.querySelector('.art-table-body .virtual-list'),
                        document.querySelector('.art-table-body .virtual-table'),
                        document.querySelector('#channelOrder-table-wrap .art-table-body'),
                        document.body
                    ];
                    
                    let scrollContainer = null;
                    for(let container of scrollContainers) {
                        if(container && container.scrollHeight > container.clientHeight) {
                            scrollContainer = container;
                            break;
                        }
                    }
                    
                    // 如果没找到合适的滚动容器，尝试直接使用tbody的父级
                    if(!scrollContainer) {
                        scrollContainer = tbody.parentElement;
                        if(scrollContainer.scrollHeight <= scrollContainer.clientHeight) {
                            scrollContainer = tbody.parentElement.parentElement;
                        }
                    }

                    if (!scrollContainer) {
                        console.log("未找到有效的滚动容器");
                        // 尝试获取当前所有行
                        const rows = tbody.querySelectorAll('tr');
                        const current_rows = [];
                        
                        rows.forEach((row, index) => {
                            const rowKey = row.getAttribute('data-row-key') || 
                                        row.getAttribute('data-rowindex') || 
                                        row.getAttribute('data-id') || 
                                        `row_${index}`;
                            
                            current_rows.push({
                                key: rowKey,
                                html: row.outerHTML,
                                rowIndex: index
                            });
                        });
                        
                        return {
                            status: "no_scroll_container",
                            new_rows: current_rows,
                            total_rows: current_rows.length,
                            scroll_position: 0,
                            max_scroll: 0,
                            client_height: 0
                        };
                    }
                    
                    // 记录滚动前的状态
                    const oldScrollTop = scrollContainer.scrollTop;
                    const maxScrollTop = scrollContainer.scrollHeight - scrollContainer.clientHeight;
                    const oldRowCount = tbody.querySelectorAll('tr').length;
                    
                    console.log("滚动容器类型:", scrollContainer.tagName || scrollContainer.className);
                    console.log("滚动前scrollTop:", oldScrollTop);
                    console.log("最大可滚动距离:", maxScrollTop);
                    console.log("客户端高度:", scrollContainer.clientHeight);
                    console.log("滚动前行数:", oldRowCount);
                    
                    // 执行滚动 - 尝试滚动一部分距离
                    const scrollStep = Math.min(800, maxScrollTop - oldScrollTop); // 每次滚动不超过剩余距离
                    if(scrollStep > 0) {
                        scrollContainer.scrollTop = oldScrollTop + scrollStep;
                    } else {
                        // 已经到达底部
                        scrollContainer.scrollTop = maxScrollTop;
                    }
                    
                    // 等待滚动完成和新内容加载
                    return new Promise(resolve => {
                        setTimeout(() => {
                            const newScrollTop = scrollContainer.scrollTop;
                            const newRowCount = tbody.querySelectorAll('tr').length;
                            const atBottom = Math.abs(scrollContainer.scrollHeight - scrollContainer.scrollTop - scrollContainer.clientHeight) < 50;
                            
                            console.log("滚动后scrollTop:", newScrollTop);
                            console.log("滚动后行数:", newRowCount);
                            console.log("是否到达底部:", atBottom);
                            
                            // 收集当前可见的所有行
                            const rows = tbody.querySelectorAll('tr');
                            const current_rows = [];
                            
                            rows.forEach((row, index) => {
                                // 获取行的唯一标识
                                const rowKey = row.getAttribute('data-row-key') || 
                                            row.getAttribute('data-rowindex') || 
                                            row.getAttribute('data-id') || 
                                            `row_${index}`;
                                
                                current_rows.push({
                                    key: rowKey,
                                    html: row.outerHTML,
                                    rowIndex: index
                                });
                            });
                            
                            resolve({
                                status: "scrolled",
                                new_rows: current_rows,
                                total_rows: current_rows.length,
                                scroll_position: newScrollTop,
                                old_scroll_position: oldScrollTop,
                                row_count_before: oldRowCount,
                                row_count_after: newRowCount,
                                at_bottom: atBottom,
                                max_scroll: maxScrollTop,
                                client_height: scrollContainer.clientHeight
                            });
                        }, 1500); // 增加等待时间到1.5秒确保内容加载
                    });
                }""")
                
                print(f'滚动结果: 第{attempts}次滚动 | 状态: {scroll_result.get("status", "unknown")} | 滚动前行数: {scroll_result.get("row_count_before", 0)} | 滚动后行数: {scroll_result.get("row_count_after", 0)} | 当前总数: {scroll_result.get("total_rows", 0)}')
                print(f'滚动位置: {scroll_result.get("old_scroll_position", 0)} -> {scroll_result.get("scroll_position", 0)} | 最大滚动: {scroll_result.get("max_scroll", 0)} | 客户端高度: {scroll_result.get("client_height", 0)}')
                
                # 处理滚动结果
                if scroll_result and isinstance(scroll_result, dict):
                    new_rows = scroll_result.get('new_rows', [])
                    
                    # 检查是否有tbody
                    if scroll_result.get('status') == 'no_tbody':
                        print("未找到tbody元素，请检查选择器路径")
                        break
                    
                    # 过滤出新的行
                    new_unique_rows = []
                    for row_data in new_rows:
                        row_key = row_data.get('key')
                        if row_key and row_key not in seen_row_keys:
                            new_unique_rows.append(row_data)
                            seen_row_keys.add(row_key)
                    
                    # 添加新行到总集合
                    if new_unique_rows:
                        collected_rows.extend(new_unique_rows)
                        consecutive_empty_attempts = 0  # 重置连续空尝试计数
                        print(f"发现 {len(new_unique_rows)} 个新行，总计 {len(collected_rows)} 行")
                    else:
                        consecutive_empty_attempts += 1
                        print(f"未发现新行，连续空尝试: {consecutive_empty_attempts}")
                    
                    # 检查是否已到达底部
                    if scroll_result.get('at_bottom', False):
                        print("已到达底部，停止滚动")
                        break
                else:
                    consecutive_empty_attempts += 1
                    print(f"滚动结果异常，连续空尝试: {consecutive_empty_attempts}")
                
                # 等待一段时间再进行下次滚动
                await page.wait_for_timeout(1500)
            
            print(f'最终收集到 {len(collected_rows)} 行数据')
            
            # 处理收集到的数据
            if collected_rows:
                print(f"总共收集到 {len(collected_rows)} 行HTML数据")
                
                # 解析收集到的行数据
                parsed_products = []
                
                for row_data in collected_rows:
                    try:
                        # 在frame中执行解析
                        parsed_data = await frame.evaluate("""(rowHtml) => {
                            // 创建临时div来解析HTML
                            const tempDiv = document.createElement('div');
                            tempDiv.innerHTML = rowHtml;
                            const row = tempDiv.querySelector('tr');
                            
                            if (!row) return null;
                            
                            const cells = row.querySelectorAll('td');
                            const cellData = [];
                            
                            cells.forEach(cell => {
                                cellData.push(cell.textContent.trim());
                            });
                            
                            return {
                                cell_count: cellData.length,
                                cells: cellData
                            };
                        }""", row_data['html'])
                        
                        if parsed_data and parsed_data['cell_count'] >= 4:
                            # 根据实际列的含义分配值，而不是假设固定顺序
                            # 表格列索引 1-33 对应以下字段：
                            # 索引1: 订单号 (order_number)
                            # 索引2: 线上订单号 (online_order_number)
                            # 索引3: 店铺名称 (shop_name)
                            # 索引4: 标签 (label)
                            # 索引5: 商品信息 (name/goods info)
                            # 索引6: 买家昵称&收件人 (buyer_nickname)
                            # 索引7: 供应商 (supplier)
                            # 索引8: 采购金额 (purchase_amount)
                            # 索引9: 状态 (status)
                            # 索引10: 快递公司 (shipping_company)
                            # 索引11: 解决方案 (solution)
                            # 索引13: 分销商推单时间 (distributor_push_time)
                            # 索引20: 客户下单数量 (customer_quantity)
                            # 索引21: 客户下单金额 (customer_amount)
                            # 索引23: 重量 (weight)
                            # 索引24: 实际称重重量 (actual_weight)
                            # 索引27: 买家留言 (buyer_message)
                            # 索引28: 卖家备注/旗帜 (seller_remark)
                            # 索引29: 线下备注 (offline_remark)
                            # 索引30: 下单时间 (placing_time)
                            # 索引31: 付款时间 (payment_time)
                            # 索引32: 发货时间 (shipping_time)
                            # 索引33: 分销商 (distributor)
                            # 索引34: 发货仓库 (shipping_warehouse)
                            
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
                            distributor_push_time = cell_texts[12] if len(cell_texts) > 12 else ""  # 注意这里索引可能有变化
                            customer_quantity_candidate = cell_texts[19] if len(cell_texts) > 19 else ""  # 索引20对应数组索引19
                            customer_amount_candidate = cell_texts[20] if len(cell_texts) > 20 else ""  # 索引21对应数组索引20
                            weight_candidate = cell_texts[22] if len(cell_texts) > 22 else ""  # 索引23对应数组索引22
                            actual_weight_candidate = cell_texts[23] if len(cell_texts) > 23 else ""  # 索引24对应数组索引23
                            buyer_message = cell_texts[26] if len(cell_texts) > 26 else ""  # 索引27对应数组索引26
                            seller_remark = cell_texts[27] if len(cell_texts) > 27 else ""  # 索引28对应数组索引27
                            offline_remark = cell_texts[28] if len(cell_texts) > 28 else ""  # 索引29对应数组索引28
                            placing_time = cell_texts[29] if len(cell_texts) > 29 else ""  # 索引30对应数组索引29
                            payment_time = cell_texts[30] if len(cell_texts) > 30 else ""  # 索引31对应数组索引30
                            shipping_time = cell_texts[31] if len(cell_texts) > 31 else ""  # 索引32对应数组索引31
                            distributor = cell_texts[32] if len(cell_texts) > 32 else ""  # 索引33对应数组索引32
                            shipping_warehouse = cell_texts[33] if len(cell_texts) > 33 else ""  # 索引34对应数组索引33
                            
                            # 智能解析价格：从文本中提取数字部分（这里我们使用采购金额作为价格参考）
                            import re
                            purchase_amount_match = re.search(r'[\d,]+\.?\d*', purchase_amount_candidate.replace(',', ''))
                            purchase_amount = float(purchase_amount_match.group()) if purchase_amount_match else 0.0
                            
                            # 智能解析客户下单金额
                            customer_amount_match = re.search(r'[\d,]+\.?\d*', customer_amount_candidate.replace(',', ''))
                            customer_amount = float(customer_amount_match.group()) if customer_amount_match else 0.0
                            
                            # 智能解析客户下单数量
                            customer_quantity_match = re.search(r'\d+', customer_quantity_candidate)
                            customer_quantity = int(customer_quantity_match.group()) if customer_quantity_match else 0
                            
                            # 智能解析重量
                            weight_match = re.search(r'[\d.]+', weight_candidate)
                            weight = float(weight_match.group()) if weight_match else 0.0
                            
                            # 智能解析实际重量
                            actual_weight_match = re.search(r'[\d.]+', actual_weight_candidate)
                            actual_weight = float(actual_weight_match.group()) if actual_weight_match else 0.0
                            
                            # 解析商品名称和ID（从商品信息列中进一步解析）
                            # 假设商品信息格式为 "商品ID-商品名称" 或类似格式
                            goods_id = ""
                            name = name_candidate
                            
                            # 如果需要从商品信息中分离ID和名称，可以添加解析逻辑
                            if '-' in name_candidate:
                                parts = name_candidate.split('-', 1)  # 分割成最多两部分
                                if len(parts) == 2:
                                    goods_id = parts[0].strip()
                                    name = parts[1].strip()
                            
                            # 创建商品对象
                            product = ProductInfo(
                                goods_id=goods_id,
                                name=name,
                                price=purchase_amount,  # 使用采购金额作为价格
                                stock=customer_quantity,  # 使用客户下单数量作为库存参考
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
                            
                    except Exception as parse_error:
                        print(f"解析行数据时出错: {parse_error}")
                        continue
                
                print(f"成功解析 {len(parsed_products)} 个商品")
                product_rows = parsed_products
            else:
                print("未收集到有效数据")
                product_rows = []
                
        except Exception as e:
            print(f"访问 iframe 失败: {e}")
            # 如果无法访问 iframe，继续在主页面查找
            product_rows = []
        
        print('product_rows-------->', len(product_rows))


        products = []
        for row in product_rows:
            try:
                # 提取商品信息 - 使用更灵活的选择器
                cells = await row.locator("td").all()
                
                if len(cells) >= 4:  # 确保有足够的列
                    # 获取单元格文本内容
                    cell_texts = []
                    for cell in cells:
                        text = await cell.text_content()
                        cell_texts.append(text.strip())
                    
                    # 根据实际列的含义分配值，而不是假设固定顺序
                    # 一般情况下，表格列可能是：商品ID、商品名称、价格、库存等
                    goods_id = cell_texts[0] if len(cell_texts) > 0 else ""
                    name = cell_texts[1] if len(cell_texts) > 1 else ""
                    price_candidate = cell_texts[2] if len(cell_texts) > 2 else ""
                    stock_candidate = cell_texts[3] if len(cell_texts) > 3 else ""
                    
                    # 智能解析价格：从文本中提取数字部分
                    import re
                    price_match = re.search(r'[\d,]+\.?\d*', price_candidate.replace(',', ''))
                    price = float(price_match.group()) if price_match else 0.0
                    
                    # 智能解析库存：提取数字部分
                    stock_match = re.search(r'\d+', stock_candidate)
                    stock = int(stock_match.group()) if stock_match else 0
                    
                    # 创建商品对象
                    product = ProductInfo(
                        goods_id=goods_id,
                        name=name,
                        price=price,
                        stock=stock,
                        platform="jushuitan"
                    )
                    products.append(product)
            except Exception as e:
                print(f"解析商品数据时出错: {e}")
                # 输出错误详情以便调试
                print(f"错误发生在处理行时，行内容可能为: {await row.text_content() if 'row' in locals() else 'unknown'}")
                continue
        
        await page.close()
        return products


class PddSpider:
    """拼多多平台爬虫"""
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.browser = None
        
    async def init_browser(self):
        """初始化浏览器"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        
    async def login(self):
        """登录拼多多商家后台"""
        if not self.browser:
            await self.init_browser()
            
        page = await self.browser.new_page()
        await page.goto("https://mms.pinduoduo.com/login")  # 实际URL可能不同
        
        # 输入用户名和密码
        await page.fill("#username-input", self.username)
        await page.fill("#password-input", self.password)
        
        # 点击登录按钮
        await page.click("#login-button")
        
        # 等待登录成功
        await page.wait_for_url("**/home**")
        
        return page
    
    async def get_products(self) -> List[ProductInfo]:
        """获取商品列表"""
        page = await self.login()
        
        # 导航到商品页面（示例）
        await page.goto("https://mms.pinduoduo.com/goods/list")
        
        # 获取商品列表（示例选择器，实际可能不同）
        product_elements = await page.locator(".goods-item").all()
        
        products = []
        for element in product_elements:
            # 提取商品信息（示例选择器，实际可能不同）
            goods_id = await element.locator(".goods-id").text_content()
            name = await element.locator(".goods-name").text_content()
            price_str = await element.locator(".goods-price").text_content()
            price = float(price_str.replace("¥", "").strip())
            stock_str = await element.locator(".goods-stock").text_content()
            stock = int(stock_str) if stock_str.isdigit() else 0
            
            product = ProductInfo(
                goods_id=goods_id.strip(),
                name=name.strip(),
                price=price,
                stock=stock,
                platform="pinduoduo"
            )
            products.append(product)
        
        await page.close()
        return products


async def crawl_all_platforms(jushuitan_creds: Dict, pdd_creds: Dict) -> Dict[str, List[ProductInfo]]:
    """爬取所有平台的数据"""
    results = {}
    
    # 爬取聚水潭数据
    if jushuitan_creds:
        jushuitan_spider = JushuitanSpider(jushuitan_creds['username'], jushuitan_creds['password'])
        results['jushuitan'] = await jushuitan_spider.get_products()
    
    # 爬取拼多多数据
    # if pdd_creds:
    #     pdd_spider = PddSpider(pdd_creds['username'], pdd_creds['password'])
    #     results['pinduoduo'] = await pdd_spider.get_products()
    
    return results


if __name__ == "__main__":
    """测试爬虫功能"""
    import os
    
    # 从环境变量获取凭据，或者使用测试值
    jushuitan_username = os.getenv("JUSHUITAN_USERNAME", "your_jushuitan_username")
    jushuitan_password = os.getenv("JUSHUITAN_PASSWORD", "your_jushuitan_password")
    pdd_username = os.getenv("PDD_USERNAME", "your_pdd_username")
    pdd_password = os.getenv("PDD_PASSWORD", "your_pdd_password")
    
    async def main():
        jushuitan_creds = {
            'username': '17607992526',
            'password': 'Aa12345600.'
        }
        
        pdd_creds = {
            'username': pdd_username,
            'password': pdd_password
        }
        
        # 爬取所有平台数据
        results = await crawl_all_platforms(jushuitan_creds, pdd_creds)
        
        # 打印结果
        for platform, products in results.items():
            print(f"\n{platform} 平台商品数量: {len(products)}")
            for product in products[:5]:  # 只显示前5个商品作为示例
                print(f"- 商品名称: {product.name}, 价格: {product.price}, 库存: {product.stock}")
    
    # 运行异步主函数
    asyncio.run(main())