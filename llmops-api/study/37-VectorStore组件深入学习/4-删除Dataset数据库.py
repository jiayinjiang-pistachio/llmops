#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/2 10:21
@Author         : jiayinkong@163.com
@File           : 4-删除Dataset数据库.py
@Description    : 
"""
import os

import weaviate
from dotenv import load_dotenv

# 重点：加载 .env 文件
load_dotenv()

# 连接远程服务器
client = weaviate.connect_to_local(
    host=os.getenv("WEAVIATE_HOST"),
    port=int(os.getenv("WEAVIATE_PORT")),
)

# 删除错误的类（这会清空该类下的数据）
if client.collections.exists("Dataset"):
    client.collections.delete("Dataset")
    print("成功删除旧的 Dataset 类")
else:
    print("Dataset数据库不存在")
