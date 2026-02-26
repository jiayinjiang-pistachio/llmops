# llmops

**快速导航**：[直接查看实现效果](#平台核心功能)

## 项目分析（架构与实现概览）

**llmops** 是一个 **LLM Ops / AI Agent 应用编排平台**，支持应用编排、知识库、插件、工作流、发布与统计分析，并提供 WebApp 嵌入与开放 API。

---

### 后端 (llmops-api)

- **技术栈**：Flask、SQLAlchemy、Redis、Weaviate、Celery、Injector、LangChain / LangGraph
- **分层**：Handler → Service → Core/Model，`Router` 统一注册路由

#### 核心模块与实现要点

**1. Agent**

- `BaseAgent`：基于 Runnable + LangGraph `StateGraph(AgentState)`，子类实现 `_built_agent()`。
- `FunctionCallAgent`：图结构为 preset_operation → long_term_memory_recall → llm ⇄ tools；支持输入/输出审核、长期记忆、流式输出；LLM 支持 `bind_tools` 时绑定工具，按 token 流式产出并区分 thought/message，通过 `AgentQueueManager` 向队列推送事件（AGENT_MESSAGE、AGENT_THOUGHT、AGENT_ACTION、DATASET_RETRIEVAL、AGENT_END 等）。
- `ReACTAgent`：继承 FunctionCallAgent，在不支持 function call 的模型上使用 ReACT：在 system prompt 中注入工具描述，LLM 输出用 ```json 包裹的 name/args 解析为 tool_calls，并做了消息清洗与角色交替以兼容智谱等模型。
- 流式：Agent 在子线程中 `invoke` 图，主线程通过 `AgentQueueManager.listen(task_id)` 从队列消费并 yield；停止/超时通过 Redis 标记与 PING 保活。

**2. 工作流**

- `Workflow` 继承 LangChain `BaseTool`，内部用 `StateGraph(WorkflowState)`，根据 `WorkflowConfig` 的 nodes/edges 动态建图。
- 节点类型：Start、End、LLM、TemplateTransform、DatasetRetrieval、Code、Tool、HttpRequest；边支持多源汇聚（`add_edge(source_nodes, target_node)`）。
- 图校验：唯一开始/结束、邻接表/逆邻接表、BFS 连通性、Kahn 判环、inputs 中对前置节点变量的引用校验。
- 执行：`_run` 调用 `_workflow.invoke({"inputs": kwargs})`，也可 `stream` 按节点输出。

**3. 知识库**

- 数据模型：Dataset → Document → Segment；ProcessRule 存分段规则；KeywordTable 存全文检索；DatasetQuery 存检索日志。
- 文档构建：`DocumentService.create_documents` 写 Document 并触发 Celery `build_documents`；`IndexingService.build_documents`：FileExtractor（按扩展名选 PyPDF/Unstructured* 等）加载 → ProcessRuleService 分割 → EmbeddingsService + JiebaService 建向量与关键词索引 → VectorDatabaseService 写入 Weaviate，Segment 与 KeywordTable 落库。
- 检索：`RetrievalService.search_in_datasets` 按策略选 SemanticRetriever、FullTextRetriever 或 EnsembleRetriever；并封装成 `dataset_retrieval` 工具供 Agent 调用。

**4. 应用 (App)**

- 草稿/发布双配置（AppConfigVersion）；默认配置在 `app_entity.DEFAULT_APP_CONFIG`（model_config、tools、workflows、datasets、retrieval_config、长期记忆、review_config、开场白与建议问题等）。
- 调试会话与 WebApp 会话通过 `InvokeFrom` 区分；发布后通过 token 获取 WebApp 配置并对话。
- 辅助 Agent 可自动创建应用：LLM 生成 preset_prompt，DALL·E 生成 icon，写入草稿并可选关联工作流等。

**5. 插件**

- 内置：`BuiltinProviderManager` 加载各 provider（如 google_serper、dalle、gaode_weather、current_time 等）的 YAML 与实现。
- 自定义：OpenAPI Schema 校验与动态调用，`ApiProviderManager` 管理 API 工具；工作流中的 Tool 节点可调内置或 API 工具。

**6. 语言模型**

- `LanguageModelManager` 从 `providers.yaml` 加载多 provider（如 openai、deepseek），按 provider+model 返回 `BaseLanguageModel`；模型能力通过 `ModelFeature`（如 TOOL_CALL、AGENT_THOUGHT）选择 FunctionCall 或 ReACT。

**7. 认证与开放接口**

- Flask-Login + 账号密码；OAuth（如 GitHub）；API Key 用于 `/openapi/chat` 等开放接口。WebApp 使用 token，不要求登录用户身份。

---

### 前端 (llmops-ui)

- **技术栈**：Vue 3、Vite、Pinia、Vue Router、Arco Design、Vue Flow、ECharts、markdown-it 等。
- **路由**：首页、空间（应用/自定义 API 插件/工作流/知识库）、知识库文档与片段 CRUD、应用广场、开放 API（含 API Key）、应用详情/发布/分析、工作流详情、WebApp 嵌入页、登录/授权、404/403。
- **与后端对应**：账号与登录、应用编排与调试会话、工作流编排与调试、知识库与文档/分段管理、内置与 API 插件、开放 API、WebApp 对话与会话列表、应用统计分析。

---

<a id="平台核心功能"></a>

# 平台核心功能

## 应用编排
- 关联工具

- 关联工作流

- 关联知识库

- 开启长期记忆

- 设置对话开场白及预设问题

- 设置LLM及参数

- 建议问题开启/关闭

- 内容审查
![插件截图.png](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/abcb2d1b6f4f4e37997f2973eb845da9~tplv-k3u1fbpfcp-watermark.image?)
![image.png](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/756c992d79cd4f2ab221b729ca26df54~tplv-k3u1fbpfcp-watermark.image?)
![image.png](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/5f524030435e440f904010559650a927~tplv-k3u1fbpfcp-watermark.image?)
![image.png](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/6c3e62457e374c5ebc3f7ae06135b72b~tplv-k3u1fbpfcp-watermark.image?)
![image.png](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/02115094d1824a2086c62e762a2884b5~tplv-k3u1fbpfcp-watermark.image?)
可以在内容审查这里对用户的输入和LLM的输出内容进行敏感词处理
![image.png](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/5b384dbbeb1545e9a30cf187ee5ea157~tplv-k3u1fbpfcp-watermark.image?)
- 让LLM优化人设与预设prompt
![image.png](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/249cd8c6e82f47d1b3a4ba1788f53547~tplv-k3u1fbpfcp-watermark.image?)
![image.png](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/ae8084b9c776444e912c48f50601444f~tplv-k3u1fbpfcp-watermark.image?)
点击替换就可以把LLM生成的预设提示词填充到左侧的`人设与回复逻辑`输入框里，这段文案会在用户提问AI时，作为`系统提示词中的预设提示词`传给LLM
![image.png](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/6b0961e6178941b6965edd167984d1f4~tplv-k3u1fbpfcp-watermark.image?)

## 知识库
1. 新建知识库
![iShot_2026-02-20_21.16.30.png](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/6313f01d36294881a7a3608452a1a31b~tplv-k3u1fbpfcp-watermark.image?)

2. 上传文件
![image.png](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/eb33984ee9cb4f43976eb1845eeeb3a8~tplv-k3u1fbpfcp-watermark.image?)

3. 分段设置，可自动分段清洗、可自定义，这里选择自定义
![image.png](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/9a1e0e0c85a24ca7afc2d30be12992e7~tplv-k3u1fbpfcp-watermark.image?)

4. 数据处理
![image.png](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/00e25c4f883f4d0fad39034508d2b8b4~tplv-k3u1fbpfcp-watermark.image?)
![image.png](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/00bf09da14aa43b4accf656088e596bd~tplv-k3u1fbpfcp-watermark.image?)

5. 召回测试<br>
全文（关键词）检索
![image.png](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/5ec83f92ed6d4e07a15b59b542dd2948~tplv-k3u1fbpfcp-watermark.image?)
相似性检索
![image.png](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/53da7bbfe3f54986a0b9f9ff50298fcc~tplv-k3u1fbpfcp-watermark.image?)


## 插件
有内置插件，也可以自定义插件
![image.png](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/b6179545df284d1683b3ef872c23b9c2~tplv-k3u1fbpfcp-watermark.image?)

自定义插件，遵循 `openapi` 规范
![image.png](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/e0b284c66e7c4407bac447b179b1ed09~tplv-k3u1fbpfcp-watermark.image?)

OpenAPI Schema
```json
{
    "description": "这是一个查询对应英文单词字典的工具", 
    "server": "https://dict.youdao.com", 
    "paths": {
        "/suggest": {
            "get": {
                "description": "根据传递的单词查询其字典信息", 
                "operationId": "YoudaoSuggest", 
                "parameters": [
                    {
                        "name": "q", 
                        "in": "query", 
                        "description": "要检索查询的单词，例如love/computer", 
                        "required": true, 
                        "type": "str"
                    }, 
                    {
                        "name": "doctype", 
                        "in": "query", 
                        "description": "返回的数据类型，支持json和xml两种格式，默认情况下json数据", 
                        "required": false, 
                        "type": "str"
                    }
                ]
            }
        }
    }
}
```

把插件关联到应用，LLM会进行智能推理，根据情况按需调用相关插件
![image.png](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/a04f364b1cc74fb98d04c696aa9b79e3~tplv-k3u1fbpfcp-watermark.image?)
![image.png](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/3da76b6fecd840a48660e7f8bbab9644~tplv-k3u1fbpfcp-watermark.image?)

## 工作流
1. 创建工作流
![image.png](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/45a47cb3886449609e79cdeb1d6a2c95~tplv-k3u1fbpfcp-watermark.image?)

2. 工作流编排与调试
![image.png](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/fc982e0886a8446facad10ea55adc5cc~tplv-k3u1fbpfcp-watermark.image?)
![image.png](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/6bddcd4d8ecb4700879bc22db0660e73~tplv-k3u1fbpfcp-watermark.image?)

## 应用发布配置
- 发布配置
![image.png](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/cb1d90103d964cd193365630b4d9dda2~tplv-k3u1fbpfcp-watermark.image?)
- 应用发布
![image.png](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/226215d4a4764436afc99b0b0a6045f7~tplv-k3u1fbpfcp-watermark.image?)

## 应用统计分析与langsmith监控
![image.png](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/342dfecdfbf64bed8a5675afd56eded9~tplv-k3u1fbpfcp-watermark.image?)
![image.png](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/22d4275a1e3a43f4bec6a45777eb5cf1~tplv-k3u1fbpfcp-watermark.image?)


# 创建Agent应用示例
## 集成快递查询工作流Agent
1. 可以通过首页的辅助Agent，让AI自动创建应用
![image.png](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/74b85e7bb94c417fa735b678d32c2ff6~tplv-k3u1fbpfcp-watermark.image?)

2. 等几分钟后，在个人空间-AI应用中看到了自动生成的Agent应用
![iShot_2026-02-20_16.27.04.png](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/4acc4686accc4c42bc7574c2aee42b2e~tplv-k3u1fbpfcp-watermark.image?)

3. Agent编排页，可以集成知识库、插件、工作流等工具，通过智能体推理得到相关信息，这里就集成了创建好的快递查询工作流，让LLM据此回答相关物流信息
![iShot_2026-02-20_17.17.06.png](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/96d4f957173e4b2fb80cfc615312695f~tplv-k3u1fbpfcp-watermark.image?)

## 电商知识库问答Agent
### 1. 使用辅助Agent自动创建Agent应用
![image.png](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/70952bfe726d428c8e574b77c28d1050~tplv-k3u1fbpfcp-watermark.image?)

### 2. 完成应用创建
![image.png](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/bbdfed2d66d14b13875e59b1ef3fb29a~tplv-k3u1fbpfcp-watermark.image?)

### 3. 调试会话
![image.png](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/7571f8898bbe45ad93b298e63aa0a75f~tplv-k3u1fbpfcp-watermark.image?)
![image.png](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/e85977d1b1374a0b95a92bec61684dff~tplv-k3u1fbpfcp-watermark.image?)

