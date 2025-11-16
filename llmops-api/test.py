#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/11/16 08:27
@Author         : jiayinkong@163.com
@File           : test.py
@Description    : 设计模式-依赖注入
"""
from injector import Injector, inject


class A:
    name = "llmops"


@inject
class B:
    def __init__(self, a: A):
        self.a = a

    def print(self):
        print(f"class A 的 name 是 {self.a.name}")


injector = Injector()

b = injector.get(B)
b.print()
