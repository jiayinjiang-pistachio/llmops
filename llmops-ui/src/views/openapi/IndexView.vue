<script setup lang="ts">
import CodeHighLight from '@/components/CodeHighLight.vue'
import {
  blockApiOutput,
  blockApiShell,
  streamApiOutput,
  streamApiShell,
} from '@/views/openapi/quick-start'
</script>

<template>
  <div class="pb-6">
    <div class="bg-white p-6 rounded-lg h-[calc(100vh-160px)] overflow-scroll scrollbar-w-none">
      <h2 class="text-base text-gray-700 font-bold mb-4">概览</h2>
      <p class="text-gray-700 mb-4">
        <span class="font-bold">ZenSnack LLMOps API</span>
        是面向开发者提供的专业级技术交互平台，致力于通过标准化接口实现更高效、全面的开发诉求。不仅如此，<span
          class="font-bold"
          >ZenSnack LLMOps API</span
        >
        还提供高度灵活且高精度的模型调度、工作流编排、知识库检索及插件扩展能力，赋能开发者构建更加精准、高效且智能的定制化
        Agent。
      </p>
      <h2 class="text-base text-gray-900 font-bold mb-4">准备工作</h2>
      <p class="text-gray-700 mb-4">
        在开始之前，您需 需要创建个人访问令牌，其次需要在 LLMOps 上完成 Agent 的创建与发布。
      </p>
      <h2 class="text-base text-gray-900 font-bold mb-4">基础使用</h2>
      <a-tabs type="text">
        <a-tab-pane key="block" title="非流式Chat">
          <p class="text-gray-700 mb-4">请求CURL</p>
          <code-high-light language="shell">{{ blockApiShell }}</code-high-light>
          <p class="text-gray-700 mb-4">返回结果示例</p>
          <code-high-light language="json">{{ blockApiOutput }}</code-high-light>
        </a-tab-pane>
        <a-tab-pane key="stream" title="流式Chat">
          <p class="text-gray-700 mb-4">请求CURL</p>
          <code-high-light language="shell">{{ streamApiShell }}</code-high-light>
          <p class="text-gray-700 mb-4">返回结果示例</p>
          <code-high-light language="json">{{ streamApiOutput }}</code-high-light>
        </a-tab-pane>
      </a-tabs>
    </div>
  </div>
</template>

<style scoped></style>
