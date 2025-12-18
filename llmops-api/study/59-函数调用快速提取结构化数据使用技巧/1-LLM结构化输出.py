#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/17 18:45
@Author         : jiayinkong@163.com
@File           : 1-LLM结构化输出.py
@Description    : 
"""
import os

import dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()


class QAExtra(BaseModel):
    question: str = Field(description="假设性问题")
    answer: str = Field(description="假设性问题对应的答案")


llm = ChatOpenAI(
    model="gpt-4o",
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE"),
)
structured_llm = llm.with_structured_output(QAExtra, method="json_mode")

prompt = ChatPromptTemplate.from_messages([
    # ("system", "从用户传递的query中提取出假设性的问题+答案"),
    ("system", "请从用户传递的query中提取出假设性的问题+答案。响应格式为JSON，并携带`question`和`answer`两个字段。"),
    ("human", "{query}")
])
chain = {"query": RunnablePassthrough()} | prompt | structured_llm
print(chain.invoke("我叫慕小课，我喜欢打篮球，游泳"))
