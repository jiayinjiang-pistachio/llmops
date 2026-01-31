#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/31 20:54
@Author         : jiayinkong@163.com
@File           : provider_entity.py
@Description    : 
"""
from typing import Union, Type

from langchain_core.pydantic_v1 import BaseModel, Field

from .model_entity import ModelType, ModelEntity, BaseLanguageModel


class ProviderEntity(BaseModel):
    """模型提供商实体信息"""
    name: str = ""  # 提供商名字
    label: str = ""  # 提供商的标签
    description: str = ""  # 提供商的描述信息
    icon: str = ""  # 提供商的图标
    background: str = ""  # 提供商的图标背景
    supported_model_types: list[ModelType] = Field(default_factory=list)  # 支持的模型类型


class Provider(BaseModel):
    """大语言模型服务提供商，在该类下，可以获取到该服务提供商的所有大语言模型、描述、图标、标签等多个信息"""
    name: str  # 提供商名字
    position: int  # 服务提供商的位置信息
    provider_entity: ProviderEntity  # 提供商实体
    model_entity_map: dict[str, ModelEntity] = Field(default_factory=dict)  # 模型实体映射
    model_class_map: dict[str, Union[None, Type[BaseLanguageModel]]] = Field(default_factory=dict)  # 模型类映射
