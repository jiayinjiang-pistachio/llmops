<script setup lang="ts">
import { computed, type PropType } from 'vue'
import DotFlashing from '@/components/DotFlashing.vue'
import AgentThought from './AgentThought.vue'
import markdownit from 'markdown-it'
import mk from 'markdown-it-katex'
import hljs from 'highlight.js'
import { useAudioPlayer } from '@/hooks/use-audio'

// 1.定义自定义组件所需数据
const props = defineProps({
  app: { type: Object, default: () => ({}), required: true },
  answer: { type: String, default: '', required: true },
  loading: { type: Boolean, default: false, required: false },
  latency: { type: Number, default: 0, required: false },
  total_token_count: { type: Number, default: 0, required: false },
  agent_thoughts: {
    type: Array as PropType<Record<string, any>[]>,
    default: () => [],
    required: true,
  },
  suggested_questions: { type: Array as PropType<string[]>, default: () => [], required: false },
  message_class: { type: String, default: 'bg-gray-100', required: false },
  message_id: { type: String, default: '', required: false },
  enable_text_to_speech: { type: Boolean, default: false, required: false },
})
const emits = defineEmits(['selectSuggestedQuestion'])

const { textToAudioLoading, isPlaying, startAudioStream, stopAudioStream } = useAudioPlayer()

// 1. 先初始化 md，此时 TS 知道它是一个 MarkdownIt 实例
const md = markdownit({
  html: true,
  linkify: true,
  typographer: true,
})

// 2. 覆盖 highlight 配置
md.options.highlight = (str: string, lang: string): string => {
  if (lang && hljs.getLanguage(lang)) {
    try {
      return (
        '<pre><code class="hljs">' +
        hljs.highlight(str, { language: lang, ignoreIllegals: true }).value +
        '</code></pre>'
      )
    } catch (e) {
      console.error(e)
    }
  }

  // 关键：直接调用 md 之前，它已经被声明过了
  return '<pre><code class="hljs">' + md.utils.escapeHtml(str) + '</code></pre>'
}

md.use(mk)

const compileMarkdown = computed(() => {
  const content = props.answer || ''

  return md.render(content)
})
</script>

<template>
  <div class="flex gap-2">
    <!-- 左侧图标 -->
    <a-avatar
      v-if="app.icon"
      :size="30"
      shape="circle"
      class="flex-shrink-0"
      :image-url="app.icon"
    />
    <a-avatar v-else :size="30" shape="circle" class="flex-shrink-0 bg-blue-700">
      <icon-apps />
    </a-avatar>
    <!-- 右侧名称与消息 -->
    <div class="flex flex-col items-start gap-2">
      <!-- 应用名称 -->
      <div class="text-gray-700 font-bold">{{ app.name }}</div>
      <!-- 推理步骤 -->
      <agent-thought :agent_thoughts="agent_thoughts" :loading="loading" />
      <!-- AI消息 -->
      <div
        v-if="loading"
        :class="`${$props.message_class} border border-gray-200 text-gray-700 px-4 py-3 rounded-2xl break-all`"
      >
        <dot-flashing />
      </div>
      <div
        v-else-if="answer.trim() !== ''"
        :class="`${$props.message_class} markdown-body border border-gray-200 text-gray-700 px-4 py-3 rounded-2xl break-all`"
        v-html="compileMarkdown"
      ></div>
      <div
        v-else
        :class="`${$props.message_class} border border-gray-200 text-gray-700 px-4 py-3 rounded-2xl break-all`"
      >
        无LLM生成内容，请重试。
      </div>
      <!-- 消息展示与操作 -->
      <div class="flex items-center justify-between">
        <!-- 消息额外展示 -->
        <a-space class="text-xs">
          <template #split>
            <a-divider direction="vertical" class="m-0" />
          </template>
          <div class="flex items-center gap-1 text-gray-500">
            <icon-check />
            {{ latency.toFixed(2) }}s
          </div>
          <div class="text-gray-500">{{ total_token_count }} Tokens</div>
        </a-space>
        <!-- 播放音频&暂停播放 -->
        <div v-if="enable_text_to_speech" class="flex items-center gap-2 ml-1">
          <template v-if="textToAudioLoading">
            <icon-loading class="group-hover:block text-gray-500" />
          </template>
          <template v-else>
            <icon-pause
              v-if="isPlaying"
              class="group-hover:block text-blue-700 cursor-pointer hover:text-blue-700"
              @click="() => stopAudioStream()"
            />
            <icon-play-circle
              v-else
              class="group-hover:block text-gray-400 cursor-pointer hover:text-gray-700"
              @click="() => startAudioStream(message_id)"
            />
          </template>
        </div>
      </div>
      <!-- 建议问题列表 -->
      <div v-if="suggested_questions.length > 0" class="flex flex-col gap-2">
        <div
          v-for="(suggested_question, idx) in suggested_questions"
          :key="idx"
          class="px-4 py-1.5 border rounded-lg text-gray-700 cursor-pointer hover:bg-gray-50"
          @click="() => emits('selectSuggestedQuestion', suggested_question)"
        >
          {{ suggested_question }}
        </div>
      </div>
    </div>
  </div>
</template>

<style>
.markdown-body pre {
  @apply overflow-auto rounded-2xl min-w-0 !important;
}
</style>
