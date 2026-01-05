#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/11/16 09:21
@Author         : jiayinkong@163.com
@File           : app_handler.py
@Description    : 
"""
import json
import os
import uuid
from dataclasses import dataclass
from operator import itemgetter
from queue import Queue
from threading import Thread
from typing import Dict, Any, Literal, Generator
from uuid import UUID

from injector import inject
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_core.memory import BaseMemory
from langchain_core.messages import ToolMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableConfig
from langchain_core.tracers import Run
from langchain_openai import ChatOpenAI
from langgraph.constants import END
from langgraph.graph import MessagesState, StateGraph

from internal.core.tools.builtin_tools.providers import BuiltinProviderManager
from internal.schema.app_schema import CompletionReq
from internal.service import AppService, VectorDatabaseService, APiToolService
from internal.task.demo_task import demo_task
from pkg.response import success_json, validate_error_json, success_message, compact_generate_response


@inject
@dataclass
class AppHandler:
    """应用控制器"""
    app_service: AppService
    vector_database_store: VectorDatabaseService
    provider_factory: BuiltinProviderManager
    api_tool_service: APiToolService
    builtin_proivder_manager: BuiltinProviderManager

    def create_app(self):
        """调用服务创建新的app记录"""
        app = self.app_service.create_app()
        return success_message(f"应用创建成功，id是{app.id}")

    def get_app(self, id: uuid.UUID):
        app = self.app_service.get_app(id)
        return success_message(f"应用已经成功获取，名称是{app.name}")

    def update_app(self, id: uuid.UUID):
        app = self.app_service.update_app(id)
        return success_message(f"应用已经成功修改，修改后的名称是：{app.name}")

    def delete_app(self, id: uuid.UUID):
        app = self.app_service.delete_app(id)
        return success_message(f"应用已经成功删除，id为{app.id}")

    @classmethod
    def _load_memory_variables(cls, input: Dict[str, Any], config: RunnableConfig) -> Dict[str, Any]:
        """加载记忆变量信息"""
        # 1. 从config中获取configurable
        configurable = config.get("configurable", {})
        configurable_memory = configurable.get("memory", None)
        if configurable_memory is not None and isinstance(configurable_memory, BaseMemory):
            return configurable_memory.load_memory_variables(input)
        return {"history": []}

    @classmethod
    def _save_context(cls, run_obj: Run, config: RunnableConfig) -> None:
        """存储对应的上下文信息到记忆实体中"""
        configurable = config.get("configurable", {})
        configurable_memory = configurable.get("memory", None)
        if configurable_memory is not None and isinstance(configurable_memory, BaseMemory):
            configurable_memory.save_context(run_obj.inputs, run_obj.outputs)

    def debug(self, app_id: UUID):
        """应用会话调试聊天接口，该接口为流式事件输出"""
        req = CompletionReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 创建队列并提取query数据
        q = Queue()
        query = req.query.data

        # 创建图程序列表
        def graph_app() -> None:
            """创建图程序应用并执行"""
            # 构建工具
            tools = [
                self.builtin_proivder_manager.get_tool("google", "google_serper")(),  # 调用，即获取到的是工具实例
                self.builtin_proivder_manager.get_tool("gaode", "gaode_weather")(),
                self.builtin_proivder_manager.get_tool("dalle", "dalle3")(),
            ]

            # 创建大语言模型LLM节点
            # def chatbot(state: MessagesState) -> MessagesState:
            #     """聊天机器人节点"""
            #     # 创建大语言模型
            #     llm = ChatOpenAI(
            #         model="gpt-4o-mini",
            #         api_key=os.getenv("GPTSAPI_API_KEY"),
            #         base_url=os.getenv("OPENAI_API_BASE")
            #     ).bind_tools(tools)
            #
            #     is_first_chunk = True
            #     is_tool_call = False
            #     gathered = None
            #     id = str(uuid.uuid4())
            #     # 调用stream()获取流式输出内容，并判断生成内容是文本还是工具调用参数
            #     for chunk in llm.stream(state["messages"]):
            #         # 检测是不是第一个区块，有些LLM第一个区块不会返回内容，需要抛弃掉
            #         if is_first_chunk and chunk.content == "" and not chunk.tool_calls:
            #             continue
            #
            #         # 叠加相应的区块
            #         if is_first_chunk:
            #             gathered = chunk
            #             is_first_chunk = False
            #         else:
            #             gathered += chunk
            #
            #         # 判断是文本生成还是工具调用，添加懂啊队列
            #         if chunk.tool_call_chunks:
            #             is_tool_call = True
            #             q.put({
            #                 "id": id,
            #                 "event": "agent_thought",
            #                 "data": json.dumps(chunk.tool_call_chunks)
            #             })
            #         else:
            #             q.put({
            #                 "id": id,
            #                 "event": "agent_message",
            #                 "data": chunk.content
            #             })
            #
            #     return {"messages": [gathered]}
            def chatbot(state: MessagesState) -> MessagesState:
                """聊天机器人节点"""
                llm = ChatOpenAI(
                    model="gpt-4o-mini",
                    api_key=os.getenv("GPTSAPI_API_KEY"),
                    base_url=os.getenv("OPENAI_API_BASE")
                ).bind_tools(tools)

                # 1. 初始化 gathered 为 None
                gathered = None
                message_id = str(uuid.uuid4())

                # 调用 stream() 获取流式输出
                for chunk in llm.stream(state["messages"]):
                    # 2. 聚合处理：LangChain 的 AIMessageChunk 支持通过 + 号自动合并 tool_calls
                    if gathered is None:
                        gathered = chunk
                    else:
                        gathered += chunk

                    # 3. 实时发送事件到前端队列
                    # 优先判断是否有工具调用片段
                    if chunk.tool_call_chunks:
                        q.put({
                            "id": message_id,
                            "event": "agent_thought",
                            "data": json.dumps(chunk.tool_call_chunks)
                        })
                    # 如果是普通文本内容且不为空
                    elif chunk.content:
                        q.put({
                            "id": message_id,
                            "event": "agent_message",
                            "data": chunk.content
                        })

                # 4. 健壮性检查：
                # 某些模型在流式结束时，gathered.tool_calls 可能还是空的（如果 ID/Name 在 Chunk 中没对齐）
                # 手动触发一次转换，确保 tool_calls 被正确解析
                if gathered.tool_call_chunks and not gathered.tool_calls:
                    # 这一步通常在 += 过程中由 LangChain 自动完成，
                    # 但如果遇到 Keyerror，说明聚合时的对象类型或数据结构有瑕疵
                    pass

                return {"messages": [gathered]}

            def tool_executor(state: MessagesState) -> MessagesState:
                """工具执行节点"""
                # 提取数据状态中的tool_calls
                tool_calls = state["messages"][-1].tool_calls

                # 将工具列表转换成字典方便使用
                tools_by_name = {
                    tool.name: tool
                    for tool in tools
                }
                print(f"tools_by_name: {tools_by_name}")

                # 执行工具并得到对应的结果
                messages = []
                for tool_call in tool_calls:
                    id = str(uuid.uuid4())
                    print(f"tool_call: {tool_call}")
                    # 如果模型返回了空的工具名，直接跳过，避免 KeyError
                    if not tool_call["name"]:
                        continue
                    tool = tools_by_name[tool_call["name"]]
                    tool_result = tool.invoke(tool_call["args"])
                    messages.append(ToolMessage(
                        tool_call_id=tool_call["id"],
                        content=json.dumps(tool_result),
                        name=tool_call["name"],
                    ))
                    q.put({
                        "id": id,
                        "event": "agent_action",
                        "data": json.dumps(tool_result)
                    })
                return {"messages": messages}

            def route(state: MessagesState) -> Literal["tool_executor", "__end__"]:
                """定义路由节点，用于确认下一步步骤"""
                ai_message = state["messages"][-1]
                if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
                    return "tool_executor"
                return END

            # 创建状态图
            graph_builder = StateGraph(MessagesState)

            # 添加节点
            graph_builder.add_node("llm", chatbot)
            graph_builder.add_node("tool_executor", tool_executor)

            # 添加边
            graph_builder.set_entry_point("llm")
            graph_builder.add_conditional_edges("llm", route)
            graph_builder.add_edge("tool_executor", "llm")

            # 编译图程序为可运行组件
            graph = graph_builder.compile()

            # 调用图结构程序并获取结果
            result = graph.invoke({"messages": [("human", query)]})
            print("最终结果", result)
            q.put(None)

        def stream_event_response() -> Generator:
            while True:
                item = q.get()
                if item is None:
                    break
                yield f"event: {item.get('event')}\n\ndata: {json.dumps(item)}\n\n"
                q.task_done()

        t = Thread(target=graph_app)
        t.start()

        return compact_generate_response(stream_event_response())

    def _debug(self, app_id: UUID):
        """聊天接口"""
        # 1. 提取从接口中获取的输入
        req = CompletionReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2. 构建prompt和记忆
        system_prompt = "你是一个强大的聊天机器人，能根据对应的上下文和历史对话信息回复用户问题。\n\n<context>{context}</context>"
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder("history"),
            ("human", "{query}")
        ])
        memory = ConversationBufferWindowMemory(
            k=3,
            input_key="query",
            return_messages=True,
            output_key="output",
            chat_memory=FileChatMessageHistory("./storage/memory/chat_history.txt")
        )

        # 3. 创建llm
        llm = ChatOpenAI(
            model="gpt-4",
            api_key=os.getenv("GPTSAPI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE"),
        )

        # 4. 创建链应用
        retriever = self.vector_database_store.get_retriever() | self.vector_database_store.combine_documents
        chain = (
                RunnablePassthrough.assign(
                    history=RunnableLambda(self._load_memory_variables) | itemgetter("history"),
                    context=itemgetter("query") | retriever
                ) | prompt | llm | StrOutputParser()
        ).with_listeners(
            on_end=self._save_context
        )

        # 5. 调用链生成内容
        chain_input = {"query": req.query.data}
        content = chain.invoke(chain_input, config={"configurable": {"memory": memory}})

        return success_json({"content": content})

    def ping(self):
        demo_task.delay(uuid.uuid4())
        return self.api_tool_service.api_tool_invoke()
        # providers = self.provider_factory.get_provider_entities()
        # return success_json({"providers": [provider.dict() for provider in providers]})
        # raise FailException("数据未找到")
