#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/11/16 09:59
@Author         : jiayinkong@163.com
@File           : app.py
@Description    : 
"""
import dotenv
from injector import Injector

from config import Config
from internal.router import Router
from internal.server.http import Http

# 将 env 加载到环境变量中
dotenv.load_dotenv()

conf = Config()

injector = Injector()

app = Http(__name__, conf=conf, router=injector.get(Router))

# 如果文件被执行
if __name__ == "__main__":
    app.run(debug=True)
