#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/17 12:09
@Author         : jiayinkong@163.com
@File           : 2-StructuredTool类方法创建工具.py
@Description    : 
"""
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import StructuredTool


def multiply(a: int, b: int) -> int:
    """将两数相乘"""
    return a * b


async def amultiply(a: int, b: int) -> int:
    """将两数相乘"""
    return a * b


class CalculatorInput(BaseModel):
    a: int = Field(description="第一个参数")
    b: int = Field(description="第二个参数")


calculator = StructuredTool.from_function(
    func=multiply,
    coroutine=amultiply,
    name="multiply_tool",
    description="用于传递的两个参数相乘",
    return_direct=True,
    args_schema=CalculatorInput
)

print(f"name: {calculator.name}")
print(f"description: {calculator.description}")
print(f"args: {calculator.args}")
print(f"result: {calculator.return_direct}")
print(calculator.invoke({"a": 2, "b": 3}))
