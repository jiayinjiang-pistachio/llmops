#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/6 14:58
@Author         : jiayinkong@163.com
@File           : conversation.py
@Description    : 
"""
from datetime import datetime

from sqlalchemy import PrimaryKeyConstraint, Column, UUID, text, String, Text, Boolean, DateTime, Integer, Numeric, \
    Float, func, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from internal.extension.database_extension import db


class Conversation(db.Model):
    """交流会话模型"""
    __tablename__ = "conversation"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_conversation_id"),
        Index("conversation_app_id_idx", "app_id"),
        Index("conversation_created_by_idx", "created_by"),
    )

    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))
    app_id = Column(UUID, nullable=False)
    name = Column(String(255), nullable=False, server_default=text("''::character varying"))
    summary = Column(Text, nullable=False, server_default=text("''::text"))
    is_pinned = Column(Boolean, nullable=False, server_default=text("false"))
    is_delete = Column(Boolean, nullable=False, server_default=text("false"))
    invoke_from = Column(String(255), nullable=False, server_default=text("''::character varying"))
    created_by = Column(
        UUID,
        nullable=True,
    )  # 会话创建者，会随着invoke_from的差异记录不同的信息，其中web_app和debugger会记录账号id、service_api会记录终端用户id
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP(0)'),
        onupdate=datetime.now,
    )
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))

    @property
    def is_new(self) -> bool:
        """只读属性，判断该会话是否第一次创建"""
        message_count = db.session.query(func.count(Message.id)).filter(
            Message.conversation_id == self.id
        ).scalar()

        return False if message_count > 1 else True


class Message(db.Model):
    """交流消息模型"""
    __tablename__ = "message"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_message_id"),
        Index("message_conversation_id_idx", "conversation_id"),
        Index("message_created_by_idx", "created_by"),
    )

    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))

    # 消息关联的记录
    app_id = Column(UUID, nullable=False)
    conversation_id = Column(UUID, nullable=False)
    invoke_from = Column(String(255), nullable=False, server_default=text("''::character varying"))
    created_by = Column(UUID, nullable=False)

    # 消息关联的原始问题
    query = Column(Text, nullable=False, server_default=text("''::text"))  # 用户提问的原始query
    message = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))  # 产生answer的消息列表
    message_token_count = Column(Integer, nullable=False, server_default=text("0"))  # 消息列表的token总数
    message_unit_price = Column(Numeric(10, 7), nullable=False, server_default=text("0.0"))  # 消息的单价
    message_price_unit = Column(Numeric(10, 4), nullable=False, server_default=text("0.0"))  # 消息的价格单位

    # 消息关联的答案信息
    answer = Column(Text, nullable=False, server_default=text("''::text"))  # Agent 生产的消息答案
    answer_token_count = Column(Integer, nullable=False, server_default=text("0"))  # 消息答案的token数
    answer_unit_price = Column(Numeric(10, 7), nullable=False, server_default=text("0.0"))  # token 的单位价格
    answer_price_unit = Column(Numeric(10, 4), nullable=False, server_default=text("0.0"))  # token的价格单位

    # 消息的相关统计信息
    latency = Column(Float, nullable=False, server_default=text("0.0"))  # 消息的总耗时
    is_deleted = Column(Boolean, nullable=False, server_default=text("false"))  # 软删除标记
    status = Column(String(255), nullable=False, server_default=text("''::character varying"))  # 消息的状态，涵盖正常、错误、停止
    error = Column(Text, nullable=False, server_default=text("''::text"))  # 发生错误时记录的信息
    total_token_count = Column(Integer, nullable=False, server_default=text("0"))  # 消耗的总token数，计算步骤的消耗
    total_price = Column(Numeric(10, 7), nullable=False, server_default=text("0.0"))  # 消耗的总价格，计算步骤的总消耗

    # 消息时间相关信息
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP(0)'),
        onupdate=datetime.now,
    )
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))

    # @property
    # def agent_thoughts(self) -> list["MessageAgentThought"]:
    #     """只读属性，返回消息智能体推理过程列表"""
    #     return db.session.query(MessageAgentThought).filter(
    #         MessageAgentThought.message_id == self.id,
    #     ).order_by(asc("position")).all()

    # 智能体推理列表，创建表关联
    agent_thoughts = relationship(
        "MessageAgentThought",  # 关联的模型名字
        backref="msg",  # 反向引用
        # lazy="selectin",  # 加载方式
        lazy="select",  # 默认不加载，查询时按需指定
        passive_deletes="all",
        uselist=True,  # 表示得到的是列表数据
        foreign_keys=[id],
        primaryjoin="MessageAgentThought.message_id == Message.id"
    )


class MessageAgentThought(db.Model):
    """智能体消息推理模型，用于记录Agent生成最终消息答案时"""
    __tablename__ = "message_agent_thought"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_message_agent_thought_id"),
        Index("message_agent_thought_app_id_idx", "app_id"),
        Index("message_agent_thought_conversation_id_idx", "conversation_id"),
        Index("message_agent_thought_message_id_idx", "message_id"),
    )

    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))

    # 推理步骤关联信息
    app_id = Column(UUID, nullable=False)
    conversation_id = Column(UUID, nullable=False)
    message_id = Column(UUID, nullable=False)
    invoke_from = Column(
        String(255),
        nullable=False,
        server_default=text("''::character varying"),
    )
    created_by = Column(UUID, nullable=False)

    # 该步骤在消息中执行的位置
    position = Column(Integer, nullable=False, server_default=text("0"))

    # 推理观察，分别记录LLM与非LLM产生的消息
    event = Column(Text, nullable=False, server_default=text("''::text"))
    tool = Column(Text, nullable=False, server_default=text("''::text"))  # 工具名称
    tool_input = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))

    thought = Column(Text, nullable=False, server_default=text("''::text"))  # 推理内容
    observation = Column(Text, nullable=False, server_default=text("''::text"))  # 观察内容

    # Agent推理观察步骤使用的消息列表（传递prompt消息内容）
    message = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    message_token_count = Column(Integer, nullable=False, server_default=text("0"))
    message_unit_price = Column(Numeric(10, 7), nullable=False, server_default=text("0.0"))
    message_price_unit = Column(Numeric(10, 4), nullable=False, server_default=text("0"))

    # LLM 生成内容相关（生成内容）
    answer = Column(Text, nullable=False, server_default=text("''::text"))
    answer_token_count = Column(Integer, nullable=False, server_default=text("0"))
    answer_unit_price = Column(Numeric(10, 7), nullable=False, server_default=text("0.0"))  # 单价，所有LLM的计算方式统一为CNY
    answer_price_unit = Column(Numeric(10, 4), nullable=False,
                               server_default=text("0.0"))  # 价格单位，值为1000代表1000token对应的单价

    # Agent 推理观察统计相关
    total_token_count = Column(Integer, nullable=False, server_default=text("0"))
    total_price = Column(Numeric(10, 7), nullable=False, server_default=text("0.0"))
    latency = Column(Float, nullable=False, server_default=text("0.0"))

    # 时间相关信息
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP(0)'),
        onupdate=datetime.now,
    )
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))
