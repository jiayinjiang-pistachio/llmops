#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/17 11:40
@Author         : jiayinkong@163.com
@File           : 1-tool装饰器创建工具.py
@Description    : 
"""
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import tool


@tool
def multipy(a: int, b: int) -> int:
    """将传递的两个数字相乘"""
    return a * b


print(f"名称: {multipy.name}")
print(f"描述：{multipy.description}")
print(f"参数：{multipy.args}")
print(f"是否直接返回：{multipy.return_direct}")

print(multipy.invoke({"a": 1, "b": 2}))


class CalculatorInput(BaseModel):
    a: int = Field(description="第一个参数")
    b: int = Field(description="第二个参数")


# 名称: multipy
# 描述：将传递的两个数字相乘
# 参数：{'a': {'title': 'A', 'type': 'integer'}, 'b': {'title': 'B', 'type': 'integer'}}
# 是否直接返回：False
# 2

print("=" * 20)


@tool("multipy_tool", return_direct=True, args_schema=CalculatorInput)
def multiply(a: int, b: int) -> int:
    """将传递的两个参数相乘"""
    return a * b


print(f"名称：{multiply.name}")
print(f"描述：{multiply.description}")
print(f"参数：{multiply.args}")
print(f"直接返回：{multiply.return_direct}")
print(multiply.invoke({"a": 2, "b": 3}))

# 打印结果：
# 名称：multipy_tool
# 描述：将传递的两个参数相乘
# 参数：{'a': {'title': 'A', 'description': '第一个参数', 'type': 'integer'}, 'b': {'title': 'B', 'description': '第二个参数', 'type': 'integer'}}
# 直接返回：True
# 6


print("=" * 20)


# Google-Style风格，使用parse_docstring=True

@tool(parse_docstring=True)
def foo(bar: str, baz: int) -> str:
    """The foo.

    Args:
        bar: The bar.
        baz: The baz.
    """
    return bar


print(foo.args)
