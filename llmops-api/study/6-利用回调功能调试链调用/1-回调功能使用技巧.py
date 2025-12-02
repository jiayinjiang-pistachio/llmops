#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/2 16:15
@Author         : jiayinkong@163.com
@File           : 1-回调功能使用技巧.py
@Description    : 
"""
import os
import time
from typing import Dict, Any, List, Optional
from uuid import UUID

import dotenv
from langchain_core.callbacks import StdOutCallbackHandler, BaseCallbackHandler
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.outputs import LLMResult
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()


class LLMOpsCallbackHandler(BaseCallbackHandler):
    """自定义回调处理器"""
    start_at: float = 0

    def on_chat_model_start(
            self,
            serialized: Dict[str, Any],
            messages: List[List[BaseMessage]],
            *,
            run_id: UUID,
            parent_run_id: Optional[UUID] = None,
            tags: Optional[List[str]] = None,
            metadata: Optional[Dict[str, Any]] = None,
            **kwargs: Any,
    ) -> Any:
        print("聊天模型开始执行了：")
        print("serialized: ", serialized)
        print("messages: ", messages)
        self.start_at = time.time()

    def on_llm_end(
            self,
            response: LLMResult,
            *,
            run_id: UUID,
            parent_run_id: Optional[UUID] = None,
            **kwargs: Any,
    ) -> Any:
        end_at: float = time.time()
        print("完整输出：", response)
        print("程序运行消耗：", end_at - self.start_at)

    # def on_llm_new_token(
    #         self,
    #         token: str,
    #         *,
    #         chunk: Optional[Union[GenerationChunk, ChatGenerationChunk]] = None,
    #         run_id: UUID,
    #         parent_run_id: Optional[UUID] = None,
    #         **kwargs: Any,
    # ) -> Any:
    #     print("token生成了")
    #     print("token: ", token)


# 1. 编排prompt
prompt = ChatPromptTemplate.from_template("{query}")

# 2. 创建大语言模型
llm = ChatOpenAI(
    model="gpt-4",
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE"),
)

# 3. 构建链
chain = {"query": RunnablePassthrough()} | prompt | llm | StrOutputParser()

# 4. 调用链并执行
# content = chain.invoke(
#     "你好，你是？",
#     config={"callbacks": [StdOutCallbackHandler(), LLMOpsCallbackHandler()]}
# )
#
# print(content)

resp = chain.stream(
    "你好，你是？",
    config={"callbacks": [StdOutCallbackHandler(), LLMOpsCallbackHandler()]}
)

for chunck in resp:
    pass
