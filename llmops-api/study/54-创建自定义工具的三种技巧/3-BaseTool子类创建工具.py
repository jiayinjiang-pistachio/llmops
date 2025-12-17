#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/17 12:24
@Author         : jiayinkong@163.com
@File           : 3-BaseTool子类创建工具.py
@Description    : 
"""
from typing import Type

from langchain_core.pydantic_v1 import Field, BaseModel
from langchain_core.tools import BaseTool


class CalculatorInput(BaseModel):
    a: int = Field("第一个参数")
    b: int = Field("第二个参数")


class MultiplyTool(BaseTool):
    """乘法计算工具"""
    name = "multiply_tool"
    description = "将传递的两个数相乘"
    args_schema: Type[BaseModel] = CalculatorInput

    def _run(self, a: int, b: int) -> int:
        """将两数相乘"""
        return a * b


calculator = MultiplyTool()

print(f"name: {calculator.name}")
print(f"description: {calculator.description}")
print(f"args: {calculator.args}")
print(f"return_direct: {calculator.return_direct}")
print(calculator.invoke({"a": 4, "b": 5}))
