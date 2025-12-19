#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/18 16:19
@Author         : jiayinkong@163.com
@File           : 2-LLM文生图应用.py
@Description    :
"""
import os

import dotenv
from langchain_community.tools.openai_dalle_image_generation import OpenAIDALLEImageGenerationTool
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

dalle = OpenAIDALLEImageGenerationTool(
    api_wrapper=DallEAPIWrapper(
        model="dall-e-3",
        api_key=os.getenv("GPTSAPI_API_KEY"),  # 确保这里使用你可用的 Key
        base_url=os.getenv("OPENAI_API_BASE")  # 确保这里传入中转或自定义地址
    )
)

llm = ChatOpenAI(
    model="gpt-4o",
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE"),
)
llm_with_tools = llm.bind_tools([dalle], tool_choice="openai_dalle")

chain = llm_with_tools | (lambda msg: list(msg.tool_calls[0]["args"].values())[0]) | dalle

print(chain.invoke("帮我绘制一张老爷爷爬山的图片"))
