#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/14 21:59
@Author         : jiayinkong@163.com
@File           : 1-回答回退策略检索器.py
@Description    : 
"""
import os
from typing import List

import dotenv
import weaviate
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.language_models import BaseLanguageModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import FewShotChatMessagePromptTemplate, ChatPromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import AuthApiKey

dotenv.load_dotenv()

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


class StepBackRetriever(BaseRetriever):
    """回答回退检索器"""
    retriever: BaseRetriever
    llm: BaseLanguageModel

    def _get_relevant_documents(
            self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """根据传入的query执行问题回退并检索"""
        # 1. 构建少量示例提示模板
        examples = [
            {"input": "慕课网上有关于AI应用开发的课程吗？", "output": "慕课网上有哪些课程？"},
            {"input": "慕小课出生在哪个国家？", "output": "慕小课的人生经历是什么样的？"},
            {"input": "司机可以开快车吗？", "output": "司机可以做什么？"},
        ]
        example_prompt = ChatPromptTemplate.from_messages([
            ("human", "{input}"),
            ("ai", "{output}"),
        ])
        few_shot_prompt = FewShotChatMessagePromptTemplate(
            examples=examples,
            example_prompt=example_prompt,
        )

        # 构建生成回退问题的模板
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "你是一个世界知识的专家。你的任务是回退问题，将问题改述为更一般或者前置问题，这样更容易回答，请参考示例来实现。"),
            few_shot_prompt,
            ("human", "{question}"),
        ])

        # 3.构建链应用，生成回退问题，并执行相应的检索
        chain = (
                {"question": RunnablePassthrough()}
                | prompt
                | self.llm
                | StrOutputParser()
                | self.retriever
        )

        return chain.invoke(query)


# 创建回答回退检索器
step_back_retriever = StepBackRetriever(
    retriever=retriever,
    llm=ChatOpenAI(
        model="gpt-4o",
        api_key=os.getenv("GPTSAPI_API_KEY"),
        base_url=os.getenv("OPENAI_API_BASE"),
        temperature=0
    )
)

# 检索文档
documents = step_back_retriever.invoke("人工智能会让世界发生翻天覆地的变化吗")
print(documents)
print(len(documents))
