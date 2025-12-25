#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/12/25 17:38
@Author         : jiayinkong@163.com
@File           : api_tool_schema.py
@Description    : 
"""
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class ValidateOpenAPISchemaReq(FlaskForm):
    """校验OpenAPI规范字符串请求"""
    openapi_schema = StringField("openapi_schema", validators=[
        DataRequired(message="openapi_schema字符串不能为空")
    ])
