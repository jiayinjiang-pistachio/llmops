#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/5 15:57
@Author         : jiayinkong@163.com
@File           : 1-摘要缓冲混合记忆示例.py
@Description    : 
"""
import os

import dotenv
from openai import OpenAI

dotenv.load_dotenv()


class ConversationSummaryBufferMemory:
    """摘要缓冲混合记忆类"""

    def __init__(self, summary: str = '', chat_histories: list = None, max_tokens: int = 300):
        self.summary = summary
        self.chat_histories = chat_histories if chat_histories is not None else []
        self.max_tokens = max_tokens
        self._client = OpenAI(
            base_url=os.getenv("OPENAI_API_BASE"),
            api_key=os.getenv("GPTSAPI_API_KEY")
        )

    @classmethod
    def get_num_tokens(cls, query: str) -> int:
        """计算传入的query的token数"""
        return len(query)

    def save_context(self, human_query: str, ai_content: str) -> None:
        """保存传入的新一次对话"""
        self.chat_histories.append({"human": human_query, "ai": ai_content})
        buffer_string = self.get_buffer_string()
        tokens = self.get_num_tokens(buffer_string)

        if tokens > self.max_tokens:
            first_chat = self.chat_histories[0]
            print("新摘要生成中～")
            self.summary_text(self.summary, f"Human: {first_chat['human']}\nAI: {first_chat['ai']}")
            print(f"新摘要生成成功：{self.summary}")
            del self.chat_histories[0]

    def get_buffer_string(self) -> str:
        """将历史对话转换成字符串"""
        buffer: str = ""
        for chat in self.chat_histories:
            buffer += f"Human: {chat['human']}\nAI: {chat['ai']}\n\n"
        return buffer.strip()

    def load_memory_variables(self) -> dict[str, any]:
        """加载记忆变量为一个字典，便于格式化到prompt中"""
        buffer_string = self.get_buffer_string()
        return {
            "chat_history": f"摘要：{self.summary}\n\n历史信息：{buffer_string}\n",
        }

    def summary_text(self, origin_summary: str, newline: str):
        """用于将旧摘要和传入的新对话生成一个新摘要"""
        prompt = f"""你是一个强大的聊天机器人，请根据用户提供的谈话内容，总结摘要，并将其添加到先前提供的摘要中，返回一个新的摘要，除了新摘要其他任何数据都不要生成，如果用户的对话信息里有一些关键的信息，
比如性别、姓名、爱好、重要事件等，这些全部都要包括在生成的摘要中，摘要尽可能要还原用户的对话记录。

请不要将<example>标签里的数据当成实际的数据，这里的数据只是一个示例数据，告诉你该如何生成新摘要。

<example>
当前摘要：人类会问人工智能对人工智能的看法，人工智能认为人工智能是一股向善的力量。

新的对话：
Human：为什么你认为人工智能是一股向善的力量？
AI：因为人工智能会帮助人类充分发挥能力。

新摘要：人类会问人工智能对人工智能的看法，人工智能认为人工智能是一股向善的力量，因为它将帮助人类充分发挥能力
</example>

==============================以下数据是实际需要处理的数据==============================

当前摘要：{origin_summary}

新的对话：
{newline}

请帮用户将上面的信息生成摘要。
"""

        try:
            completion = self._client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": prompt},
                ],
                # max_retries=2,
                # timeout=30,
            )
            self.summary = completion.choices[0].message.content
        except Exception as e:
            print(f"生成摘要失败: {e}")
            # 简单的回退策略：直接拼接
            self.summary = f"{origin_summary} {newline}"[:500]  # 限制长度


# 创建客户端和记忆
client = OpenAI(
    base_url=os.getenv("OPENAI_API_BASE"),
    api_key=os.getenv("GPTSAPI_API_KEY")
)
memory = ConversationSummaryBufferMemory("", [], 300)

# 主对话循环
while True:
    query = input("Human: ")

    if query == "q":
        break

    memory_variables = memory.load_memory_variables()

    # 修复：正确拼接字符串
    answer_prompt = f"""你是一个强大的聊天机器人，请根据对应的上下文和用户提问解决问题。

{memory_variables.get('chat_history')}

用户的提问是：{query}

"""

    try:
        resp = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": answer_prompt}
            ],
            stream=True,
            # max_retries=3,
            # timeout=60,
        )
    except Exception as e:
        print(f"GPT-4 请求失败: {e}")
        print("尝试使用 GPT-3.5-Turbo...")
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": answer_prompt}
            ],
            stream=True,
        )

    print("AI: ", end="", flush=True)
    ai_content = ""

    for chunk in resp:
        if chunk.choices and len(chunk.choices) > 0:
            content = chunk.choices[0].delta.content
            if content is not None:
                ai_content += content
                print(content, end="", flush=True)

    print()
    memory.save_context(query, ai_content)
