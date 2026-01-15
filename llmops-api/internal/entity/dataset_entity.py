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


DEFAULT_PROCESS_RULE = {
    "mode": "custom",
    "rule": {
        "pre_process_rules": [
            {"id": "remove_extra_space", "enabled": True},
            {"id": "remove_url_and_email", "enabled": True},
        ],
        "segment": {
            "separators": [
                "\n\n",
                "\n",
                "。|！|？",
                "\.\s|\!\s|\?\s",  # 英文标点符号后面通常需要加空格
                "；|;\s",
                "，|,\s",
                " ",
                ""
            ],
            "chunk_size": 500,
            "chunk_overlap": 50,
        }
    }
}


class DocumentStatus(str, Enum):
    """文档状态类型枚举"""
    WAITING = "waiting"
    PARSING = "parsing"
    SPLITTING = "splitting"
    INDEXING = "indexing"
    COMPLETED = "completed"
    ERROR = "error"


class SegmentStatus(str, Enum):
    """片段状态类型枚举"""
    WAITING = "waiting"
    INDEXING = "indexing"
    COMPLETED = "completed"
    ERROR = "error"


class RetrievalStrategy(str, Enum):
    """检索策略类型枚举"""
    FULL_TEXT = "full_text"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"


class RetrievalSource(str, Enum):
    HIT_TESTING = "hit_testing"
    APP = "app"
    DEBUGGER = "debugger"
