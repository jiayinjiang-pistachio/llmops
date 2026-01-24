#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/22 15:10
@Author         : jiayinkong@163.com
@File           : workflow.py
@Description    : 
"""
from typing import Any, Optional, Iterator

from flask import current_app
from langchain_core.pydantic_v1 import PrivateAttr, BaseModel, Field, create_model
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.utils import Input, Output
from langchain_core.tools import BaseTool
from langgraph.graph.state import CompiledStateGraph, StateGraph

from internal.core.workflow.entities.node_entity import NodeType
from internal.core.workflow.entities.variable_entity import VariableTypeMap
from internal.core.workflow.entities.workflow_entity import WorkflowConfig, WorkflowState
from internal.core.workflow.nodes import (
    StartNode, EndNode, LLMNode, TemplateTransformNode, DatasetRetrievalNode, CodeNode, ToolNode, HttpRequestNode
)

NodeClasses = {
    NodeType.START: StartNode,
    NodeType.DATASET_RETRIEVAL: DatasetRetrievalNode,
    NodeType.LLM: LLMNode,
    NodeType.CODE: CodeNode,
    NodeType.TEMPLATTE_TRANSFORM: TemplateTransformNode,
    NodeType.TOOL: ToolNode,
    NodeType.HTTP_REQUEST: HttpRequestNode,
    NodeType.END: EndNode,
}


class Workflow(BaseTool):
    """工作流Langchain工具类"""
    _workflow_config: WorkflowConfig = PrivateAttr(None)
    _workflow: CompiledStateGraph = PrivateAttr(None)

    def __init__(self, workflow_config: WorkflowConfig, **kwargs):
        super().__init__(
            name=workflow_config.name,
            description=workflow_config.description,
            args_schema=self._build_args_schema(workflow_config),
            **kwargs
        )

        # 完善工作流配置与工作流图结构程序的初始化
        self._workflow_config = workflow_config
        self._workflow = self._build_workflow()

    @classmethod
    def _build_args_schema(cls, workflow_config: WorkflowConfig) -> type[BaseModel]:
        """构建输入参数结构体"""
        # 提取开始节点的输入参数信息
        fields = {}

        # 从开始节点中找出原始的输入inputs
        inputs = next(
            (node.get("inputs", []) for node in workflow_config.nodes if node.get("node_type") == NodeType.START),
            []
        )

        # 循环遍历所有输入信息，并创建字段映射
        for input in inputs:
            filed_name = input.get("name")
            field_type = VariableTypeMap.get(input.get("type"), str)
            field_description = input.get("description", "")
            field_required = input.get("required", True)

            fields[filed_name] = (
                field_type if field_required else Optional[field_type],
                Field(description=field_description)
            )

        # 调用create_model创建一个BaseModel类，并使用以上分析好了的字段
        return create_model("DynamicModel", **fields)

    def _build_workflow(self) -> CompiledStateGraph:
        """构建编译后的工作流图程序"""
        graph = StateGraph(WorkflowState)

        # 提取 nodes、edges 信息
        nodes = self._workflow_config.nodes
        edges = self._workflow_config.edges

        # 循环遍历所有节点，添加节点
        for node in nodes:
            node_flag = f"{node.get('node_type')}_{node.get('id')}"

            if node.get("node_type") == NodeType.START:
                graph.add_node(
                    node_flag,
                    NodeClasses[NodeType.START](node_data=node),
                )
            elif node.get("node_type") == NodeType.DATASET_RETRIEVAL:
                graph.add_node(
                    node_flag,
                    NodeClasses[NodeType.DATASET_RETRIEVAL](
                        flask_app=current_app._get_current_object(),
                        account_id=self._workflow_config.account_id,
                        node_data=node,
                    ),
                )
            elif node.get("node_type") == NodeType.LLM:
                graph.add_node(
                    node_flag,
                    NodeClasses[NodeType.LLM](node_data=node),
                )
            elif node.get("node_type") == NodeType.CODE:
                graph.add_node(
                    node_flag,
                    NodeClasses[NodeType.CODE](node_data=node),
                )
            elif node.get("node_type") == NodeType.TEMPLATTE_TRANSFORM:
                graph.add_node(
                    node_flag,
                    NodeClasses[NodeType.TEMPLATTE_TRANSFORM](node_data=node),
                )
            elif node.get("node_type") == NodeType.TOOL:
                graph.add_node(
                    node_flag,
                    NodeClasses[NodeType.TOOL](node_data=node),
                )
            elif node.get("node_type") == NodeType.HTTP_REQUEST:
                graph.add_node(
                    node_flag,
                    NodeClasses[NodeType.HTTP_REQUEST](node_data=node),
                )
            elif node.get("node_type") == NodeType.END:
                graph.add_node(
                    node_flag,
                    NodeClasses[NodeType.END](node_data=node),
                )

        # 循环遍历所有边，添加边
        for edge in edges:
            # 添加边映射关系
            graph.add_edge(
                f"{edge.get('source_type')}_{edge.get('source')}",
                f"{edge.get('target_type')}_{edge.get('target')}",
            )

            # 检测特殊的边（开始节点和结束节点）
            if edge.get("source_type") == NodeType.START:
                graph.set_entry_point(f"{edge.get('source_type')}_{edge.get('source')}")
            elif edge.get("target_type") == NodeType.END:
                graph.set_finish_point(f"{edge.get('target_type')}_{edge.get('target')}")

        return graph.compile()

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        return self._workflow.invoke({"inputs": kwargs})

    def stream(
            self,
            input: Input,
            config: Optional[RunnableConfig] = None,
            **kwargs: Optional[Any],
    ) -> Iterator[Output]:
        """工作流流式输出每个节点的结果"""
        return self._workflow.stream({"inputs": input})
