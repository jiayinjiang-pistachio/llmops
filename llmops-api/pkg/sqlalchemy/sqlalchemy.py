#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/11/20 22:47
@Author         : jiayinkong@163.com
@File           : sqlalchemy.py
@Description    : 
"""
from contextlib import contextmanager

from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy


class SQLAlchemy(_SQLAlchemy):
    """重写SQLAlchemy中的核心类，实现自动提交"""

    @contextmanager
    def auto_commit(self):
        try:
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
