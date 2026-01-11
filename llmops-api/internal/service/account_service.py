#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/11 15:03
@Author         : jiayinkong@163.com
@File           : account_service.py
@Description    : 
"""
from dataclasses import dataclass
from uuid import UUID

from injector import inject

from internal.model import Account
from pkg.sqlalchemy import SQLAlchemy
from .base_service import BaseService


@inject
@dataclass
class AccountService(BaseService):
    """账号服务"""
    db: SQLAlchemy

    def get_account(self, account_id: UUID) -> Account:
        """根据account_id查询账号信息"""
        return self.get(Account, account_id)
