#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/8 16:21
@Author         : jiayinkong@163.com
@File           : 1-configurable_filed使用技巧.py
@Description    : 
"""
import os

import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import ConfigurableField
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

# 1. 创建提示模板
prompt = ChatPromptTemplate.from_template("请生成一个小于{x}的随机整数")

# 2. 创建LLM大语言模型，并配置temperature参数为可在运行时配置，配置键位llm_temperature
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
).configurable_fields(
    temperature=ConfigurableField(
        id="llm_temperature",
        name="大语言模型温度",
        description="温度越低，生成的内容越稳定，温度越高生成的内容越随机"
    )
)

# 3. 构建链应用
chain = prompt | llm | StrOutputParser()

# 4. 正常调用
content = chain.invoke({"x": 1000})
print(content)

print("=" * 20)

# 5. 将 temperature修改为0调用内容
content = chain.invoke(
    {"x": 1000},
    config={"configurable": {"llm_temperature": 0}}
)
print(content)
