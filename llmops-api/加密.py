#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/2/20 15:12
@Author         : jiayinkong@163.com
@File           : 加密.py
@Description    : 
"""


def main(params):
    import json
    import urllib.parse

    # 1. 将requestData和apiKey拼接
    request_data = {"logisticCode": f"{params.get('logistic_code')}"}
    api_key = "b5d333d9-22b5-4014-9ad7-17d1b97873a5"

    combine_data = json.dumps(request_data) + api_key

    # 2. MD5加密并转成小写
    import hashlib
    md5_hash = hashlib.md5(combine_data.encode("utf-8")).hexdigest()

    # 3. base64编码
    import base64
    base64_encoded = base64.b64encode(md5_hash.encode("utf-8")).decode("utf-8")

    # 4. URL 编码
    url_encoded = urllib.parse.quote(base64_encoded)

    return {
        "RequestType": 8002,
        "EBusinessID": 1912757,
        "DataSign": url_encoded,
        "RequestData": urllib.parse.quote(json.dumps(request_data)),
    }
