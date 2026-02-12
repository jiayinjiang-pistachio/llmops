#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/19 16:41
@Author         : jiayinkong@163.com
@File           : api_key.py
@Description    : 
"""
from sqlalchemy import PrimaryKeyConstraint, Column, UUID, text, String, Boolean, DateTime, Index

from internal.extension.database_extension import db
from internal.model import Account


class ApiKey(db.Model):
    """API密钥模型"""
    __tablename__ = "api_key"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_api_key_id"),
        Index("api_key_account_id_idx", "account_id"),
        Index("api_key_api_key_idx", "api_key"),
    )

    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))
    account_id = Column(UUID, nullable=False)  # 关联账号 id
    api_key = Column(String(255), nullable=False, server_default=text("''::character varying"))
    is_active = Column(Boolean, nullable=False, server_default=text("false"))
    remark = Column(String(255), nullable=False, server_default=text("''::character varying"))
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP(0)'),
        server_onupdate=text('CURRENT_TIMESTAMP(0)')
    )
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))

    @property
    def account(self) -> "Account":
        """只读属性，返回该密钥归属的账号信息"""
        return db.session.query(Account).get(self.account_id)
