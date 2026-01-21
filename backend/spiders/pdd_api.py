import requests
import json

url = "https://yingxiao.pinduoduo.com/mms-gateway/venus/api/goods/promotion/v1/list"

headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9",
    "content-type": "application/json",
    "origin": "https://yingxiao.pinduoduo.com",
    "referer": "https://yingxiao.pinduoduo.com/goods/promotion/list?msfrom=mms_sidenav",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    
    # 🔥 关键反爬参数
    "anti-content": "0asAfqn55iQoU99xvHB2Jm_fMX5BlJudACW0TS8a2Xkf2VOzfK40YZbiCSi40Cx-hCw66pj4aCnJ28u5tlf1xa9-hC2Y6OhRAzi3tvU_et7w-yZw2TWTDZVb7VnQk3gnQ_7QGgq39gmmRr6XsIoC9htTNVSGgL0Af_9dV0gDUxigMSIkWarEv5RJQJkkAYFvpjWXG4BgXP-nIw0IBcB1kULXFdv7zYGYUM-rH7DyXjmzZiOWUXeN82wT_2IAyXk4V3Q5UgYsP_22P2l0YC9Pxm77py6tF6gq0deOtZ9wvv7v9jUzbjGcJy9Bfywd4W0BmN2k3PNf297HPfR27IAqshThNU8Lyp2F46IMgvlUHc2oijkyLbcun6x_w2jII1U8-ubWhhh3-QB-K-878AIVS7DrA3ehYOui_I5dcUKa_YWhbOyajvLUYi_1wRHaJoH9k8Jboa",

    # ⚠️ 营销系统上下文
    "adbiz-front-trace-id": "cGNfMTc2ODk2MzcwOTI1OF9wcm9tb3Rpb25fNWI1M2Y0OWQtNzY2Ny00ZGRjLTk5NDYtZTQ5OWU3MGU5Yzg4",
    "adbiz-page-enter-time": "1768963708590",
    "adbiz-page-version": "v20260119.17.16.44-1113",
    
    # 🔐 安全相关头部
    "priority": "u=1, i",
    "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",

    # 🍪 Cookie 原样
    "cookie": "_a42=386ba908-471c-4b9d-af6d-4a6bdb864a66; _bee=hLBIWqdPbG9KmuR61y1cMuEu1YCxYQ7b; _f77=6e928cbe-c1ca-443d-b1f0-b17187327621; _nano_fp=Xpmjl0CJlpXJlpTbXo_FIMEr7tOdempOVQeEZl1q; api_uid=Ck9MdGlvHC1LLQBZQjvSAg==; rckk=hLBIWqdPbG9KmuR61y1cMuEu1YCxYQ7b; ru1k=6e928cbe-c1ca-443d-b1f0-b17187327621; ru2k=386ba908-471c-4b9d-af6d-4a6bdb864a66; SUB_PASS_ID=eyJ0IjoiRmp6SjJQbEg0YWgzQWZYNG9Dbkd6c3MxaERWUkl6N1NSU21kYUNLc29xcUJTV0NnWVRrT0xLbHpZU1YvWTh0VyIsInYiOjEsInMiOjcsIm0iOjI2MzU2NDc4OSwidSI6MTczNzA1NTIyfQ; SUB_SYSTEM_ID=7; windows_app_shop_token_23=eyJ0IjoiSFhuNXNjQjhrNDlqNXVKajY3QVJEaVNDU1UySS94czk1NER6cUZRUmFVODEzUS9CMzFkS3c3TG5RdGhuV0p5ZSIsInYiOjEsInMiOjIzLCJtIjoyNjM1NjQ3ODksInUiOjE3MzcwNTUyMn0"
}

payload = {
    "crawlerInfo": "0asAfqn55iQoU99xvHB2Jm_fMX5BlJudACW0TS8a2Xkf2VOzfK40YZbiCSi40Cx-hCw66pj4aCnJ28u5tlf1xa9-hC2Y6OhRAzi3tvU_et7w-yZw2TWTDZVb7VnQk3gnQ_7QGgq39gmmRr6XsIoC9htTNVSGgL0Af_9dV0gDUxigMSIkWarEv5RJQJkkAYFvpjWXG4BgXP-nIw0IBcB1kULXFdv7zYGYUM-rH7DyXjmzZiOWUXeN82wT_2IAyXk4V3Q5UgYsP_22P2l0YC9Pxm77py6tF6gq0deOtZ9wvv7v9jUzbjGcJy9Bfywd4W0BmN2k3PNf297HPfR27IAqshThNU8Lyp2F46IMgvlUHc2oijkyLbcun6x_w2jII1U8-ubWhhh3-QB-K-878AIVS7DrA3ehYOui_I5dcUKa_YWhbOyajvLUYi_1wRHaJoH9k8Jboa",
    "clientType": 1,
    "blockType": 3,
    "beginDate": "2026-01-21",
    "endDate": "2026-01-21",
    "pageNumber": 1,
    "pageSize": 50,
    "sortBy": 9999,
    "orderBy": 9999,
    "filter": {},
    "scenesMode": 1
}

resp = requests.post(url, headers=headers, json=payload, timeout=15)
print(resp.status_code)
print(len(resp.json().get('result').get('adInfos')))
