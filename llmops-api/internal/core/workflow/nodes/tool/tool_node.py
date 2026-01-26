#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/23 18:13
@Author         : jiayinkong@163.com
@File           : tool_node.py
@Description    : 
"""
import json
import time
from typing import Any, Optional

from langchain_core.pydantic_v1 import PrivateAttr
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool

from internal.core.workflow.entities.node_entity import NodeResult, NodeStatus
from internal.core.workflow.entities.workflow_entity import WorkflowState
from internal.core.workflow.nodes import BaseNode
from internal.core.workflow.nodes.tool.tool_entity import ToolNodeData
from internal.core.workflow.utils.helper import extract_variables_from_state
from internal.exception import FailException


class ToolNode(BaseNode):
    """工具调用节点"""
    node_data = ToolNodeData
    _tool: BaseTool = PrivateAttr(None)  # LangChain工具实例

    def __init__(self, *args, **kwargs: Any):
        """构造函数，完成对工具的初始化"""
        super().__init__(*args, **kwargs)

        # 导入依赖注入及工具提供者
        from app.http.app import injector

        if self.node_data.tool_type == "builtin_tool":
            from internal.core.tools.builtin_tools.providers import BuiltinProviderManager

            builtin_provider_manager = injector.get(BuiltinProviderManager)

            _tool_cls = builtin_provider_manager.get_tool(
                self.node_data.provider_id,
                self.node_data.tool_id
            )

            if not _tool_cls:
                raise FailException("该内置插件扩展不存在，请核实后重试")

            self._tool = _tool_cls(**self.node_data.params)
        else:
            from pkg.sqlalchemy import SQLAlchemy
            from internal.model import ApiTool

            db = injector.get(SQLAlchemy)

            # 调用数据库查询记录并创建API自定义插件
            api_tool: ApiTool = db.session.query(ApiTool).filter(
                ApiTool.provider_id == self.node_data.provider_id,
                ApiTool.name == self.node_data.tool_id,
            ).one_or_none()

            if not api_tool:
                raise FailException("该内置插件扩展不存在，请核实后重试")

            # 导入API插件提供者
            from internal.core.tools.api_tools.providers import ApiProviderManager
            api_provider_manager = injector.get(ApiProviderManager)

            # 创建API插件提供者并赋值
            from internal.core.tools.api_tools.entities import ToolEntity
            self._tool = api_provider_manager.get_tool(ToolEntity(
                id=str(api_tool.id),
                name=api_tool.name,
                url=api_tool.url,
                method=api_tool.method,
                description=api_tool.description,
                headers=api_tool.provider.headers,
                parameters=api_tool.parameters
            ))

    def invoke(self, state: WorkflowState, config: Optional[RunnableConfig] = None) -> WorkflowState:
        """工具调用节点执行函数，根据传递的信息调用预设的插件，包括内置插件和API自定义插件"""
        start_at = time.perf_counter()

        # 从状态中提取出输入数据
        inputs_dict = extract_variables_from_state(self.node_data.inputs, state)

        # 调用插件并提取结果
        try:
            result = self._tool.invoke(inputs_dict)
        except Exception as e:
            raise FailException(f"扩展插件执行失败：{str(e)}")

        # 判断result是否是字符串，如果不是，需要转成字符串
        if not isinstance(result, str):
            result = json.dumps(result)

        # 构建输出结构
        outputs = {}
        if self.node_data.outputs:
            outputs[self.node_data.outputs[0].name] = result
        else:
            outputs["text"] = result

        return {
            "node_results": [
                NodeResult(
                    node_data=self.node_data,
                    inputs=inputs_dict,
                    outputs=outputs,
                    status=NodeStatus.SUCCEEDED,
                    latency=(time.perf_counter() - start_at),
                )
            ]
        }
