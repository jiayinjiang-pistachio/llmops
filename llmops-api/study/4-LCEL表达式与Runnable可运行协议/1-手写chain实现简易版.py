#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/2 14:15
@Author         : jiayinkong@163.com
@File           : 1-手写chain实现简易版.py
@Description    : 
"""
import os
from typing import Any

import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

# 1. 构建组件
prompt = ChatPromptTemplate.from_template("{query}")
llm = ChatOpenAI(
    model="gpt-4",
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE"),
)
parser = StrOutputParser()


# 2. 定义一个链
class Chain:
    steps: list = []

    def __init__(self, steps: list):
        self.steps = steps

    def invoke(self, input: Any) -> Any:
        for step in self.steps:
            input = step.invoke(input)
            print("步骤：", step)
            print("输出：", input)
            print("=" * 20)
        return input


# 3. 编排链
chain = Chain([prompt, llm, parser])

# 4. 执行链并获取结果
print(chain.invoke({"query": "你好，你是？"}))
