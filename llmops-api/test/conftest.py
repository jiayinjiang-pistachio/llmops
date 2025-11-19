#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/11/18 20:14
@Author         : jiayinkong@163.com
@File           : conftest.py.py
@Description    : 
"""
import pytest

from app.http.app import app


@pytest.fixture
def client():
    """获取Flask应用的测试应用，并返回"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
