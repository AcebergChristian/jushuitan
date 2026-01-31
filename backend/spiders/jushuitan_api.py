import requests
import json
from datetime import datetime, timedelta, date

def get_jushuitan_orders(sync_date=None):
    """
    获取聚水潭订单数据，默认查询前一天的所有订单
    """
    url = "https://innerapi.scm121.com/api/inner/order/list"

    headers = {
        "authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiIyMjIyNzI4MiIsInJvbGVJZHMiOltdLCJ1c2VyX25hbWUiOiIxNzYwNzk5MjUyNiIsImNvSWQiOiIxNDQ4MjExMyIsImV4cGlyYXRpb24iOjE3Njk1MTk3NDA4NTMsInVzZXIiOnsiY29JZCI6IjE0NDgyMTEzIiwiY29OYW1lIjoiMTc2NzkyOTYwNDIiLCJsb2dpbk5hbWUiOiIxNzYwNzk5MjUyNiIsImxvZ2luV2F5IjoiVVNFUk5BTUUiLCJuaWNrTmFtZSI6Iua1i-ivlWVycCIsInJvbGVJZHMiOiIxMDMiLCJ1aWQiOiIyMjIyNzI4MiJ9LCJhdXRob3JpdGllcyI6WyJKU1QtY2hhbm5lbCIsIm11bHRpTG9naW4iLCJKU1Qtc3VwcGxpZXIiXSwiY2xpZW50X2lkIjoicGMiLCJqdGkiOiI4YzMxNTM3Yi0wY2M4LTQ2NGUtODA0Zi0yNzkzYWZmODM0MjQiLCJleHAiOjE3Njk1MTk3NDB9.wHfimSEOLEF607G0UoVmBfPV0ZZW3lJAP_JQp1qhHp0",
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
        "uid": "22227282",
        "pageNum": 1,
        "pageSize": 999,
        "searchType": 1
    }

    # payload = {
    #     "dateQueryType": "OrderDate",
    #     "orderTypeEnum": "ALL",
    #     "noteType": "NOFILTER",
    #     "orderByKey": 0,
    #     "ascOrDesc": False,
    #     "orderStatus": [
    #         "WaitPay",
    #         "WaitConfirm",
    #         "WaitOuterSent",
    #         "Sent",
    #         "Question",
    #         "Delivering",
    #         "WaitFConfirm",
    #         "OuterSent"
    #     ],
    #     "coId": "14482113",
    #     "uid": "22227282",
    #     "pageNum": 1,
    #     "pageSize": 999,
    #     "searchType": 1
    # }

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



