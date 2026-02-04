#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/2/1 13:27
@Author         : jiayinkong@163.com
@File           : chat.py
@Description    : 
"""
import json
import time
from typing import List, Optional, Any

import requests
import tiktoken
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_openai import ChatOpenAI

from internal.core.language_model.entities.model_entity import BaseLanguageModel


class Chat(ChatOpenAI, BaseLanguageModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _generate(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> ChatResult:
        # 1. 判断是否为那个特殊的生图模型
        if self.model_name == "gemini-2.5-flash-image-hd":
            return self._generate_image(messages)

        # 2. 如果是普通模型，调用父类原本的 OpenAI 逻辑
        return super()._generate(messages, stop, run_manager, **kwargs)

    def _generate_image(self, messages: List[BaseMessage]) -> ChatResult:
        """适配 v3 异步生图接口"""
        # 1. 安全地获取 API Key 的明文内容
        if hasattr(self.openai_api_key, "get_secret_value"):
            actual_key = self.openai_api_key.get_secret_value()
        else:
            actual_key = str(self.openai_api_key)

        headers = {
            "Authorization": f"Bearer {actual_key}",  # 确保传入的是明文字符串
            "Content-Type": "application/json"
        }

        prompt = messages[-1].content

        # 1. 提交任务
        submit_url = f"{self.openai_api_base}/google/{self.model_name}/text-to-image"
        payload = {"prompt": prompt, "aspect_ratio": "1:1", "output_format": "png"}

        try:
            submit_resp = requests.post(submit_url, json=payload, headers=headers)
            submit_resp.raise_for_status()
            submit_data = submit_resp.json()

            # 获取查询结果的 URL
            # 对应你提供的 JSON 结构: data -> urls -> get
            poll_url = submit_data.get("data", {}).get("urls", {}).get("get")

            if not poll_url:
                raise Exception("未获取到任务查询链接")

            # 2. 轮询结果 (简易逻辑：最多等 30 秒)
            final_image_url = None
            for _ in range(15):  # 每 2 秒查一次，查 15 次
                time.sleep(2)
                status_resp = requests.get(poll_url, headers=headers)
                status_data = status_resp.json()

                # 注意：这里需要根据你查询接口返回的真实结构微调
                # 通常查询接口返回的 data 里会包含 status 和最终的图片 url
                res_data = status_data.get("data", {})

                if res_data.get("status") == "completed":
                    # 假设最终图片在 res_data["outputs"][0] 或类似位置
                    # 建议先打印 status_data 确认最终图片路径
                    outputs = res_data.get("outputs", [])
                    if outputs:
                        final_image_url = outputs[0]
                    break
                elif res_data.get("status") == "failed":
                    raise Exception("图片生成失败")

            if final_image_url:
                # 包装成 Markdown 格式，前端如果是渲染器可以直接显示图片
                content = f"![generated_image]({final_image_url})"
            else:
                content = f"任务已提交，但生成超时。你可以稍后访问此链接查看：{poll_url}"

        except Exception as e:
            content = f"生图模型调用出错: {str(e)}"

        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=content))])

    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        """手动计算 Token 数量，支持 cl100k_base 编码"""
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
        except Exception:
            # 兜底逻辑：如果无法获取编码器，按字符长度估算
            return sum(len(str(m.content)) // 2 + 3 for m in messages) + 3

        num_tokens = 0
        for message in messages:
            num_tokens += 3  # 每条消息的角色前缀等消耗
            content = message.content or ""
            if isinstance(content, list):
                content = json.dumps(content)
            num_tokens += len(encoding.encode(content))

        num_tokens += 3  # 结束 bonus
        return num_tokens
