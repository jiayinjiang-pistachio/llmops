#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/23 10:37
@Author         : jiayinkong@163.com
@File           : llm_node.py
@Description    : 
"""
import time
from typing import Optional

from jinja2 import Template
from langchain_core.runnables import RunnableConfig

from internal.core.workflow.entities.node_entity import NodeResult, NodeStatus
from internal.core.workflow.entities.workflow_entity import WorkflowState
from internal.core.workflow.nodes import BaseNode
from internal.core.workflow.nodes.llm.llm_entity import LLMNodeData
from internal.core.workflow.utils.helper import extract_variables_from_state


class LLMNode(BaseNode):
    # 这里不需要写类型标注，直接赋值即可，它会覆盖基类的 ClassVar
    node_data = LLMNodeData

    def invoke(self, state: WorkflowState, config: Optional[RunnableConfig] = None) -> WorkflowState:
        """llm节点的执行函数"""
        start_at = time.perf_counter()

        inputs_dict = extract_variables_from_state(self.node_data.inputs, state)

        # 使用jinja2格式模板信息
        template = Template(self.node_data.prompt)
        prompt_value = template.render(**inputs_dict)

        # 根据配置创建LLM实例
        from app.http.module import injector
        from internal.service import LanguageModelService
        language_model_service = injector.get(LanguageModelService)
        llm = language_model_service.load_language_model(self.node_data.language_model_config)

        # llm = ChatOpenAI(
        #     model=self.node_data.language_model_config.get("model", "gpt-4o-mini"),
        #     api_key=os.getenv("GPTSAPI_API_KEY"),
        #     base_url=os.getenv("OPENAI_API_BASE"),
        #     **self.node_data.language_model_config.get("parameters", {}),
        # )

        # 调用LLM并传递prompt后提取数据
        content = llm.invoke(prompt_value).content
        # content = ""
        # for chunk in llm.stream(prompt_value):
        #     content += chunk

        outputs = {}
        if self.node_data.outputs:
            outputs[self.node_data.outputs[0].name] = content
        else:
            outputs["output"] = content

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
