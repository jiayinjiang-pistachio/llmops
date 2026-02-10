#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time           : 2025/11/16 09:21
@Author         : jiayinkong@163.com
@File           : app_handler.py
@Description    : 
"""
import os
from dataclasses import dataclass
from uuid import UUID

from flask import request
from flask_login import current_user, login_required
from injector import inject

from internal.core.language_model import LanguageModelManager
from internal.schema import (
    CreateAppReq, GetAppResp, GetPublishHistoriesWithPageReq, GetPublishHistoriesWithPageResp,
    FallbackHistoryToDraftReq, UpdateDebugConversationSummaryReq, DebugChatReq, GetDebugConversationMessagesWithPageReq,
    GetDebugConversationMessagesWithPageResp, GetAppsWithPageReq, GetAppsWithPageResp, UpdateAppReq
)
from internal.service import AppService
from internal.service.retrieval_service import RetrievalService
from pkg.paginator import PageModel
# from internal.task.demo_task import demo_task
from pkg.response import validate_error_json, success_json, success_message, compact_generate_response


@inject
@dataclass
class AppHandler:
    """应用控制器"""
    app_service: AppService
    retrieval_service: RetrievalService
    language_model_manager: LanguageModelManager

    @login_required
    def get_apps_with_page(self):
        """获取app应用列表分页数据"""
        # 1. 提取请求数据并校验
        req = GetAppsWithPageReq(request.args)
        if not req.validate():
            return validate_error_json(req.errors)

        # 2. 调用服务获取应用列表、分页数据
        apps, paginator = self.app_service.get_apps_with_page(req, current_user)

        # 3. 响应结构体
        resp = GetAppsWithPageResp(many=True)

        return success_json(PageModel(list=resp.dump(apps), paginator=paginator))

    @login_required
    def create_app(self):
        """调用服务创建新的app记录"""
        req = CreateAppReq()
        if not req.validate():
            return validate_error_json(req.errors)

        app = self.app_service.create_app(req, current_user)

        return success_json({"id": app.id})

    @login_required
    def get_app(self, app_id: UUID):
        """获取指定的应用基础信息"""
        app = self.app_service.get_app(app_id, current_user)
        resp = GetAppResp()

        return success_json(resp.dump(app))

    @login_required
    def update_app(self, app_id: UUID):
        """根据传递的app id和新应用信息，更新应用信息"""
        # 1. 提取请求数据并校验
        req = UpdateAppReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2. 调用服务更新应用信息
        self.app_service.update_app(app_id, current_user, **req.data)

        return success_message("修改Agent智能体应用成功")

    @login_required
    def delete_app(self, app_id: UUID):
        """根据传递的app id，删除应用"""
        self.app_service.delete_app(app_id, current_user)
        return success_message("删除Agent智能体应用成功")

    @login_required
    def copy_app(self, app_id: UUID):
        """根据传递的app_id，快速拷贝该应用"""
        app = self.app_service.copy_app(app_id, current_user)
        return success_json({"id": app.id})

    @login_required
    def get_draft_app_cconfig(self, app_id: UUID):
        """获取草稿配置信息"""
        draft_config = self.app_service.get_draft_app_config(app_id, current_user)

        return success_json(draft_config)

    @login_required
    def update_draft_app_config(self, app_id: UUID):
        """根据传递的应用id获取应用的最新草稿配置"""
        draft_app_config = request.get_json(force=True, silent=True) or {}

        # 2. 调用服务更新应用的草稿配置
        self.app_service.update_draft_app_config(app_id, draft_app_config, current_user)

        return success_message("更新应用草稿配置成功")

    @login_required
    def publish(self, app_id: UUID):
        """根据传递的应用id发布/更新特定的草稿配置信息"""
        self.app_service.publish_graft_app_config(app_id, current_user)
        return success_message("发布/更新应用配置成功")

    @login_required
    def cancel_publish(self, app_id: UUID):
        """根据传递的应用id，取消发布指定的应用配置信息"""
        self.app_service.cancel_publish_app_config(app_id, current_user)
        return success_message("取消发布应用配置成功")

    @login_required
    def get_publish_histories_with_page(self, app_id: UUID):
        """根据传递的应用id,获取应用发布历史列表"""
        # 1. 获取请求数据并校验
        req = GetPublishHistoriesWithPageReq(request.args)
        if not req.validate():
            return validate_error_json(req.errors)

        # 2. 调用服务获取分页列表数据
        app_config_version, paginator = self.app_service.get_publish_histories_with_page(app_id, req, current_user)

        # 3. 创建响应结构并返回
        resp = GetPublishHistoriesWithPageResp(many=True)

        return success_json(PageModel(list=resp.dump(app_config_version), paginator=paginator))

    @login_required
    def fallback_history_to_draft(self, app_id: UUID):
        """根据传递的应用Id+历史配置版本id，退回指定版本到草稿中"""

        # 思路就是：找到这个指定版本的app_config_version记录，把这个记录拷贝一份，粘贴覆盖app的当前的draft配置，完成覆盖即完成回退操作
        # 也就是说，app当前这条draft记录还是原来那条，只不过是值被替换了

        # 1. 提取数据并校验
        req = FallbackHistoryToDraftReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2. 调用服务回退指定版本到草稿
        self.app_service.fallback_history_to_draft(app_id, req.app_config_version_id.data, current_user)

        return success_message("回退历史配置至草稿成功")

    @login_required
    def get_debug_conversation_summary(self, app_id: UUID):
        """根据传递的应用id获取调试会话长期记忆"""
        summary = self.app_service.get_debug_conversation_summary(app_id, current_user)

        return success_json({"summary": summary})

    @login_required
    def update_debug_conversation_summary(self, app_id: UUID):
        """根据传递的应用id+摘要信息更新调试会话长期记忆"""
        # 1. 提取数据并校验
        req = UpdateDebugConversationSummaryReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2. 调用服务更新调试会话长期记忆
        self.app_service.update_debug_conversation_summary(app_id, req.summary.data, current_user)

        return success_message("更新AI应用长期记忆成功")

    @login_required
    def delete_debug_conversation(self, app_id: UUID):
        """根据传递的应用id，清空应用的调试会话记录"""
        self.app_service.delete_debug_conversation(app_id, current_user)
        return success_message("清空应用调试会话记录成功")

    @login_required
    def debug_chat(self, app_id: UUID):
        """提取数据并校验数据"""
        req = DebugChatReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2. 调用服务发起会话调试
        response = self.app_service.debug_chat(app_id, req.query.data, current_user)

        return compact_generate_response(response)

    @login_required
    def stop_debug_chat(self, app_id: UUID, task_id: UUID):
        """根据传递的应用id+任务id停止某个应用的指定调试会话"""
        self.app_service.stop_debug_chat(app_id, task_id, current_user)
        return success_message("停止应用调试会话成功")

    @login_required
    def get_debug_conversation_messages_with_page(self, app_id: UUID):
        """根据传递的应用id获取该应用的调试会话分页列表记录"""
        req = GetDebugConversationMessagesWithPageReq(request.args)
        if not req.validate():
            return validate_error_json(req.errors)

        # 2. 调用服务获取数据
        messages, paginator = self.app_service.get_debug_conversation_messages_with_page(app_id, req, current_user)

        # 3. 创建响应结构
        resp = GetDebugConversationMessagesWithPageResp(many=True)

        return success_json(PageModel(list=resp.dump(messages), paginator=paginator))

    @login_required
    def get_published_config(self, app_id: UUID):
        """根据传递的应用id获取应用的发布配置信息"""
        published_config = self.app_service.get_published_config(app_id, current_user)
        return success_json(published_config)

    @login_required
    def regenerate_web_app_token(self, app_id: UUID):
        """根据传递的应用idh重新生成WebApp凭证标识"""
        token = self.app_service.regenerate_web_app_token(app_id, current_user)
        return success_json({"token": token})

    @login_required
    def ping(self):
        provider = self.language_model_manager.get_provider("zhipuai")
        model_entity = provider.get_model_entity("glm-4.7-flash")
        model_class = provider.get_model_class(model_entity.model_type)
        llm = model_class(**{
            **model_entity.attributes,
            "features": model_entity.features,
            "metadata": model_entity.metadata,
        })

        return success_json({
            "content": llm.invoke("你好，你是？").content,
            "features": llm.features,
            "metadata": llm.metadata,
        })

    @login_required
    def ping_temp2(self):
        # model_class = self.language_model_manager.get_model_class_by_provider_and_model("google", "gemini-1.5-flash")
        # model_class = self.language_model_manager.get_model_class_by_provider_and_model(
        #     "google",
        #     "gemini-3-flash-preview"
        # )
        model_class = self.language_model_manager.get_model_class_by_provider_and_model("openai", "gpt-5-mini")

        # model_class = self.language_model_manager.get_model_class_by_provider_and_model(
        #     "zhipuai",
        #     "glm-4.6v-flash",
        # )

        # model_class = self.language_model_manager.get_model_class_by_provider_and_model(
        #     "deepseek",
        #     "deepseek-reasoner"
        # )

        # llm = model_class(
        #     model="gemini-3-flash-preview",
        #     api_key=os.getenv("GPTSAPI_API_KEY"),
        #     base_url=os.getenv("OPENAI_API_BASE")
        # )

        # llm = model_class(
        #     model="gemini-2.5-flash-image-hd",
        #     api_key=os.getenv("GPTSAPI_API_KEY"),
        #     base_url=os.getenv("OPENAI_API_BASE_V3")
        # )

        llm = model_class(
            model="gpt-5-mini",
            api_key=os.getenv("GPTSAPI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE")
        )

        # llm = model_class(
        #     model="glm-4.6v-flash",
        # )

        # llm = model_class(
        #     api_key=os.getenv("DEEPSEEK_API_KEY"),
        #     base_url=os.getenv("DEEPSEEK_BASE_URL"),
        #     model="deepseek-reasoner",
        #     temperature=0.5,
        # )

        return success_message(llm.invoke("你好，请告诉我你的模型，你会生成图片吗").content)

    @login_required
    def ping_temp(self):
        # pass
        # from internal.core.workflow import Workflow
        # from internal.core.workflow.entities.workflow_entity import WorkflowConfig
        # workflow = Workflow(workflow_config=WorkflowConfig(
        #     name="ZenSnack-工作流",
        #     description="测试工作流",
        # ))
        #
        # return success_json(workflow.invoke({"query": "你好，你是？", "username": "Zennell"}))

        from internal.core.workflow import Workflow
        from internal.core.workflow.entities.workflow_entity import WorkflowConfig

        # 工作流流程: 开始->(知识库检索->大语言模型->代码执行)/(Http请求->模板转换)/(工具1)/(工具2)->结束
        nodes = [
            {
                "id": "18d938c4-ecd7-4a6b-9403-3625224b96cc",
                "node_type": "start",
                "title": "开始",
                "description": "工作流的起点节点，支持定义工作流的起点输入等信息。",
                "inputs": [
                    {
                        "name": "query",
                        "type": "string",
                        "description": "用户输入的query信息",
                        "required": True,
                        "value": {
                            "type": "generated",
                            "content": "",
                        }
                    },
                    {
                        "name": "location",
                        "type": "string",
                        "description": "需要查询的城市地址信息",
                        "required": False,
                        "value": {
                            "type": "generated",
                            "content": "",
                        }
                    },
                    {
                        "name": "q",
                        "type": "string",
                        "description": "用户需要查询的单词翻译",
                        "required": False,
                        "value": {
                            "type": "generated",
                            "content": "",
                        }
                    },
                ]
            },
            {
                "id": "868b5769-1925-4e7b-8aa4-af7c3d444d91",
                "node_type": "dataset_retrieval",
                "title": "知识库检索",
                "description": "",
                "inputs": [
                    {
                        "name": "query",
                        "type": "string",
                        "value": {
                            "type": "ref",
                            "content": {
                                "ref_node_id": "18d938c4-ecd7-4a6b-9403-3625224b96cc",
                                "ref_var_name": "query"
                            }
                        }
                    }
                ],
                "dataset_ids": [
                    "8210bfbd-0baa-46f5-bcd4-fe2b789fb4f6",
                    "4e25b342-1a2b-40f9-86a7-da3052f2a75a"
                ],
            },
            {
                "id": "675fca50-1228-8008-82dc-0c714158534c",
                "node_type": "http_request",
                "title": "HTTP请求",
                "description": "",
                "url": "https://www.langchain.com/",
                "method": "get",
                "inputs": [],
            },
            {
                "id": "eba75e0b-21b7-46ed-8d21-791724f0740f",
                "node_type": "llm",
                "title": "大语言模型",
                "description": "",
                "inputs": [
                    {
                        "name": "query",
                        "type": "string",
                        "value": {
                            "type": "ref",
                            "content": {
                                "ref_node_id": "18d938c4-ecd7-4a6b-9403-3625224b96cc",
                                "ref_var_name": "query",
                            },
                        }
                    },
                    {
                        "name": "context",
                        "type": "string",
                        "value": {
                            "type": "ref",
                            "content": {
                                "ref_node_id": "868b5769-1925-4e7b-8aa4-af7c3d444d91",
                                "ref_var_name": "combine_documents",
                            },
                        }
                    },
                ],
                "prompt": (
                    "你是一个强有力的AI机器人，请根据用户的提问回复特定的内容，用户的提问是: {{query}}。\n\n"
                    "如果有必要，可以使用上下文内容进行回复，上下文内容:\n\n<context>{{context}}</context>"
                ),
                "model_config": {
                    "provider": "openai",
                    "model": "gpt-4o-mini",
                    "parameters": {
                        "temperature": 0.5,
                        "top_p": 0.85,
                        "frequency_penalty": 0.2,
                        "presence_penalty": 0.2,
                        "max_tokens": 8192,
                    },
                }
            },
            {
                "id": "623b7671-0bc2-446c-bf5e-5e25032a522e",
                "node_type": "template_transform",
                "title": "模板转换",
                "description": "",
                "inputs": [
                    {
                        "name": "location",
                        "type": "string",
                        "value": {
                            "type": "ref",
                            "content": {
                                "ref_node_id": "18d938c4-ecd7-4a6b-9403-3625224b96cc",
                                "ref_var_name": "location",
                            },
                        }
                    },
                    {
                        "name": "query",
                        "type": "string",
                        "value": {
                            "type": "ref",
                            "content": {
                                "ref_node_id": "18d938c4-ecd7-4a6b-9403-3625224b96cc",
                                "ref_var_name": "query"
                            }
                        }
                    }
                ],
                "template": "地址: {{location}}\n提问内容: {{query}}",
            },
            {
                "id": "4a9ed43d-e886-49f7-af9f-9e85d83b27aa",
                "node_type": "code",
                "title": "代码",
                "description": "",
                "inputs": [
                    {
                        "name": "combine_documents",
                        "type": "string",
                        "value": {
                            "type": "ref",
                            "content": {
                                "ref_node_id": "868b5769-1925-4e7b-8aa4-af7c3d444d91",
                                "ref_var_name": "combine_documents",
                            },
                        }
                    },
                ],
                "code": """def main(params):
            return {
                "first_100_documents": params.get("combine_documents", "")[:100]
            }""",
                "outputs": [
                    {
                        "name": "first_100_documents",
                        "type": "string",
                        "value": {
                            "type": "generated",
                            "content": "",
                        }
                    }
                ]
            },
            {
                "id": "2f6cf40d-0219-421b-92ff-229fdde15ecb",
                "node_type": "tool",
                "title": "内置工具",
                "description": "",
                "type": "builtin_tool",
                "provider_id": "google",
                "tool_id": "google_serper",
                "inputs": [
                    {
                        "name": "query",
                        "type": "string",
                        "value": {
                            "type": "ref",
                            "content": {
                                "ref_node_id": "18d938c4-ecd7-4a6b-9403-3625224b96cc",
                                "ref_var_name": "query"
                            }
                        }
                    }
                ]
            },
            {
                "id": "e9fc1f95-1a59-4ba4-a87d-2ad349287234",
                "node_type": "tool",
                "title": "API工具",
                "description": "",
                "type": "api_tool",
                "provider_id": "a96b86d0-d3e9-44d3-81dd-f4193734c52c",
                "tool_id": "YoudaoSuggest",
                "inputs": [
                    {
                        "name": "q",
                        "type": "string",
                        "value": {
                            "type": "ref",
                            "content": {
                                "ref_node_id": "18d938c4-ecd7-4a6b-9403-3625224b96cc",
                                "ref_var_name": "q"
                            }
                        }
                    }
                ],
                "outputs": [
                    {
                        "name": "api_tool_text",
                        "type": "string",
                        "value": {
                            "type": "generated",
                            "content": "",
                        }
                    },
                ]
            },
            {
                "id": "860c8411-37ed-4872-b53f-30afa0290211",
                "node_type": "end",
                "title": "结束",
                "description": "工作流的结束节点，支持定义工作流最终输出的变量等信息。",
                "outputs": [
                    {
                        "name": "query",
                        "type": "string",
                        "value": {
                            "type": "ref",
                            "content": {
                                "ref_node_id": "18d938c4-ecd7-4a6b-9403-3625224b96cc",
                                "ref_var_name": "query",
                            },
                        }
                    },
                    {
                        "name": "location",
                        "type": "string",
                        "value": {
                            "type": "ref",
                            "content": {
                                "ref_node_id": "18d938c4-ecd7-4a6b-9403-3625224b96cc",
                                "ref_var_name": "location",
                            },
                        }
                    },
                    {
                        "name": "username",
                        "type": "string",
                        "value": {
                            "type": "literal",
                            "content": "泽辉呀",
                        }
                    },
                    {
                        "name": "llm_output",
                        "type": "string",
                        "value": {
                            "type": "ref",
                            "content": {
                                "ref_node_id": "eba75e0b-21b7-46ed-8d21-791724f0740f",
                                "ref_var_name": "output"
                            }
                        }
                    },
                    {
                        "name": "template_combine",
                        "type": "string",
                        "value": {
                            "type": "ref",
                            "content": {
                                "ref_node_id": "623b7671-0bc2-446c-bf5e-5e25032a522e",
                                "ref_var_name": "output",
                            }
                        }
                    },
                    {
                        "name": "first_100_documents",
                        "type": "string",
                        "value": {
                            "type": "ref",
                            "content": {
                                "ref_node_id": "4a9ed43d-e886-49f7-af9f-9e85d83b27aa",
                                "ref_var_name": "first_100_documents",
                            }
                        }
                    },
                    {
                        "name": "youdao_suggest_result",
                        "type": "string",
                        "value": {
                            "type": "ref",
                            "content": {
                                "ref_node_id": "e9fc1f95-1a59-4ba4-a87d-2ad349287234",
                                "ref_var_name": "api_tool_text"
                            }
                        }
                    },
                    {
                        "name": "google_search_result",
                        "type": "string",
                        "value": {
                            "type": "ref",
                            "content": {
                                "ref_node_id": "2f6cf40d-0219-421b-92ff-229fdde15ecb",
                                "ref_var_name": "text",
                            }
                        }
                    },
                    {
                        "name": "http_request_text",
                        "type": "string",
                        "value": {
                            "type": "ref",
                            "content": {
                                "ref_node_id": "675fca50-1228-8008-82dc-0c714158534c",
                                "ref_var_name": "text",
                            }
                        }
                    },
                    {
                        "name": "http_request_status_code",
                        "type": "int",
                        "value": {
                            "type": "ref",
                            "content": {
                                "ref_node_id": "675fca50-1228-8008-82dc-0c714158534c",
                                "ref_var_name": "status_code",
                            }
                        }
                    }
                ]
            },
        ]

        edges = [
            # 开始->知识库检索
            {
                "id": "c8732feb-9c6d-4528-8103-ad33af9a162a",
                "source": "18d938c4-ecd7-4a6b-9403-3625224b96cc",
                "source_type": "start",
                "target": "868b5769-1925-4e7b-8aa4-af7c3d444d91",
                "target_type": "dataset_retrieval",
            },
            # 知识库检索->大语言模型
            {
                "id": "675f8403-cbf4-8008-9aae-76ecae12c675",
                "source": "868b5769-1925-4e7b-8aa4-af7c3d444d91",
                "source_type": "dataset_retrieval",
                "target": "eba75e0b-21b7-46ed-8d21-791724f0740f",
                "target_type": "llm",
            },
            # 大语言模型->代码code
            {
                "id": "675f8403-cbf4-8008-9aae-d508d8337e49",
                "source": "eba75e0b-21b7-46ed-8d21-791724f0740f",
                "source_type": "llm",
                "target": "4a9ed43d-e886-49f7-af9f-9e85d83b27aa",
                "target_type": "code",
            },
            # 代码code->结束
            {
                "id": "675f8403-cbf4-8008-9aae-d508d8337000",
                "source": "4a9ed43d-e886-49f7-af9f-9e85d83b27aa",
                "source_type": "code",
                "target": "860c8411-37ed-4872-b53f-30afa0290211",
                "target_type": "end",
            },
            # 开始->http请求
            {
                "id": "c8732feb-9c6d-4528-8103-ad33af9a1611",
                "source": "18d938c4-ecd7-4a6b-9403-3625224b96cc",
                "source_type": "start",
                "target": "675fca50-1228-8008-82dc-0c714158534c",
                "target_type": "http_request",
            },
            # http请求->模板转换
            {
                "id": "c8732feb-9c6d-4528-8103-ad33af9a1629",
                "source": "675fca50-1228-8008-82dc-0c714158534c",
                "source_type": "http_request",
                "target": "623b7671-0bc2-446c-bf5e-5e25032a522e",
                "target_type": "template_transform",
            },
            # 模板转换->结束
            {
                "id": "51e993f4-a832-48bc-8211-59b37acf678c",
                "source": "623b7671-0bc2-446c-bf5e-5e25032a522e",
                "source_type": "template_transform",
                "target": "860c8411-37ed-4872-b53f-30afa0290211",
                "target_type": "end",
            },
            # 开始->工具1
            {
                "id": "675f8533-de28-8228-9f27-d508d8337e00",
                "source": "18d938c4-ecd7-4a6b-9403-3625224b96cc",
                "source_type": "start",
                "target": "2f6cf40d-0219-421b-92ff-229fdde15ecb",
                "target_type": "tool",
            },
            # 工具1->结束
            {
                "id": "675f8533-de28-8008-9f27-d508d8337e00",
                "source": "2f6cf40d-0219-421b-92ff-229fdde15ecb",
                "source_type": "tool",
                "target": "860c8411-37ed-4872-b53f-30afa0290211",
                "target_type": "end",
            },
            # 开始->工具2
            {
                "id": "675f8533-de28-8228-9f27-d50812337e00",
                "source": "18d938c4-ecd7-4a6b-9403-3625224b96cc",
                "source_type": "start",
                "target": "e9fc1f95-1a59-4ba4-a87d-2ad349287234",
                "target_type": "tool",
            },
            # 工具2->结束
            {
                "id": "675f8533-de28-8008-9f27-d508d8937e00",
                "source": "e9fc1f95-1a59-4ba4-a87d-2ad349287234",
                "source_type": "tool",
                "target": "860c8411-37ed-4872-b53f-30afa0290211",
                "target_type": "end",
            },
        ]

        workflow = Workflow(workflow_config=WorkflowConfig(
            account_id=current_user.id,
            name="workflow",
            description="工作流组件",
            nodes=nodes,
            edges=edges,
        ))

        result = workflow.invoke({"query": "请给我一些油性皮肤护肤建议", "location": "广州", "q": "love"})

        return success_json({
            **result,
            "info": {
                "name": workflow.name,
                "description": workflow.description,
                "args_schema": workflow.args_schema.schema(),
            },
            "node_results": [node_result.dict() for node_result in result["node_results"]]
        })
