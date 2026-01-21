# import requests
# import json

# url = "https://yingxiao.pinduoduo.com/mms-gateway/venus/api/goods/promotion/v1/list"

# headers = {
#     "content-type": "application/json;charset=UTF-8",
#     "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
#     "origin": "https://yingxiao.pinduoduo.com",
#     "referer": "https://yingxiao.pinduoduo.com/goods/promotion/list?msfrom=mms_sidenav",
#     # ⚠️ 必须从浏览器 Network → Request Headers 里完整复制
#     "cookie": "_a42=386ba908-471c-4b9d-af6d-4a6bdb864a66; _bee=hLBIWqdPbG9KmuR61y1cMuEu1YCxYQ7b; _f77=6e928cbe-c1ca-443d-b1f0-b17187327621; _nano_fp=Xpmjl0CJlpXJlpTbXo_FIMEr7tOdempOVQeEZl1q; api_uid=Ck9MdGlvHC1LLQBZQjvSAg==; rckk=hLBIWqdPbG9KmuR61y1cMuEu1YCxYQ7b; ru1k=6e928cbe-c1ca-443d-b1f0-b17187327621; ru2k=386ba908-471c-4b9d-af6d-4a6bdb864a66; SUB_PASS_ID=eyJ0IjoiRmp6SjJQbEg0YWgzQWZYNG9Dbkd6c3MxaERWUkl6N1NSU21kYUNLc29xcUJTV0NnWVRrT0xLbHpZU1YvWTh0VyIsInYiOjEsInMiOjcsIm0iOjI2MzU2NDc4OSwidSI6MTczNzA1NTIyfQ; SUB_SYSTEM_ID=7; windows_app_shop_token_23=eyJ0IjoiSFhuNXNjQjhrNDlqNXVKajY3QVJEaVNDU1UySS94czk1NER6cUZRUmFVODEzUS9CMzFkS3c3TG5RdGhuV0p5ZSIsInYiOjEsInMiOjIzLCJtIjoyNjM1NjQ3ODksInUiOjE3MzcwNTUyMn0"
# }

# payload = {
#     "crawlerInfo": "0asWfqnUFjlaF99ZzO7GUq9e7zM4der6DsvBZwOR2XDf22c80_s0U9arTxyPl4t1e-6utsmGR9sU6hEHKxGgruWaf1b9QQW8Jx3GJF17kGFZzFk4N6UPaUEf2Ic5XNdpIfVawPH9xm4g7n20QMuZdaTsFsteSgDxOXgsXPaiMP_bXZC_SoCibQ53vmEzMyEMwm_AQnTYDOKmRSB9pfyyitwH5z4s3h5W3tRCC6Ek08pzVh6EwntCDV1tOVbvK2gVOEUej4Q2teV9D0z9_39IKuyYN54ghudERsRVa5K3Ta-1bnXKikjMoh9F5FBzpqeO5qaxN-00sgWtWIoTXuCRSQqni-FE23lIBICdRbMLCkA3-EIpS-h5sD9TiLLmlnqULGkYmRm08-rDU-2-_3HnMK888WiiMpkteytZuWAfvShoCcOoF1oNFuIiTQgpEqH9D8Jbav",
#     "clientType": 1,
#     "blockType": 3,
#     "beginDate": "2026-01-10",
#     "endDate": "2026-01-11",
#     "pageNumber": 1,
#     "pageSize": 50,
#     "sortBy": 9999,
#     "orderBy": 9999,
#     "filter": {},
#     "scenesMode": 1
# }

# resp = requests.post(url, headers=headers, json=payload, timeout=15)
# resp.raise_for_status()