# 获取所有聚水潭订单数据
def get_all_jushuitan_orders(sync_date=None):
    """
    获取聚水潭订单数据，支持查询指定时间段内的所有订单
    如果未提供日期范围，则默认查询最近7天的订单
    """
    url = "https://innerapi.scm121.com/api/inner/order/list"

    headers = {
        "authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiIyMDExNjY1MSIsInJvbGVJZHMiOltdLCJ1c2VyX25hbWUiOiIxNTE3OTkwMzQ3NyIsImNvSWQiOiIxNDQ4MjExMyIsImV4cGlyYXRpb24iOjE3NzAzNjY2NzkyMDUsInVzZXIiOnsiY29JZCI6IjE0NDgyMTEzIiwiY29OYW1lIjoiMTc2NzkyOTYwNDIiLCJsb2dpbk5hbWUiOiIxNTE3OTkwMzQ3NyIsImxvZ2luV2F5IjoiVVNFUk5BTUUiLCJuaWNrTmFtZSI6IuiQjSIsInJvbGVJZHMiOiIxMSIsInVpZCI6IjIwMTE2NjUxIn0sImF1dGhvcml0aWVzIjpbIkpTVC1jaGFubmVsIiwibXVsdGlMb2dpbiIsIkpTVC1zdXBwbGllciJdLCJjbGllbnRfaWQiOiJwYyIsImp0aSI6Ijk1NzBmNTNkLWY5ODYtNDQ0YS1iYzZlLTJjY2UyYTk2YmQ3ZiIsImV4cCI6MTc3MDM2NjY3OX0.lhHgB_VpuzTBaxDqnBKlLyz5U5vTLn7tYFktr-tNpcU",
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
        "orderStatus":["WaitConfirm","WaitOuterSent","Sent","Question","Delivering"],
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
  



# 获取被取消的聚水潭订单数据
def get_cancel_jushuitan_from_allorders(date=None):
    """
    获取聚水潭订单数据，支持查询指定时间段内的所有订单
    如果未提供日期范围，则默认查询最近7天的订单
    """
    url = "https://innerapi.scm121.com/api/inner/order/list"

    headers = {
        "authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiIyMDExNjY1MSIsInJvbGVJZHMiOltdLCJ1c2VyX25hbWUiOiIxNTE3OTkwMzQ3NyIsImNvSWQiOiIxNDQ4MjExMyIsImV4cGlyYXRpb24iOjE3NzAzNjY2NzkyMDUsInVzZXIiOnsiY29JZCI6IjE0NDgyMTEzIiwiY29OYW1lIjoiMTc2NzkyOTYwNDIiLCJsb2dpbk5hbWUiOiIxNTE3OTkwMzQ3NyIsImxvZ2luV2F5IjoiVVNFUk5BTUUiLCJuaWNrTmFtZSI6IuiQjSIsInJvbGVJZHMiOiIxMSIsInVpZCI6IjIwMTE2NjUxIn0sImF1dGhvcml0aWVzIjpbIkpTVC1jaGFubmVsIiwibXVsdGlMb2dpbiIsIkpTVC1zdXBwbGllciJdLCJjbGllbnRfaWQiOiJwYyIsImp0aSI6Ijk1NzBmNTNkLWY5ODYtNDQ0YS1iYzZlLTJjY2UyYTk2YmQ3ZiIsImV4cCI6MTc3MDM2NjY3OX0.lhHgB_VpuzTBaxDqnBKlLyz5U5vTLn7tYFktr-tNpcU",
        "content-type": "application/json;charset=UTF-8",
        "origin": "https://innerorder.scm121.com",
        "referer": "https://innerorder.scm121.com/distribute",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/141.0.0.0 Safari/537.36",
        "appcode": "sc.scm121.com",
        "app-version": "TOWER_20260116204226",
        "source": "SUPPLIER"
    }

    # 如果没有提供sync_date，则默认使用前一天的日期
    if date is None:
        today = datetime.now()
        date = today.strftime("%Y-%m-%d")
        
    
    # 设置当天的开始和结束时间
    start_time = f"{date} 00:00:00"
    end_time = f"{date} 23:59:59"

    payload = {
        "startTime": start_time,
        "endTime": end_time,
        "dateQueryType": "OrderDate",
        "orderTypeEnum": "ALL",
        "orderStatus":["WaitConfirm","WaitOuterSent","Sent","Question","Delivering"],
        "noteType": "NOFILTER",
        "orderByKey": 0,
        "ascOrDesc": False,
        "coId": "14482113",
        "uid": "22227282",
        "pageNum": 1,
        "pageSize": 9999,
        "searchType": 1
    }

    print(payload)
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        
        data = resp.json()
        order_count = len(data.get('data', []))
        
        print("data.get('data', [])[0:1]", data.get('data', [])[0:1])
        return data
        
    except requests.exceptions.RequestException as e:
        print(f'请求聚水潭API失败: {e}')
        return None
    except Exception as e:
        print(f'处理聚水潭数据时发生错误: {e}')
        return None




# 获取 售后订单数据 list接口
# def get_cancel_jushuitan_shouhouorders(startdate=None, enddate=None, oid_list=None):
#     """
#         获取聚水潭订单数据，支持查询指定时间段内的所有订单
#         如果未提供日期范围，则默认查询最近7天的订单
#         现在使用 acquireAllSimpleOrders API 获取包含特定标签的订单
#     """
#     url = "https://innerapi.scm121.com/api/inner/after-sale/page/list"

#     headers = {
#         "accept": "application/json",
#         "accept-language": "zh-CN,zh;q=0.9",
#         "app-version": "TOWER_20260129220440",
#         "appcode": "sc.scm121.com",
#         "authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiIyMDExNjY1MSIsInJvbGVJZHMiOltdLCJ1c2VyX25hbWUiOiIxNTE3OTkwMzQ3NyIsImNvSWQiOiIxNDQ4MjExMyIsImV4cGlyYXRpb24iOjE3NzAzNjY2NzkyMDUsInVzZXIiOnsiY29JZCI6IjE0NDgyMTEzIiwiY29OYW1lIjoiMTc2NzkyOTYwNDIiLCJsb2dpbk5hbWUiOiIxNTE3OTkwMzQ3NyIsImxvZ2luV2F5IjoiVVNFUk5BTUUiLCJuaWNrTmFtZSI6IuiQjSIsInJvbGVJZHMiOiIxMSIsInVpZCI6IjIwMTE2NjUxIn0sImF1dGhvcml0aWVzIjpbIkpTVC1jaGFubmVsIiwibXVsdGlMb2dpbiIsIkpTVC1zdXBwbGllciJdLCJjbGllbnRfaWQiOiJwYyIsImp0aSI6Ijk1NzBmNTNkLWY5ODYtNDQ0YS1iYzZlLTJjY2UyYTk2YmQ3ZiIsImV4cCI6MTc3MDM2NjY3OX0.lhHgB_VpuzTBaxDqnBKlLyz5U5vTLn7tYFktr-tNpcU",
#         "content-type": "application/json;charset=UTF-8",
#         "gwfp": "f70e214f0437e583f00459f083004911",
#         "origin": "https://innerorder.scm121.com",
#         "priority": "u=1, i",
#         "referer": "https://innerorder.scm121.com/afterSales",
#         "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
#         "sec-ch-ua-mobile": "?0",
#         "sec-ch-ua-platform": '"macOS"',
#         "sec-fetch-dest": "empty",
#         "sec-fetch-mode": "cors",
#         "sec-fetch-site": "same-site",
#         "source": "SUPPLIER",
#         "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
#     }

#     # 如果没有提供日期范围，使用默认逻辑
#     if startdate and enddate:
#         pass
#     else:
#         yesterday = datetime.now() - timedelta(days=1)
#         startdate = yesterday.strftime("%Y-%m-%d")
#         enddate = datetime.now().strftime("%Y-%m-%d")

#     start_time = f"{startdate} 00:00:00"
#     end_time = f"{enddate} 00:00:00"

#     payload = {
#         "coId": "14482113",
#         "uid": "20116651",
#         "searchType": 1,
#         "confirmStartTime": start_time,
#         "confirmEndTime": end_time,
#         "querySortDTO": {
#             "shopEndDate": False
#         },
#         "isWhite": 1,
#         "afterSaleStatus": ["WaitConfirm", "Confirmed"],
#         "pageNum": 1,
#         "pageSize": 9999
#     }
#     try:
#         resp = requests.post(url, headers=headers, json=payload, timeout=15)
#         resp.raise_for_status()
        
#         data = resp.json()
#         order_count = len(data.get('data', []))
#         print(f'成功获取聚水潭取消订单的数据，共{order_count}条记录')
        
#         return data
        
#     except requests.exceptions.RequestException as e:
#         print(f'请求聚水潭API失败: {e}')
#         return None
#     except Exception as e:
#         print(f'处理聚水潭数据时发生错误: {e}')
#         return None





# # 通过订单ID列表获取订单详细信息
# def get_cancel_jushuitan_orders_oidlist(startdate=None, enddate=None, oid_list=None):
#     """
#     通过订单ID列表获取订单详细信息
#     """
#     url = "https://innerapi.scm121.com/api/inner/order/acquireAllSimpleOrders"

#     headers = {
#         "accept": "application/json",
#         "accept-language": "zh-CN,zh;q=0.9",
#         "app-version": "TOWER_20260129220440",
#         "appcode": "sc.scm121.com",
#         "authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiIyMDExNjY1MSIsInJvbGVJZHMiOltdLCJ1c2VyX25hbWUiOiIxNTE3OTkwMzQ3NyIsImNvSWQiOiIxNDQ4MjExMyIsImV4cGlyYXRpb24iOjE3NzAzNjY2NzkyMDUsInVzZXIiOnsiY29JZCI6IjE0NDgyMTEzIiwiY29OYW1lIjoiMTc2NzkyOTYwNDIiLCJsb2dpbk5hbWUiOiIxNTE3OTkwMzQ3NyIsImxvZ2luV2F5IjoiVVNFUk5BTUUiLCJuaWNrTmFtZSI6IuiQjSIsInJvbGVJZHMiOiIxMSIsInVpZCI6IjIwMTE2NjUxIn0sImF1dGhvcml0aWVzIjpbIkpTVC1jaGFubmVsIiwibXVsdGlMb2dpbiIsIkpTVC1zdXBwbGllciJdLCJjbGllbnRfaWQiOiJwYyIsImp0aSI6Ijk1NzBmNTNkLWY5ODYtNDQ0YS1iYzZlLTJjY2UyYTk2YmQ3ZiIsImV4cCI6MTc3MDM2NjY3OX0.lhHgB_VpuzTBaxDqnBKlLyz5U5vTLn7tYFktr-tNpcU",
#         "content-type": "application/json;charset=UTF-8",
#         "gwfp": "f70e214f0437e583f00459f083004911",
#         "origin": "https://innerorder.scm121.com",
#         "priority": "u=1, i",
#         "referer": "https://innerorder.scm121.com/afterSales",
#         "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
#         "sec-ch-ua-mobile": "?0",
#         "sec-ch-ua-platform": '"macOS"',
#         "sec-fetch-dest": "empty",
#         "sec-fetch-mode": "cors",
#         "sec-fetch-site": "same-site",
#         "source": "SUPPLIER",
#         "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
#     }

#     # 如果oid_list为空，返回空数据
#     # if not oid_list:
#     #     print("订单ID列表为空，返回空数据")
#     #     return {"data": []}

#     # 设置时间范围（如果提供的话）
#     payload = {
#         "oidList": [],
#         "pageSize": 9999,
#         "pageNum": 1
#     }

#     # 如果提供了时间范围，添加到请求中
#     if startdate and enddate:
#         payload["startTime"] = f"{startdate} 00:00:00"
#         payload["endTime"] = f"{enddate} 23:59:59"

#     print(payload)
#     try:
#         resp = requests.post(url, headers=headers, json=payload, timeout=15)
#         resp.raise_for_status()
        
#         data = resp.json()
        
#         order_count = len(data.get('data', []))
#         print(f'成功获取订单详细信息，共{order_count}条记录')
        
        
#         return data
        
#     except requests.exceptions.RequestException as e:
#         print(f'请求聚水潭API失败: {e}')
#         return None
#     except Exception as e:
#         print(f'处理聚水潭数据时发生错误: {e}')
#         return None


# 如果直接运行此脚本，则执行查询
# if __name__ == "__main__":
#     result = get_cancel_jushuitan_orders_oidlist(startdate="2026-01-26", enddate="2026-01-26")
#     if result:
#         data = result.get("data", [])
#         print(f'data========> {len(data)}', data[0:30])
#     else:
#         print('未能获取到聚水潭订单数据')