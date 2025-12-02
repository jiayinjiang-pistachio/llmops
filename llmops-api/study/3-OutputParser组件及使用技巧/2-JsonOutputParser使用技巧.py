#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/11/30 15:30
@Author         : jiayinkong@163.com
@File           : 2-JsonOutputParser使用技巧.py
@Description    : 
"""
import os

import dotenv
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()


# 1. 创建一个json数据结构，用于告诉大语言模型这个json长什么样
class Joke(BaseModel):
    joke: str = Field(description="回答用户的冷笑话")
    # 冷笑话的笑点
    punchline: str = Field(description="这个冷笑话的笑点")


parser = JsonOutputParser(pydantic_object=Joke)

# 2. 构建一个提示模板
prompt = ChatPromptTemplate.from_template("请根据用户的提问进行回答。\n{format_instructions}\n{query}").partial(
    format_instructions=parser.get_format_instructions())

# 3. 构建一个大语言模型
llm = ChatOpenAI(
    model="gpt-4",
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE"),
)

# 4. 传递提示并进行解析
joke = parser.invoke(llm.invoke(prompt.invoke({"query": "请讲一个程序员的冷笑话"})))
print(joke)