# data = resp.json()
# print("返回 code:", data.get("code"))
# print("商品条数:", len(data.get("result", {}).get("list", [])))



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
    "anti-content": "0asAfqn5HjlaF99V_-0CaiCm0sJ2tlioepRkv4abdiSUg4aEzFtAbgGcry7zCCbXeHb49LLRCtRCDh5UJgymWd2HPUQEXb3q3uYUKXzdZFVIvmMmmq5gaCJf2qoZmcgpUf1qwtG6CoC-0g1CMY29VEpsUftSoCNZgEft9e23gpgxLBr_VjRQJZFYi8oMWK26hdnwvdFzukTDhZsEL_KhIgZpvByo6qjGuFM-DO7uyX8m8BicnCnSu_sZZZ2HlvLfPxen0Us5p0Bs4T9cGo92UVqUlfSlv0-MlfHQBq_B4IqfOSIq0DHQkcj24ZeEv00JSYFC0Ff6-tP4UZdWCzLrOVuUG1fn-oYEgSFN3fqlyFok0lM8H9I4qjhRY5Cr7b6vaEdYz11J7YX-0Q0N-cyvpuwIiz3B6_-I83374aRrpyGiR1iLo3HLUJb_tu19XX4W2d2HDW51",

    # ⚠️ 营销系统上下文
    "adbiz-front-trace-id": "cGNfMTc2ODk2MTc1NTYzOV9wcm9tb3Rpb25fZTc4ZDI5ZDMtMWJhNC00MWRhLWE5NmQtOTA1MzM4ZTQyZTgz",
    "adbiz-page-enter-time": "1768961755024",
    "adbiz-page-version": "v20260119.17.16.44-1113",

    # 🍪 Cookie 原样
    "cookie": "_a42=386ba908-471c-4b9d-af6d-4a6bdb864a66; _bee=hLBIWqdPbG9KmuR61y1cMuEu1YCxYQ7b; _f77=6e928cbe-c1ca-443d-b1f0-b17187327621; _nano_fp=Xpmjl0CJlpXJlpTbXo_FIMEr7tOdempOVQeEZl1q; api_uid=Ck9MdGlvHC1LLQBZQjvSAg==; rckk=hLBIWqdPbG9KmuR61y1cMuEu1YCxYQ7b; ru1k=6e928cbe-c1ca-443d-b1f0-b17187327621; ru2k=386ba908-471c-4b9d-af6d-4a6bdb864a66; SUB_PASS_ID=eyJ0IjoiRmp6SjJQbEg0YWgzQWZYNG9Dbkd6c3MxaERWUkl6N1NSU21kYUNLc29xcUJTV0NnWVRrT0xLbHpZU1YvWTh0VyIsInYiOjEsInMiOjcsIm0iOjI2MzU2NDc4OSwidSI6MTczNzA1NTIyfQ; SUB_SYSTEM_ID=7; windows_app_shop_token_23=eyJ0IjoiSFhuNXNjQjhrNDlqNXVKajY3QVJEaVNDU1UySS94czk1NER6cUZRUmFVODEzUS9CMzFkS3c3TG5RdGhuV0p5ZSIsInYiOjEsInMiOjIzLCJtIjoyNjM1NjQ3ODksInUiOjE3MzcwNTUyMn0"
}

payload = {
    "crawlerInfo": "0asAfa5E-wCE4xymXHSt_USOOG7INqX_L3PpXq7tN5X_xMn2xtibQam3WpN3fwZ3EtZ3nqNUHqNQQjmqlP_RiqZnt49Dzbcm7aaeUK17-PeCik7RmUlGrVAH8MPBeKeBfUe-a-EBbZD-C4ecSD-eVkzeUkzwKe9SE9BVoCrZAL5ZezeFEzXskzRRvzelp-fR1eL2CSkhSMf-7UFRmdeyC1AA_zKlTK99T73EPdP2dl0AgQpA6nn2mA4CKqdNnTUrNo_Wvn5mqy5XodnDJNT7aNuVeqXrsTsiipUr6an2AmXS9OpiTyn0QdXTs9Vl0gOH_Cp11v2PLPCnxh6onUIKx94Zgl_PhG58pai7EhX_3apdMXG3XX4dyj5mCoGlJVzcd04luh_nNdiKNq0ju06fi9Kt54IGnCa8uejKuCjaOM8XCxZG50mE6q9a9T9x9aNvTBOORX3",
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
print(resp.json())

