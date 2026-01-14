#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/11/19 22:00
@Author         : jiayinkong@163.com
@File           : app_service.py
@Description    : 
"""
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from flask import request
from injector import inject

from internal.entity.app_entity import AppStatus, AppConfigType, DEFAULT_APP_CONFIG
from internal.model import App, Account, AppConfigVersion, ApiTool, Dataset
from internal.schema import CreateAppReq
from pkg.sqlalchemy import SQLAlchemy
from .base_service import BaseService
from ..core.tools.builtin_tools.providers import BuiltinProviderManager
from ..exception import NotFoundException, ForbiddenException
from ..lib.helper import datetime_to_timestamp


@inject
@dataclass
class AppService(BaseService):
    """应用服务逻辑"""
    db: SQLAlchemy
    builtin_provider_manager: BuiltinProviderManager

    def create_app(self, req: CreateAppReq, account: Account) -> App:
        """创建Agent应用服务"""
        # 1. 开启数据库自动提交上下文
        with self.db.auto_commit():
            # 2. 创建应用记录，并刷新记录，从而可以拿到应用id
            app = App(
                account_id=account.id,
                name=req.name.data,
                icon=req.icon.data,
                description=req.description.data or "",
                status=AppStatus.DRAFT,
            )
            self.db.session.add(app)
            self.db.session.flush()  # 只有刷新了下方新增草稿记录时才能拿到app_id

            # 3. 添加草稿记录
            app_config_version = AppConfigVersion(
                app_id=app.id,
                version=0,
                config_type=AppConfigType.DRAFT,
                **DEFAULT_APP_CONFIG,
            )
            self.db.session.add(app_config_version)
            self.db.session.flush()

            # 4. 为应用添加草稿配置id
            app.draft_app_config_id = app_config_version.id

        # 5. 返回创建的应用记录
        return app

    def get_app(self, app_id: UUID, account: Account) -> App:
        """根据传递的id获取应用的基础信息"""
        # 1. 查询数据库获取应用基础信息
        app = self.get(App, app_id)

        # 2. 判断应用是否存在
        if not app:
            raise NotFoundException("该应用不存在，请核实后重试")

        # 3. 判断当前账号是否有权限访问该应用
        if app.account_id != account.id:
            raise ForbiddenException("当前账号无权限访问该应用，请核实后重试")

        return app

    def update_app(self, id: UUID) -> App:
        with self.db.auto_commit():
            app = self.get_app(id)
            app.name = "慕课网机器人"
        return app

    def delete_app(self, id: UUID) -> App:
        with self.db.auto_commit():
            app = self.get_app(id)
            self.db.session.delete(app)
        return app

    def get_draft_app_config(self, app_id: UUID, account: Account) -> dict[str, Any]:
        """根据传递的app_id+account账号信息获取应用草稿配置"""
        # 1. 获取应用基础信息
        app = self.get_app(app_id, account)

        draft_app_config = app.draft_app_config

        # 2. todo: 校验model_config

        # 3. 校验工具
        draft_tools = draft_app_config.tools
        validate_tools = []
        tools = []

        for draft_tool in draft_tools:
            # 4. 校验内置工具
            if draft_tool["type"] == "builtin_tool":
                provider = self.builtin_provider_manager.get_provider(draft_tool["provider_id"])
                if not provider:
                    continue

                tool_entity = provider.get_tool_entity(draft_tool["tool_id"])
                if not tool_entity:
                    continue

                # 5. 判断工具的params与草稿配置中的params是否一致，不一致则设置为默认值
                param_keys = set([param.name for param in tool_entity.params])
                params = draft_tool["params"]

                if set(draft_tool["params"].keys()) - param_keys:
                    params = {
                        param.name: param.default
                        for param in tool_entity.params
                        if param.default is not None
                    }
                # 6. 数据都存在，并且参数已经校验完毕，可以将数据添加到validate_tools
                validate_tools.append({
                    **draft_tool,
                    "params": params,
                })

                # 7. 组装内置工具展示信息
                provider_entity = provider.provider_entity
                tools.append({
                    "type": "builtin_tool",
                    "provider": {
                        "id": provider_entity.name,
                        "name": provider_entity.name,
                        "label": provider_entity.label,
                        "icon": f"{request.scheme}://{request.host}/builtin-tools/{provider_entity.name}/icon",
                        "description": provider_entity.description,
                    },
                    "tool": {
                        "id": tool_entity.name,
                        "name": tool_entity.name,
                        "label": tool_entity.label,
                        "description": tool_entity.description,
                        "params": params,
                    }
                })
            elif draft_tool["type"] == "api_tool":
                # 8.查询数据获取对应的工具记录，并检测是否存在
                tool_record = self.db.session.query(ApiTool).filter(
                    ApiTool.provider_id == draft_tool["provider_id"],
                    ApiTool.name == draft_tool["tool_id"],
                ).one_or_none()

                if not tool_record:
                    continue

                # 9. 数据校验通过，往validate_tools 添加数据
                validate_tools.append(draft_tool)

                # 10. 组装api工具展示信息
                provider = tool_record.provider
                tools.append({
                    "type": "api_tool",
                    "provider": {
                        "id": str(provider.id),
                        "name": provider.name,
                        "label": provider.name,
                        "icon": provider.icon,
                        "description": provider.description,
                    },
                    "tool": {
                        "id": str(tool_record.id),
                        "name": tool_record.name,
                        "label": tool_record.name,
                        "description": tool_record.description,
                        "params": {}
                    },
                })

        # 11. 判断是否需要更新草稿配置中的工具列表信息
        if draft_tools != validate_tools:
            # 12. 更新草稿配置中的工具列表
            self.update(
                draft_app_config,
                tools=validate_tools,
            )

        # 13. 校验知识库列表，如果引用了不存在/被删除的知识库，需要剔除数据并更新，同时获取知识库额外信息
        datasets = []
        draft_datasets = draft_app_config.datasets

        # 根据draft_datasets中的知识库id列表查询数据库中的知识库记录
        dataset_records = self.db.session.query(Dataset).filter(
            Dataset.id.in_(draft_datasets)
        ).all()
        dataset_dict: dict[str, Dataset] = {str(dataset_record.id): dataset_record for dataset_record in
                                            dataset_records}
        dataset_sets = set(dataset_dict.keys())

        # 14. 计算存在的知识库id列表，为了保留原始顺序，使用列表循环的方式来判断
        exist_dataset_ids = [dataset_id for dataset_id in draft_datasets if dataset_id in dataset_sets]

        # 15. 判断是否存在已删除的知识库，如果存在则更新
        if set(exist_dataset_ids) != set(draft_datasets):
            self.update(draft_app_config, datasets=exist_dataset_ids)

        # 16. 循环获取知识库列表
        for dataset_id in exist_dataset_ids:
            dataset = dataset_dict.get(str(dataset_id))
            datasets.append({
                "id": str(dataset.id),
                "name": dataset.name,
                "icon": dataset.icon,
                "description": dataset.description,
            })

        # todo: 17. 校验工作流列表对应的数据
        workflows = []

        # 18. 将数据转换成字典返回
        return {
            "id": str(draft_app_config.id),
            "model_config": draft_app_config.model_config,
            "dialog_round": draft_app_config.dialog_round,
            "preset_prompt": draft_app_config.preset_prompt,
            "tools": tools,
            "workflows": workflows,
            "datasets": datasets,
            "retrieval_config": draft_app_config.retrieval_config,
            "long_term_memory": draft_app_config.long_term_memory,
            "opening_statement": draft_app_config.opening_statement,
            "opening_questions": draft_app_config.opening_questions,
            "speech_to_text": draft_app_config.speech_to_text,
            "text_to_speech": draft_app_config.text_to_speech,
            "review_config": draft_app_config.review_config,
            "updated_at": datetime_to_timestamp(draft_app_config.updated_at),
            "created_at": datetime_to_timestamp(draft_app_config.created_at),
        }
