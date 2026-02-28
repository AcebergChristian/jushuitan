import requests
import json
from datetime import datetime, timedelta, date


authorization = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiIyMDExNjY1MSIsInJvbGVJZHMiOltdLCJ1c2VyX25hbWUiOiIxNTE3OTkwMzQ3NyIsImNvSWQiOiIxNDQ4MjExMyIsImV4cGlyYXRpb24iOjE3NzMwMjE5MDA2MTQsInVzZXIiOnsiY29JZCI6IjE0NDgyMTEzIiwiY29OYW1lIjoiMTc2NzkyOTYwNDIiLCJsb2dpbk5hbWUiOiIxNTE3OTkwMzQ3NyIsImxvZ2luV2F5IjoiVVNFUk5BTUUiLCJuaWNrTmFtZSI6IuiQjSIsInJvbGVJZHMiOiIxMSIsInVpZCI6IjIwMTE2NjUxIn0sImF1dGhvcml0aWVzIjpbIkpTVC1jaGFubmVsIiwiSlNULXN1cHBsaWVyIiwibXVsdGlMb2dpbiJdLCJjbGllbnRfaWQiOiJwYyIsImp0aSI6IjE1MTU2NTdmLTkyMmQtNDZhMS05NGVkLThkYmE1NTc0OTZlYSIsImV4cCI6MTc3MzAyMTkwMH0.F1ehLc62lAkaStgVmyhGQgSDiDgA8rvC2SAOLnKuPjU"

# 销售金额 = 待推单审核+异常+待发货+已发货+被拆分+已取消
# 销售成本 = 待推单审核+异常+待发货+已发货


