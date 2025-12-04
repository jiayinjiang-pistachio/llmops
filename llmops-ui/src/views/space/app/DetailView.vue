<template>
  <!-- 最外层容器，高度撑满整个浏览器屏幕 -->
  <div class="min-h-screen">
    <!-- 顶部导航栏 -->
    <header class="h-[74px] bg-gray-100 border-b border-gray-200 px-4 flex items-center">
      顶部导航栏
    </header>
    <!-- 底部内容区 -->
    <div class="flex flex-row h-[calc(100vh-74px)]">
      <!-- 左侧的编排 -->
      <div class="w-2/3 bg-gray-50 h-full">
        <header class="flex items-center h-16 border-b border-gray-200 px-7 text-xl text-gray-700">
          应用编排
        </header>
        <div class="flex flex-row h-[calc(100%-64px)]">
          <div class="flex-1 border-r border-gray-200 p-6">人设与回复逻辑</div>
          <div class="flex-1 p-6">应用能力</div>
        </div>
      </div>
      <!-- 右侧的调试与预览 -->
      <div class="flex flex-col w-1/3 bg-white h-full">
        <header class="flex flex-shrink-0 items-center h-16 px-4 text-xl bg-white border-b border-gray-200 shadow-sm">
          调试与预览
        </header>
        <!-- 调试对话界面 -->
        <div class="h-full min-h-0 px-6 py-7 overflow-x-hidden overflow-y-scroll scrollbar-w-none">
          <!-- 人类消息 -->
          <div class="flex flex-row gap-2 mb-6">
            <!-- 头像 -->
            <a-avatar :size="30" class="flex-shrink-0" :style="{ backgroundColor: '#3370ff' }">幕</a-avatar>
            <!-- 实际消息 -->
            <div class="flex flex-col gap-2">
              <div class="font-semibold text-gray-700">慕小课</div>
              <div class="max-w-max bg-blue-700 text-white border border-blue-800 px-4 py-3 rounded-2xl leading-5">
                能详细讲解下LLM是什么吗？
              </div>
            </div>
          </div>
          <!-- AI消息 -->
          <div class="flex flex-row gap-2 mb-6">
            <!-- 头像 -->
            <a-avatar :size="30" class="flex-shrink-0" :style="{ backgroundColor: '#00d0b6' }">
              <icon-apps />
            </a-avatar>
            <!-- 实际消息 -->
            <div class="flex flex-col gap-2">
              <div class="font-semibold text-gray-700">ChatGPT聊天机器人</div>
              <div class="max-w-max bg-gray-100 text-gray-900 border border-gray-200 px-4 py-3 rounded-2xl leading-5">
                LLM 即 Large Language
                Model，大语言模型，是一种基于深度学习的自然语言处理模型，具有很高的语言理解和生成能力，能够处理各式各样的自然语言任务，例如文本生成、问答、翻译、摘要等。它通过在大量的文本数据上进行训练，学习到语言的模式、结构和语义知识。
              </div>
            </div>
          </div>
          <!-- AI加载状态 -->
          <div class="flex flex-row gap-2 mb-6">
            <!-- 头像 -->
            <a-avatar :size="30" class="flex-shrink-0" :style="{ backgroundColor: '#00d0b6' }">
              <icon-apps />
            </a-avatar>
            <!-- 实际消息 -->
            <div class="flex flex-col gap-2">
              <div class="font-semibold text-gray-700">ChatGPT聊天机器人</div>
              <div class="max-w-max bg-gray-100 text-gray-900 border border-gray-200 px-4 py-3 rounded-2xl leading-5">
                <icon-loading />
              </div>
            </div>
          </div>
        </div>
        <!-- 调试对话输入框 -->
        <div class="flex flex-col w-full flex-shrink-0">
          <!-- 顶部输入框 -->
          <div class="px-6 flex items-center gap-4">
            <!-- 清除按钮 -->
            <a-button type="text" shape="circle" class="flex-shrink-0">
              <template #icon>
                <icon-empty :size="16" :style="{ color: '#374151' }" />
              </template>
            </a-button>
            <!-- 输入框组件 -->
            <div class="h-[50px] flex items-center gap-2 px-4 flex-1 border border-gray-200 rounded-full">
              <input type="text" class="flex-1 outline-0">
              <a-button type="text" shape="circle">
                <template #icon>
                  <icon-plus-circle :size="16" :style="{ color: '#374151' }" />
                </template>
              </a-button>
              <a-button type="text" shape="circle">
                <template #icon>
                  <icon-send :size="16" :style="{ color: '#1d4ed8' }" />
                </template>
              </a-button>
            </div>
          </div>
          <!-- 底部提示文案 -->
          <div class="text-center text-gray-500 text-xs py-4">
            内容由AI生成，无法确保真实准确，仅供参考。
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="less"></style>

<script setup lang="ts">

</script>
