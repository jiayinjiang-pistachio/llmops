#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/8 18:54
@Author         : jiayinkong@163.com
@File           : 1-Runnable组件生命周期监听器.py
@Description    : 
"""
import time

from langchain_core.runnables import RunnableLambda, RunnableConfig
from langchain_core.tracers import Run


def on_start(run_obj: Run, config: RunnableConfig) -> None:
    print("on_start")
    print("run_obj: ", run_obj)
    print("config: ", config)
    print("=" * 20)


def on_end(run_obj: Run, config: RunnableConfig) -> None:
    print("on_end")
    print("run_obj: ", run_obj)
    print("config: ", config)
    print("=" * 20)


def on_error(run_obj: Run, config: RunnableConfig) -> None:
    print("on_error")
    print("run_obj: ", run_obj)
    print("config: ", config)
    print("=" * 20)


# 1. 创建RunnableLambda与链
runnable = RunnableLambda(lambda x: time.sleep(x)).with_listeners(
    on_start=on_start,
    on_end=on_end,
    on_error=on_error,
)
chain = runnable

# 调用并执行链
chain.invoke(2, config={"configurable": {"name": "慕小课"}})
