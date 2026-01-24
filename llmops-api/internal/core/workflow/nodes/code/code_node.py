#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/23 16:51
@Author         : jiayinkong@163.com
@File           : code_node.py
@Description    : 
"""
import ast
from typing import Optional

from langchain_core.runnables import RunnableConfig

from internal.core.workflow.entities.node_entity import NodeResult, NodeStatus
from internal.core.workflow.entities.variable_entity import VariableEntity, VariableValueType, \
    VariableTypeDefaultValueMap
from internal.core.workflow.entities.workflow_entity import WorkflowState
from internal.core.workflow.nodes import BaseNode
from internal.core.workflow.nodes.code.code_entity import CodeNodeData
from internal.exception import FailException


class CodeNode(BaseNode):
    node_data_cls = CodeNodeData

    def invoke(self, state: WorkflowState, config: Optional[RunnableConfig] = None) -> WorkflowState:
        """python code 节点执行函数"""
        inputs: list[VariableEntity] = self.node_data.inputs

        inputs_dict = {}
        for input in inputs:
            # 判断input的值类型
            if input.value.type == VariableValueType.LITERAL:
                inputs_dict[input.name] = input.value.content
            else:
                # input 的值是引用类型
                # 循环上一个节点的node_results
                for node_result in state["node_results"]:
                    # 寻找当前input所对应的引用节点
                    if input.value.content.ref_node_id == node_result.node_data.id:
                        inputs_dict[input.name] = node_result.outputs.get(
                            input.value.content.ref_var_name,
                            VariableTypeDefaultValueMap.get(input.type)
                        )

        # todo: 执行python代码，该方法目前可以执行任意代码。所以非常危险，后续考虑迁移到沙箱
        result = self._execute_function(self.node_data.code, params=inputs_dict)

        if not isinstance(result, dict):
            raise FailException("main函数的返回值必须是一个字典")

        outputs_dict = {}
        for output in self.node_data.outputs:  # 这个outputs是由外部传进来的，里面写好了需要输出的字段和定义了值类型
            # 提取输出数据，非严格校验
            outputs_dict[output.name] = result.get(
                output.name,
                VariableTypeDefaultValueMap.get(output.type)
            )

        # 构建状态数据并返回
        return {
            "node_results": [
                NodeResult(
                    node_data=self.node_data,
                    inputs=inputs_dict,
                    outputs=outputs_dict,
                    status=NodeStatus.SUCCEEDED,
                )
            ]
        }

    @classmethod
    def _execute_function(cls, code: str, *args, **kwargs):
        """执行python函数代码"""
        try:
            tree = ast.parse(code)
            main_func = None

            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    # 如果是函数节点
                    if node.name == "main":
                        # 如果已经赋值给main_func
                        if main_func:
                            raise FailException("代码中只能有一个函数")

                        if len(node.args.args) != 1 or node.args.args[0].arg != "params":
                            raise FailException("main函数必须只有一个参数且参数名为params")

                        main_func = node

                    else:
                        raise FailException("代码中不能有其他函数，只能有main函数")
                else:
                    # 非函数节点
                    raise FailException("代码中只能包含函数定义，不允许其他语句存在")

            # 判断是否找到main函数
            if not main_func:
                raise FailException("代码中必须包含名为main的函数")

            # 2. 【关键修复】将整个 AST 树编译成可执行的代码对象
            # compile 接受 AST 树，并将其转换为 exec 能识别的 code object
            byte_code = compile(tree, filename="<user_code>", mode="exec")

            # 3. 创建一个空的命名空间来存放执行结果
            local_vars = {}

            # 4. 执行编译后的代码
            # 这步操作会在 local_vars 字典里创建出一个名为 'main' 的函数对象
            exec(byte_code, {}, local_vars)

            # 5. 从命名空间中提取并调用 main 函数
            if "main" in local_vars and callable(local_vars["main"]):
                return local_vars["main"](*args, **kwargs)
            else:
                raise Exception("未找到可调用的 main 函数")

        except Exception as e:
            raise Exception(f"Python执行出错: {str(e)}")
