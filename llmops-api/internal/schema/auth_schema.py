#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/12 12:09
@Author         : jiayinkong@163.com
@File           : auth_schema.py
@Description    : 
"""
from flask_wtf import FlaskForm
from marshmallow import Schema, fields
from wtforms import StringField
from wtforms.validators import DataRequired, Length, Email, regexp

from pkg.password.password import password_pattern


class PasswordLoginReq(FlaskForm):
    """账号密码登录请求"""
    email = StringField("email", validators=[
        DataRequired("登录邮箱不能为空"),
        Email("登录邮箱格式错误"),
        Length(min=5, max=254, message="登录邮箱长度在5-254个字符")
    ])
    password = StringField("password", validators=[
        DataRequired("账号密码不能为空"),
        regexp(regex=password_pattern, message="密码至少包含一个字母，一个数字，并且长度为8-16"),
    ])


class PasswordLoginResp(Schema):
    """账号密码登录响应"""
    access_token = fields.String()
    expire_at = fields.Integer()
