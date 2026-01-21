import requests
import json

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



payload1 = {
    "startTime": "2026-01-01 00:00:00",
    "endTime": "2026-01-20 23:59:59",
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

# payload2 = {
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

resp = requests.post(url, headers=headers, json=payload1, timeout=15)
resp.raise_for_status()

data = resp.json()
print('data========>',  len(data['data']))
# print("总数:", data.get("data", {}).get("total"))
# print("本页条数:", len(data.get("data", {}).get("list", [])))
