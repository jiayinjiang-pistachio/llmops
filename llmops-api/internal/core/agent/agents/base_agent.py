#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2026/1/8 11:28
@Author         : jiayinkong@163.com
@File           : base_agent.py
@Description    : 
"""
import uuid
from abc import abstractmethod
from threading import Thread
from typing import Optional, Any, Iterator

from langchain_core.language_models import BaseLanguageModel
from langchain_core.load import Serializable
from langchain_core.pydantic_v1 import PrivateAttr
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.graph.state import CompiledStateGraph

from internal.core.agent.agents.agent_queue_manager import AgentQueueManager
from internal.core.agent.entities.agent_entity import AgentConfig, AgentState
from internal.core.agent.entities.queue_entity import AgentResult, AgentThought, QueueEvent
from internal.exception import FailException


class BaseAgent(Serializable, Runnable):
    """基于Runnable的基础智能体基类"""
    llm: BaseLanguageModel
    agent_config: AgentConfig
    _agent: CompiledStateGraph = PrivateAttr(None)  # 为了让子类也能够访问 _agent
    _agent_queue_manager: AgentQueueManager = PrivateAttr(None)  # 为了让子类也能够访问 _agent_queue_manager

    class Config:
        # 字段允许随意类型，且不需要校验器
        arbitrary_types_only = True

    def __init__(self, llm: BaseLanguageModel, agent_config: AgentConfig, *args, **kwargs):
        """构造函数，初始化智能体图结构程序"""
        super().__init__(*args, llm=llm, agent_config=agent_config, **kwargs)

        self._agent = self._built_agent()
        self._agent_queue_manager = AgentQueueManager(
            user_id=agent_config.user_id,
            invoke_from=agent_config.invoke_from,
        )

    @abstractmethod
    def _built_agent(self) -> CompiledStateGraph:
        """构建智能体函数，等待子类实现"""
        raise NotImplementedError("_built_agent未实现")

    def invoke(self, input: AgentState, config: Optional[RunnableConfig] = None) -> AgentResult:
        """块内容响应，一次性生成完整内容返回"""
        # 1. 调用stream方法获取流式事件输出数据
        agent_result = AgentResult(query=input["messages"][0].content)

        agent_thoughts: dict[str, AgentThought] = {}
        for agent_thought in self.stream(input, config):
            # 2. 提取事件id
            event_id = str(agent_thought.id)

            # 3. 除了ping事件，其他事件都记录
            if agent_thought.event != QueueEvent.PING:

                # 单独处理agent_message事件，叠加处理
                if agent_thought.event == QueueEvent.AGENT_MESSAGE:
                    if event_id not in agent_thoughts:
                        # 初始化事件存储到agent_thoughts
                        agent_thoughts[event_id] = agent_thought
                    else:
                        # 叠加智能体消息事件
                        agent_thoughts[event_id] = agent_thoughts[event_id].model_copy(update={
                            "thought": agent_thoughts[event_id].thought + agent_thought.thought,
                            "answer": agent_thoughts[event_id].answer + agent_thought.answer,
                            "latency": agent_thought.latency,
                        })

                    # 更新智能体消息答案
                    agent_result.answer += agent_thought.answer
                else:
                    # 4. 处理其他事件，覆盖处理
                    agent_thoughts[event_id] = agent_thought

                    if agent_thought.event in [QueueEvent.STOP, QueueEvent.ERROR, QueueEvent.TIMEOUT]:
                        agent_result.status = agent_thought.event
                        agent_result.error = agent_thought.observation if agent_thought.event == QueueEvent.ERROR else ""

        agent_result.agent_thoughts = [agent_thought for agent_thought in agent_thoughts.values()]

        # next 相当于ts的find函数，找到第一个符合条件的就返回
        agent_result.message = next(
            (agent_thought.message for agent_thought in agent_thoughts.values()
             if agent_thought.event == QueueEvent.AGENT_MESSAGE),
            []
        )

        # 计算总耗时
        agent_result.latency = sum([agent_thought.latency for agent_thought in agent_thoughts.values()])

        return agent_result

    def stream(
            self,
            input: AgentState,
            config: Optional[RunnableConfig] = None,
            **kwargs: Optional[Any],
    ) -> Iterator[AgentThought]:
        """流式输出，每个node节点或LLM每生成一个token时则会返回响应内容"""
        # 1. 检测子类是否已构建Agent智能体，如果未构建则抛出错误
        if not self._agent:
            raise FailException("智能体未成功构建，请核实后尝试")

        # 2. 构建对应的任务id及数据初始化
        input["task_id"] = input.get("task_id", uuid.uuid4())
        input["history"] = input.get("history", [])
        input["iteration_count"] = input.get("iteration_count", 0)

        # 3. 创建子线程并执行
        thread = Thread(
            target=self._agent.invoke,
            args=(input,),
        )
        thread.start()

        # 4. 调用队列管理器监听数据并返回迭代器
        yield from self._agent_queue_manager.listen(input["task_id"])

    @property
    def agent_queue_manager(self) -> AgentQueueManager:
        """只读属性，返回智能体队列管理器"""
        return self._agent_queue_manager
