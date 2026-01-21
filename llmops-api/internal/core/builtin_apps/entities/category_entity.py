#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/21 16:24
@Author         : jiayinkong@163.com
@File           : category_entity.py
@Description    : 
"""
from pydantic import BaseModel, Field


class CategoryEntity(BaseModel):
    """内置应用分类实体"""
    name: str = Field(default="")
    category: str = Field(default="")
