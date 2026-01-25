#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/25 20:02
@Author         : jiayinkong@163.com
@File           : workflow_handler.py
@Description    : 
"""
from dataclasses import dataclass
from uuid import UUID

from flask import request
from flask_login import login_required, current_user
from injector import inject

from internal.schema.workflow_schema import CreateWorkflowReq, UpdateWorkflowReq, GetWorkflowResp, \
    GetWorkflowsWithPageReq, GetWorkflowsWithPageResp
from internal.service import WorkflowService
from pkg.paginator import PageModel
from pkg.response import validate_error_json, success_json, success_message


@inject
@dataclass
class WorkflowHandler:
    """工作流处理器"""
    workflow_service: WorkflowService

    @login_required
    def get_workflows_with_page(self):
        """获取当前登录账号下的工作流分页列表数据"""
        # 1.提取请求并校验
        req = GetWorkflowsWithPageReq(request.args)
        if not req.validate():
            return validate_error_json(req.errors)

        # 2.获取分页列表数据
        workflows, paginator = self.workflow_service.get_workflows_with_page(req, current_user)

        # 3.构建响应并返回
        resp = GetWorkflowsWithPageResp(many=True)

        return success_json(PageModel(list=resp.dump(workflows), paginator=paginator))

    @login_required
    def create_workflow(self):
        """新增工作流"""
        # 1. 提取请求并校验
        req = CreateWorkflowReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2. 调用服务创建工作流
        workflow = self.workflow_service.create_workflow(req, current_user)

        return success_json({"id": workflow.id})

    def get_workflow(self, workflow_id: UUID):
        """根据传递的工作流id获取工作流详情"""
        workflow = self.workflow_service.get_workflow(workflow_id, current_user)
        resp = GetWorkflowResp()
        return success_json(resp.dump(workflow))

    @login_required
    def update_workflow(self, workflow_id: UUID):
        """根据传递的工作流id获取工作流详情"""
        # 1. 提取请求并校验
        req = UpdateWorkflowReq()
        if not req.validate():
            return validate_error_json(req.errors)

        self.workflow_service.update_workflow(workflow_id, current_user, **req.data)

        return success_message("修改工作流基础信息成功")

    @login_required
    def delete_workflow(self, workflow_id: UUID):
        """根据传递的工作流id删除指定的工作流"""
        self.workflow_service.delete_workflow(workflow_id, current_user)

        return success_message("删除工作流成功")
