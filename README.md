
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
![image.png](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/6081d5229df840b4b87b6370c5151789~tplv-k3u1fbpfcp-watermark.image?)
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
![iShot_2026-02-20_16.26.44.png](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/8fa820f1ddfd4fba8ec062a77b90d35f~tplv-k3u1fbpfcp-watermark.image?)

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

