#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/23 14:23
@Author         : jiayinkong@163.com
@File           : dataset_retrieval_entity.py
@Description    : 
"""
from uuid import UUID

from langchain_core.pydantic_v1 import BaseModel, Field
from pydantic import model_validator

from internal.core.workflow.entities.node_entity import BaseNodeData
from internal.core.workflow.entities.variable_entity import VariableEntity, VariableValueType, VariableType
from internal.entity.dataset_entity import RetrievalStrategy
from internal.exception import FailException


class RetrievalConfig(BaseModel):
    """检索配置信息"""
    retrieval_strategy: RetrievalStrategy = RetrievalStrategy.SEMANTIC  # 检索策略
    k: int = 4  # 最大召回数
    score: float = 0  # 得分阈值


class DatasetRetrievalNodeData(BaseNodeData):
    """知识库检索节点信息"""
    dataset_ids: list[UUID]
    retrieval_config: RetrievalConfig = RetrievalConfig()
    inputs: list[VariableEntity] = Field(default_factory=list)
    outputs: list[VariableEntity] = Field(
        exclude=True,
        default_factory=lambda: [
            VariableEntity(name="combine_documents", value={"type": VariableValueType.GENERATED})
        ]
    )

    @classmethod
    @model_validator(mode="before")
    def validate_inputs(cls, values):
        inputs = values.get("inputs", [])

        if len(inputs) != 1:
            raise FailException("知识库节点输入变量信息出错")

        input_query: VariableEntity = inputs[0]

        if input_query.name != "query" or input_query.type != VariableType.STRING or input_query.required is False:
            raise FailException("知识库节点输入变量名/变量类型/必填属性出错")

        return values
