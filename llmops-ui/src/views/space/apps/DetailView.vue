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
        <header
          class="flex flex-shrink-0 items-center h-16 px-4 text-xl bg-white border-b border-gray-200 shadow-sm"
        >
          调试与预览
        </header>
        <!-- 调试对话界面 -->
        <div class="h-full min-h-0 px-6 py-7 overflow-x-hidden overflow-y-scroll scrollbar-w-none">
          <!-- 人类消息 -->
          <div class="flex flex-row gap-2 mb-6" v-for="message in messages" :key="message.content">
            <!-- 头像 -->
            <a-avatar
              v-if="message.role === 'user'"
              :size="30"
              class="flex-shrink-0"
              :style="{ backgroundColor: '#3370ff' }"
              >幕</a-avatar
            >
            <a-avatar
              v-else
              :size="30"
              class="flex-shrink-0"
              :style="{ backgroundColor: '#00d0b6' }"
            >
              <icon-apps />
            </a-avatar>
            <!-- 实际消息 -->
            <div class="flex flex-col gap-2">
              <div class="font-semibold text-gray-700">
                {{ message.role === 'user' ? '慕小课' : 'ChatGPT聊天机器人' }}
              </div>
              <div
                v-if="message.role === 'user'"
                class="max-w-max bg-blue-700 text-white border border-blue-800 px-4 py-3 rounded-2xl leading-5"
              >
                {{ message.content }}
              </div>
              <div
                v-else
                class="max-w-max bg-gray-100 text-gray-900 border border-gray-200 px-4 py-3 rounded-2xl leading-5"
              >
                {{ message.content }}
                <div v-if="isLoading" class="cursor"></div>
              </div>
            </div>
          </div>
          <!-- 没有任何数据时显示的内容 -->
          <div
            v-if="!messages.length"
            class="mt-[25%] flex flex-col items-center justify-center gap-2"
          >
            <a-avatar :size="70" shape="square" :style="{ backgroundColor: '#00d0b6' }">
              <icon-apps />
            </a-avatar>
            <div class="text-2xl font-semibold text-gray-900 mt-2">ChatGPT聊天机器人</div>
          </div>
        </div>
        <!-- 调试对话输入框 -->
        <div class="flex flex-col w-full flex-shrink-0">
          <!-- 顶部输入框 -->
          <div class="px-6 flex items-center gap-4">
            <!-- 清除按钮 -->
            <a-button type="text" shape="circle" class="flex-shrink-0" @click="clearMessages">
              <template #icon>
                <icon-empty :size="16" :style="{ color: '#374151' }" />
              </template>
            </a-button>
            <!-- 输入框组件 -->
            <div
              class="h-[50px] flex items-center gap-2 px-4 flex-1 border border-gray-200 rounded-full"
            >
              <input
                v-model="query"
                type="text"
                class="flex-1 outline-0"
                @keyup.enter="send"
                placeholder="请输入您的问题..."
              />
              <a-button type="text" shape="circle">
                <template #icon>
                  <icon-plus-circle :size="16" :style="{ color: '#374151' }" />
                </template>
              </a-button>
              <a-button type="text" shape="circle" @click="send">
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
import { debugApps } from '@/services/app'
import { Message } from '@arco-design/web-vue'
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'

interface MessageItem {
  role: 'user' | 'ai'
  content: string
}

const query = ref('')
const messages = ref<MessageItem[]>([])
const isLoading = ref(false)
const route = useRoute()
const appId = computed(() => route.params.app_id as string)

const clearMessages = () => {
  messages.value = []
}

const send = async () => {
  try {
    if (!query.value.trim()) {
      Message.error('用户提问不能为空')
      return
    }

    if (isLoading.value) {
      Message.warning('上一次回复还未结束，请稍等')
      return
    }
    // 提取用户信息
    const humanQuery = query.value.trim()
    messages.value.push({
      role: 'user',
      content: humanQuery,
    })

    // 清空输入框
    query.value = ''

    isLoading.value = true

    messages.value.push({
      role: 'ai',
      content: '',
    })

    // 发起API请求
    await debugApps(appId.value, humanQuery, (eventResponse) => {
      // 提取流式事件响应数据以及事件名称
      const event = eventResponse?.event
      const data = eventResponse?.data

      // 获取最后一条消息
      const lastIdx = messages.value.length - 1
      const message = messages.value[lastIdx]

      // todo
      console.log("data.answer: ", data.answer)
      if (event === 'agent_message') {
        if (messages.value[lastIdx]) {
          messages.value[lastIdx].content = message?.content + data.answer
        }
      }
    })
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.cursor {
  display: inline-block;
  width: 1px;
  height: 14px;
  background-color: #444444;
  animation: blink 1s step-end infinite;
  vertical-align: middle;
}

@keyframes blink {
  0%,
  100% {
    opacity: 1; /* 显示 */
  }

  50% {
    opacity: 0;
  }
}
</style>
