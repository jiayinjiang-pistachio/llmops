#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/26 19:53
@Author         : jiayinkong@163.com
@File           : api_provider_manager.py
@Description    : 
"""
from dataclasses import dataclass
from typing import Callable, Type, Optional

import requests
from injector import inject
from langchain_core.tools import BaseTool, StructuredTool
from pydantic.v1 import BaseModel, Field, create_model

from internal.core.tools.api_tools.entities import ToolEntity
from internal.core.tools.api_tools.entities.openapi_schema import ParameterIn, ParameterTypeMap


# from pydantic import BaseModel, Field, create_model

# {"description":"这是一个查询对应英文单词字典的工具","server":"https://dict.youdao.com","paths":{"/suggest":{"get":{"description":"根据传递的单词查询其字典信息","operationId":"YoudaoSuggest","parameters":[{"name":"q","in":"query","description":"要检索查询的单词，例如love/computer","required":true,"type":"str"},{"name":"doctype","in":"query","description":"返回的数据类型，支持json和xml两种格式，默认情况下json数据","required":false,"type":"str"}]}}}}


@inject
@dataclass
class ApiProviderManager(BaseModel):
    """API工具提供者管理器，能根据传递的工具配置信息生成自定义LangChain工具"""

    @classmethod
    def _create_tool_func_from_tool_entity(cls, tool_entity: ToolEntity) -> Callable:
        """根据传递的信息创建发起API请求的函数"""

        def tool_func(**kwargs) -> str:
            """API工具请求函数"""
            # 1. 定义变量存储来自path/query/header/cookie/request_body的数据
            parameters = {
                ParameterIn.PATH: {},
                ParameterIn.HEADER: {},
                ParameterIn.QUERY: {},
                ParameterIn.COOKIE: {},
                ParameterIn.REQUEST_BODY: {}
            }

            # 2. 更改参数结构映射
            parameter_map = {parameter.get("name"): parameter for parameter in tool_entity.parameters}
            header_map = {header.get("key"): header.get("value") for header in tool_entity.headers}

            # 3. 循环遍历传递的所有字段并校验
            for key, value in kwargs.items():
                # 4. 提取键值对关联的字段并校验
                parameter = parameter_map.get(key)
                if parameter is None:
                    continue

                # 5. 将参数存储到合适的位置上，默认在query上
                parameters[parameter.get("in", ParameterIn.QUERY)][key] = value

            # 6. 构建request请求并返回采集的内容
            return requests.request(
                method=tool_entity.method,
                url=tool_entity.url.format(**parameters[ParameterIn.PATH]),
                params=parameters[ParameterIn.QUERY],
                json=parameters[ParameterIn.REQUEST_BODY],
                headers={**header_map, **parameters[ParameterIn.HEADER]},
                cookies=parameters[ParameterIn.COOKIE],
            ).text

        return tool_func

    @classmethod
    def _create_model_from_parameters(cls, parameters: list[dict]) -> Type[BaseModel]:
        """根据传递的parameters参数创建BaseModel子类"""
        fields = {}
        for parameter in parameters:
            field_name = parameter.get("name")
            field_type = ParameterTypeMap.get(parameter.get("type"), str)
            field_required = parameter.get("required", True)
            field_description = parameter.get("description", "")

            fields[field_name] = (
                field_type if field_required else Optional[field_type],
                Field(description=field_description)
            )
        return create_model("dynamicModel", **fields)

    def get_tool(self, tool_entity: ToolEntity) -> BaseTool:
        """根据传递的配置获取自定义API工具"""
        return StructuredTool.from_function(
            func=self._create_tool_func_from_tool_entity(tool_entity),
            name=f"{tool_entity.id}_{tool_entity.name}",
            description=tool_entity.description,
            args_schema=self._create_model_from_parameters(tool_entity.parameters),
        )
