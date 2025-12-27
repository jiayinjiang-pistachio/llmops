#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/24 11:31
@Author         : jiayinkong@163.com
@File           : gaode_weather.py
@Description    : 
"""
import json
import os
from typing import Type, Any

import requests
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool

from internal.lib.helper import add_attributes


class GaodeWeatherArgsSchema(BaseModel):
    city: str = Field(description="需要查询天气预报的目标城市，例如广州")


class GaodeWeatherTool(BaseTool):
    """根据传入的城市名查询天气"""
    name = "gaode_weather"
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


@add_attributes("args_schema", GaodeWeatherArgsSchema)
def gaode_weather(**kwargs) -> BaseModel:
    """获取高德天气预报查询工具"""
    return GaodeWeatherTool()
