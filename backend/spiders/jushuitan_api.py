import requests
import json
from datetime import datetime, timedelta

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



# 如果直接运行此脚本，则执行查询
# if __name__ == "__main__":
#     result = get_jushuitan_orders()
#     if result:
#         data = result.get("data", [])
#         print(f'data========> {len(data)}',  data[0])
#     else:
#         print('未能获取到聚水潭订单数据')