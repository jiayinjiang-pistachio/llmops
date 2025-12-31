#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/11/16 09:59
@Author         : jiayinkong@163.com
@File           : app.py
@Description    : 
"""
import dotenv
from flask_migrate import Migrate
from injector import Injector

from config import Config
from internal.router import Router
from internal.server.http import Http
from pkg.sqlalchemy import SQLAlchemy
from .module import ExtensionModule

# 将 env 加载到环境变量中
dotenv.load_dotenv()

conf = Config()

# 传入 [ExtensionModule] 表示使用这个模块的配置
injector = Injector([ExtensionModule])

# injector.get(SQLAlchemy)：从注入器获取 SQLAlchemy 实例（实际上是 db）
app = Http(
    __name__,
    conf=conf,
    db=injector.get(SQLAlchemy),
    migrate=injector.get(Migrate),
    router=injector.get(Router)
)

celery = app.extensions["celery"]

# 如果文件被执行
if __name__ == "__main__":
    app.run(debug=True)
