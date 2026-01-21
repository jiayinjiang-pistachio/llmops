#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/21 16:19
@Author         : jiayinkong@163.com
@File           : builtin_app_manager.py
@Description    : 
"""
import os
from typing import Dict

import yaml
from pydantic import BaseModel, Field

from internal.core.builtin_apps.entities.builtin_app_entity import BuiltinAppEntity
from internal.core.builtin_apps.entities.category_entity import CategoryEntity


class BuiltinAppManager(BaseModel):
    """内置应用管理器"""
    builtin_app_map: dict[str, BuiltinAppEntity] = Field(default_factory=dict)
    categories: list[CategoryEntity] = Field(default_factory=list)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_categories()
        self._init_builtin_apps()

    def get_builtin_apps(self) -> Dict[str, BuiltinAppEntity]:
        return [builtin_app for builtin_app in self.builtin_app_map.values()]

    def get_builtin_app(self, builtin_app_id: str) -> BuiltinAppEntity:
        return self.builtin_app_map.get(builtin_app_id, None)

    def get_categories(self) -> list[CategoryEntity]:
        return self.categories

    def _init_categories(self):
        """初始化内置应用分类数据"""
        if self.categories:
            return

        current_path = os.path.abspath(__file__)
        parent_path = os.path.dirname(current_path)
        categories_yaml_path = os.path.join(parent_path, "categories", "categories.yaml")

        with open(categories_yaml_path, "r", encoding="utf-8") as f:
            categories = yaml.safe_load(f)

            for category in categories:
                self.categories.append(CategoryEntity(**category))

    def _init_builtin_apps(self):
        """初始化内置应用数据"""
        if self.builtin_app_map:
            return

        current_path = os.path.abspath(__file__)
        parent_path = os.path.dirname(current_path)
        builtin_apps_path = os.path.join(parent_path, "builtin_apps")

        # 遍历 builtin_apps_path 下的所有 yaml | yml 文件
        for filename in os.listdir(builtin_apps_path):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                file_path = os.path.join(builtin_apps_path, filename)

                # 读取yaml｜yml文件的数据
                with open(file_path, "r", encoding="utf-8") as f:
                    builtin_app_dict = yaml.safe_load(f)

                    # 初始化内置应用数据并添加到字典中
                    self.builtin_app_map[builtin_app_dict["id"]] = BuiltinAppEntity(**builtin_app_dict)
