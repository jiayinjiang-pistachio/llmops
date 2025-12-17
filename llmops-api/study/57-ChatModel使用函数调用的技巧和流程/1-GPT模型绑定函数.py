#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/17 16:28
@Author         : jiayinkong@163.com
@File           : 1-GPT模型绑定函数.py
@Description    : 
"""
import json
import os
from typing import Type, Any

import dotenv
import requests
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.messages import ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnablePassthrough
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()


class GaodeWeatherArgsSchema(BaseModel):
    city: str = Field(description="需要查询天气预报的城市，例如：广州")


class GoogleSerperArgsSchema(BaseModel):
    query: str = Field(description="执行谷歌搜索的查询语句")


class GaodeWeatherTool(BaseTool):
    """根据传入的城市名查询天气"""
    name = "gaode_weather_tool"
    description = "当你想询问天气或与天气相关的问题时的工具。"
    args_schema: Type[BaseModel] = GaodeWeatherArgsSchema

    def _run(self, *args: Any, **kwargs: Any) -> str:
        """运行工具获取对应城市的天气预报"""
        try:
            # 获取高德API密钥，如果没有则抛出错误
            gaode_api_key = os.getenv("GAODE_API_KEY")
            if not gaode_api_key:
                return "高德API_KEY不存在"
            # 提取城市，并查询行政编码
            city = kwargs.get("city")
            session = requests.session()
            api_domain = "https://restapi.amap.com/v3"
            city_response = session.request(
                method="GET",
                url=f"{api_domain}/config/district?keywords={city}&subdistrict=0&extensions=all&key={gaode_api_key}",
                headers={"Content-Type": "application/json; charset=utf-8"},
            )
            city_response.raise_for_status()
            city_data = city_response.json()

            # 提取行政编码调用天气预报查询接口
            if city_data.get("info") == "OK":
                if len(city_data.get("districts")) > 0:
                    ad_code = city_data.get("districts")[0]["adcode"]
                    weather_response = session.request(
                        method="GET",
                        url=f"{api_domain}/weather/weatherInfo?key={gaode_api_key}&city={ad_code}&extensions=all&output=json",
                        headers={"Content-Type": "application/json; charset=utf-8"},
                    )
                    weather_response.raise_for_status()
                    weather_data = weather_response.json()

                    if weather_data.get("info") == "OK":
                        return json.dumps(weather_data)

            session.close()
            return f"获取{kwargs.get('city')}天气预报信息失败"
        except Exception as e:
            return f"Exception：获取{kwargs.get('city')}天气预报信息失败"


# 1. 定义工具列表
gaode_weather = GaodeWeatherTool()
google_serper = GoogleSerperRun(
    name="google_serper_tool",
    description=(
        "一个低成本的谷歌搜索API。"
        "当你需要回答有关时事问题时，可以调用该工具。"
        "该工具的输入是搜索查询语句。"
    ),
    args_schema=GoogleSerperArgsSchema,
    api_wrapper=GoogleSerperAPIWrapper(),
)
tool_dict = {
    gaode_weather.name: gaode_weather,
    google_serper.name: google_serper,
}
tools = [tool for tool in tool_dict.values()]

# 2. 创建prompt
prompt = ChatPromptTemplate.from_messages([
    ("system",
     "你是由OpenAI开发的聊天机器人，可以帮助用户回答问题，必要时刻请调用工具帮助用户解答，如果问题需要多个工具回答，请一次性调用所有工具，不要分步调用"),
    ("human", "{query}")
])

# 3. 创建大语言模型并绑定工具
llm = ChatOpenAI(
    model="gpt-4o",
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE"),
)
llm_with_tool = llm.bind_tools(tools=tools)

# 4. 创建应用链
chain = {"query": RunnablePassthrough()} | prompt | llm_with_tool

# 5. 调用链应用，并获取输出响应
query = "东莞现在天气怎样，这一周内会下雨吗"
resp = chain.invoke(query)
tool_calls = resp.tool_calls

# 6. 判断是工具调用还是正常输出
if len(tool_calls) <= 0:
    print(f"生成内容：{resp.content}")
else:
    # 7. 将历史的系统消息、人类消息、AI消息整合
    # 重建第二次推理所需的完整上下文
    # 这一步的作用只有一个：把最初的 system + human 消息重新构造出来
    messages = prompt.invoke(query).to_messages()
    messages.append(resp)
    print("整合的消息：", messages)

    # 8. 循环遍历所有工具调用工具
    for tool_call in tool_calls:
        tool = tool_dict.get(tool_call.get("name"))  # 获取需要执行的工具
        print("正在执行工具：", tool.name)
        content = tool.invoke(tool_call.get("args"))  # 工具执行结果
        print("执行工具完毕，返回的结果：", content)

        tool_call_id = tool_call.get("id")

        messages.append(ToolMessage(
            content=content,
            tool_call_id=tool_call_id,
        ))
    print("输出内容：", llm.invoke(messages).content)
