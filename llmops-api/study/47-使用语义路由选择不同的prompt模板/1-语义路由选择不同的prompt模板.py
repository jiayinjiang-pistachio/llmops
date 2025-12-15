#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/15 17:40
@Author         : jiayinkong@163.com
@File           : 1-语义路由选择不同的prompt模板.py
@Description    : 
"""
import os

import dotenv
import numpy as np
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

dotenv.load_dotenv()


def cosine_sim(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


# 1.定义两份不同的prompt模板(物理模板、数学模板)
physics_template = """你是一位非常聪明的物理教程。
你擅长以简洁易懂的方式回答物理问题。
当你不知道问题的答案时，你会坦率承认自己不知道。

这是一个问题：
{query}"""
math_template = """你是一位非常优秀的数学家。你擅长回答数学问题。
你之所以如此优秀，是因为你能将复杂的问题分解成多个小步骤。
并且回答这些小步骤，然后将它们整合在一起回来更广泛的问题。

这是一个问题：
{query}"""

# 2. 创建文本嵌入模型，并执行嵌入
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=os.getenv("GPTSAPI_API_KEY"),
    openai_api_base=os.getenv("OPENAI_API_BASE")
)
prompt_templates = [physics_template, math_template]
prompt_embeddings = embeddings.embed_documents(prompt_templates)


def prompt_router(input) -> ChatPromptTemplate:
    """根据传入的query计算返回不同的提示模板"""
    query_embedding = embeddings.embed_query(input["query"])

    # 2. 计算相似性
    # similarity = cosine_similarity([query_embedding], prompt_embeddings)[0]
    # most_similar = prompt_templates[similarity.argmax()]
    # print("使用数学模板" if most_similar == math_template else "使用物理模板")

    similarities = [
        cosine_sim(query_embedding, pe)
        for pe in prompt_embeddings
    ]

    most_similar = prompt_templates[int(np.argmax(similarities))]

    print("使用数学模板" if most_similar == math_template else "使用物理模板")
    
    # 3. 构建提示模板
    return ChatPromptTemplate.from_template(most_similar)


chain = (
        {"query": RunnablePassthrough()}
        | RunnableLambda(prompt_router)
        | ChatOpenAI(
    model="gpt-4o",
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE"),
    temperature=0
)
        | StrOutputParser()
)

print(chain.invoke("黑洞是什么?"))
print("======================")
print(chain.invoke("能介绍下余弦计算公式么？"))
