#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/14 20:46
@Author         : jiayinkong@163.com
@File           : 1-问题分解策略.py
@Description    : 
"""
import os
from operator import itemgetter

import dotenv
import weaviate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import AuthApiKey

dotenv.load_dotenv()


def format_qa_pair(question: str, answer: str) -> str:
    """格式化问题和答案为一个字符串"""
    return f"Question: {question}\nAnswer: {answer}\n\n".strip()


# 1.定义分解子问题的prompt
decomposition_prompt = ChatPromptTemplate.from_template(
    "你是一个乐于助人的AI助理，可以针对一个输入问题生成多个相关的子问题。\n"
    "目标是将输入问题分解成一组可以独立回答的子问题或者子任务。\n"
    "生成与一下问题相关的多个搜索查询：{question}\n"
    "并使用换行符进行分割，输出（3个子问题/子查询）："
)

# 2.构建分解问题链
decomposition_chain = (
        {"question": RunnablePassthrough()}
        | decomposition_prompt
        | ChatOpenAI(
    temperature=0,
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE"),
)
        | StrOutputParser()
        | (lambda x: x.strip().split("\n"))
)

embedding = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=os.getenv("GPTSAPI_API_KEY"),
    openai_api_base=os.getenv("OPENAI_API_BASE")
)

# 创建连接客户端
client = weaviate.connect_to_weaviate_cloud(
    cluster_url="leskh5srpsgusmg0hyiyg.c0.asia-southeast1.gcp.weaviate.cloud",
    auth_credentials=AuthApiKey(
        "TUcxREMvQ2VENG1TSEtUL19JaDh6OXVyVG9uZVRoTzJXUnUwc2l2b0w5bVpzcnRRREF3blZXWEJCRHR3PV92MjAw"),
    skip_init_checks=True,  # 添加这个，跳过初始化检查
    additional_config=weaviate.classes.init.AdditionalConfig(
        timeout=weaviate.classes.init.Timeout(init=30, query=60, insert=120)  # 设置超时
    )
)

# 创建Langchain向量数据库实例
db = WeaviateVectorStore(
    client=client,
    index_name="DatasetDemo",
    text_key="text",
    embedding=embedding,
)
retriever = db.as_retriever(search_type="mmr")

# 4.执行提问获取子问题
question = "关于LLMOps应用配置的文档有哪些"
sub_questions = decomposition_chain.invoke(question)

# 5. 构建迭代问题链：提示模板+链
prompt = ChatPromptTemplate.from_template("""这是你需要回答的问题：
---
{question}
---

这是所有可用的背景问题和答案对：
---
{qa_pairs}
---

这是与问题相关的额外背景信息：
---
{context}
---""")

chain = (
        {
            "question": itemgetter("question"),
            "qa_pairs": itemgetter("qa_pairs"),
            "context": itemgetter("question") | retriever,
        }
        | prompt
        | ChatOpenAI(
    model="gpt-4o",
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE"),
    temperature=0
)
        | StrOutputParser()
)

# 循环遍历所有子问题，进行检索并获取答案
qa_pairs = ""
for sub_question in sub_questions:
    answer = chain.invoke({"question": sub_question, "qa_pairs": qa_pairs})
    qa_pair = format_qa_pair(sub_question, answer)
    qa_pairs += "\n---\n" + qa_pair
    print(f"问题: {sub_question}")
    print(f"答案: {answer}")
