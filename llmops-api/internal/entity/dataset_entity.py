#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/31 20:34
@Author         : jiayinkong@163.com
@File           : dataset_entity.py
@Description    : 
"""
from enum import Enum

# 默认知识库描述格式化文本
DEFAULT_DATASET_DESCRIPTION = "当你需要回答关于《{name}》的时候可以引用该知识库。"


# str, Enum
# 既享受枚举的命名空间和组织性，又保持字符串的直接可用性

class ProcessType(str, Enum):
    AUTOMATIC = "automatic"
    CUSTOM = "custom"