# 获取销售金额订单数据（包含所有状态）
def get_jushuitan_orders_for_sales_amount(sync_date=None):
    """
    获取用于计算销售金额的订单数据
    orderStatus: ["WaitConfirm", "WaitOuterSent", "Sent", "Split", "Cancelled", "Question", "Delivering"]
    """
    url = "https://innerapi.scm121.com/api/inner/order/list"

    headers = {
        "authorization": authorization,
        "content-type": "application/json;charset=UTF-8",
        "origin": "https://innerorder.scm121.com",
        "referer": "https://innerorder.scm121.com/distribute",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/144.0.0.0 Safari/537.36",
        "appcode": "sc.scm121.com",
        "app-version": "TOWER_20260207204353",
        "source": "SUPPLIER"
    }

    # 如果没有提供sync_date，则默认使用前一天的日期
    if sync_date is None:
        yesterday = datetime.now() - timedelta(days=1)
        sync_date = yesterday.strftime("%Y-%m-%d")
    elif isinstance(sync_date, date):
        sync_date = sync_date.strftime("%Y-%m-%d")

    # 设置当天的开始和结束时间
    start_time = f"{sync_date} 00:00:00"
    end_time = f"{sync_date} 23:59:59"

    payload = {
        "startTime": start_time,
        "endTime": end_time,
        "dateQueryType": "OrderDate",
        "orderTypeEnum": "ALL",
        "orderStatus": ["WaitConfirm", "WaitOuterSent", "Sent", "Split", "Cancelled", "Question", "Delivering"],
        "noteType": "NOFILTER",
        "orderByKey": 4,
        "ascOrDesc": True,
        "coId": "14482113",
        "uid": "20116651",
        "pageNum": 1,
        "pageSize": 500,
        "searchType": 1
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()

        data = resp.json()
        order_count = len(data.get('data', []))
        print(f'成功获取销售金额订单数据，共{order_count}条记录')

        return data

    except requests.exceptions.RequestException as e:
        print(f'请求聚水潭API失败: {e}')
        return None
    except Exception as e:
        print(f'处理聚水潭数据时发生错误: {e}')
        return None


# 获取销售成本订单数据（不包含已取消和被拆分）
def get_jushuitan_orders_for_sales_cost(sync_date=None):
    """
    获取用于计算销售成本的订单数据
    orderStatus: ["WaitConfirm", "WaitOuterSent", "Sent", "Question", "Delivering"]
    """
    url = "https://innerapi.scm121.com/api/inner/order/list"

    headers = {
        "authorization": authorization,
        "content-type": "application/json;charset=UTF-8",
        "origin": "https://innerorder.scm121.com",
        "referer": "https://innerorder.scm121.com/distribute",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/144.0.0.0 Safari/537.36",
        "appcode": "sc.scm121.com",
        "app-version": "TOWER_20260207204353",
        "source": "SUPPLIER"
    }

    # 如果没有提供sync_date，则默认使用前一天的日期
    if sync_date is None:
        yesterday = datetime.now() - timedelta(days=1)
        sync_date = yesterday.strftime("%Y-%m-%d")
    elif isinstance(sync_date, date):
        sync_date = sync_date.strftime("%Y-%m-%d")

    # 设置当天的开始和结束时间
    start_time = f"{sync_date} 00:00:00"
    end_time = f"{sync_date} 23:59:59"

    payload = {
        "startTime": start_time,
        "endTime": end_time,
        "dateQueryType": "OrderDate",
        "orderTypeEnum": "ALL",
        "orderStatus": ["WaitConfirm", "WaitOuterSent", "Sent", "Question", "Delivering"],
        "noteType": "NOFILTER",
        "orderByKey": 4,
        "ascOrDesc": True,
        "coId": "14482113",
        "uid": "20116651",
        "pageNum": 1,
        "pageSize": 500,
        "searchType": 1
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()

        data = resp.json()
        order_count = len(data.get('data', []))
        print(f'成功获取销售成本订单数据，共{order_count}条记录')

        return data

    except requests.exceptions.RequestException as e:
        print(f'请求聚水潭API失败: {e}')
        return None
    except Exception as e:
        print(f'处理聚水潭数据时发生错误: {e}')
        return None


# 获取所有聚水潭订单数据（保留旧方法以兼容）
def get_all_jushuitan_orders(sync_date=None):
    """
    获取聚水潭订单数据，支持查询指定时间段内的所有订单
    如果未提供日期范围，则默认查询最近7天的订单
    """
    url = "https://innerapi.scm121.com/api/inner/order/list"

    headers = {
        "authorization": authorization,
        "content-type": "application/json;charset=UTF-8",
        "origin": "https://innerorder.scm121.com",
        "referer": "https://innerorder.scm121.com/distribute",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/141.0.0.0 Safari/537.36",
        "appcode": "sc.scm121.com",
        "app-version": "TOWER_20260116204226",
        "source": "SUPPLIER"
    }

    # 如果没有提供sync_date，则默认使用前一天的日期
    if sync_date is None:
        yesterday = datetime.now() - timedelta(days=1)
        sync_date = yesterday.strftime("%Y-%m-%d")
    elif isinstance(sync_date, date):
        # 如果传入的是date对象，转换为字符串
        sync_date = sync_date.strftime("%Y-%m-%d")

    # 设置当天的开始和结束时间
    start_time = f"{sync_date} 00:00:00"
    end_time = f"{sync_date} 23:59:59"

    payload = {
        "startTime": start_time,
        "endTime": end_time,
        "dateQueryType": "OrderDate",
        "orderTypeEnum": "ALL",
        "orderStatus": ["WaitConfirm", "WaitOuterSent", "Sent", "Question", "Delivering"],
        "noteType": "NOFILTER",
        "orderByKey": 0,
        "ascOrDesc": False,
        "coId": "14482113",
        "uid": "22227282",
        "pageNum": 1,
        "pageSize": 9999,
        "searchType": 1
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()

        data = resp.json()
        order_count = len(data.get('data', []))
        print(f'成功获取聚水潭订单数据，共{order_count}条记录')

        return data

    except requests.exceptions.RequestException as e:
        print(f'请求聚水潭API失败: {e}')
        return None
    except Exception as e:
        print(f'处理聚水潭数据时发生错误: {e}')
        return None








# 获取所有订单数据 用来与售后数据联查得到refund_amount
def get_all_jushuitan_orders_with_refund(sync_date=None):
    """
    获取聚水潭订单数据，支持查询指定时间段内的所有订单
    如果未提供日期范围，则默认查询最近7天的订单
    """
    url = "https://innerapi.scm121.com/api/inner/order/list"

    headers = {
        "authorization": authorization,
        "content-type": "application/json;charset=UTF-8",
        "origin": "https://innerorder.scm121.com",
        "referer": "https://innerorder.scm121.com/distribute",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/141.0.0.0 Safari/537.36",
        "appcode": "sc.scm121.com",
        "app-version": "TOWER_20260116204226",
        "source": "SUPPLIER"
    }

    # 如果没有提供sync_date，则默认使用前一天的日期
    if sync_date is None:
        yesterday = datetime.now() - timedelta(days=1)
        sync_date = yesterday.strftime("%Y-%m-%d")
    elif isinstance(sync_date, date):
        # 如果传入的是date对象，转换为字符串
        sync_date = sync_date.strftime("%Y-%m-%d")

    # 设置当天的开始和结束时间
    start_time = f"{sync_date} 00:00:00"
    end_time = f"{sync_date} 23:59:59"

    payload = {
        "startTime": start_time,
        "endTime": end_time,
        "dateQueryType": "OrderDate",
        "orderTypeEnum": "ALL",
        "noteType": "NOFILTER",
        "orderByKey": 0,
        "ascOrDesc": False,
        "coId": "14482113",
        "uid": "20116651",
        "pageNum": 1,
        "pageSize": 9999,
        "searchType": 1
    }


    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()

        data = resp.json()
        order_count = len(data.get('data', []))
        print(f'成功获取聚水潭订单数据，共{order_count}条记录')

        return data

    except requests.exceptions.RequestException as e:
        print(f'请求聚水潭API失败: {e}')
        return None
    except Exception as e:
        print(f'处理聚水潭数据时发生错误: {e}')
        return None



# 通过售后页面获取退款数据
def get_cancel_jushuitan_from_shouhou(date=None):
    """
    获取聚水潭售后订单数据，支持查询指定时间段内的所有售后订单
    如果未提供日期范围，则默认查询最近7天的售后订单
    """
    url = "https://innerapi.scm121.com/api/inner/after-sale/page/list"

    headers = {
        "authorization": authorization,
        "content-type": "application/json;charset=UTF-8",
        "origin": "https://innerorder.scm121.com",
        "referer": "https://innerorder.scm121.com/afterSales",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "appcode": "sc.scm121.com",
        "app-version": "TOWER_20260130202757",
        "source": "SUPPLIER",
        "accept": "application/json",
        "accept-language": "zh-CN,zh;q=0.9",
        "gwfp": "180fcdc0c0f8aa459761e4b59acf09a5"
    }

    # 如果没有提供date，则默认使用前一天的日期
    if date is None:
        today = datetime.now()
        date = today.strftime("%Y-%m-%d")

    # 设置当天的开始和结束时间
    confirm_start_time = f"{date} 00:00:00"
    confirm_end_time = f"{date} 23:59:59"

    payload = {
        "coId": "14482113",
        "uid": "20116651",
        "searchType": 1,
        "confirmStartTime": confirm_start_time,
        "confirmEndTime": confirm_end_time,
        "querySortDTO": {
            "shopEndDate": False
        },
        "isWhite": 1,
        "afterSaleStatus": ["Confirmed"],
        "pageNum": 1,
        "pageSize": 9999  # 获取所有记录
    }


    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()

        data = resp.json()
        order_count = len(data.get('data', []))

        print(f"获取到 {order_count} 条售后订单记录")
        return data

    except requests.exceptions.RequestException as e:
        print(f'请求聚水潭售后API失败: {e}')
        return None
    except Exception as e:
        print(f'处理聚水潭售后数据时发生错误: {e}')
        return None



# 查售后订单数据 获取acqiure接口数据 参数日期和oidlist
def acquire_all_simple_orders(oid_list):
    """
    获取售后订单的详细数据
    
    参数:
        oid_list: 订单ID列表
        page_num: 页码，默认为1
        page_size: 每页数量，默认为50
    
    返回:
        订单详细数据
    """
    url = "https://innerapi.scm121.com/api/inner/order/acquireAllSimpleOrders"
    
    headers = {
        "accept": "application/json",
        "accept-language": "zh-CN,zh;q=0.9",
        "app-version": "TOWER_20260205204706",
        "appcode": "sc.scm121.com",
        "authorization": authorization,
        "content-type": "application/json;charset=UTF-8",
        "gwfp": "180fcdc0c0f8aa459761e4b59acf09a5",
        "origin": "https://innerorder.scm121.com",
        "referer": "https://innerorder.scm121.com/afterSales",
        "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "source": "SUPPLIER",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
    }
    
    payload = {
        "oidList": oid_list,
        "pageSize": 1,
        "pageNum": 9999
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        
        data = resp.json()
        order_count = len(data.get('data', []))
        print(f'成功获取售后订单详细数据，共{order_count}条记录')
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f'请求聚水潭售后订单详细API失败: {e}')
        return None
    except Exception as e:
        print(f'处理聚水潭售后订单详细数据时发生错误: {e}')
        return None







# 如果直接运行此脚本，则执行查询
# if __name__ == "__main__":
#     result = get_cancel_jushuitan_from_shouhou(date="2026-01-26")
#     if result:
#         data = result.get("data", [])
#         print(f'data========> {len(data)}')
#     else:
#         print('未能获取到聚水潭订单数据')
