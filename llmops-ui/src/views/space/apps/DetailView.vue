<template>
  <div class="flex-1 w-full min-h-0 bg-white">
    <div class="flex-1 grid grid-cols-[26fr_14fr] h-full w-full">
      <!-- 左侧应用编排 -->
      <div class="bg-gray-50 flex flex-col h-full">
        <!-- 顶部标题 -->
        <div class="flex items-center h-16 border-b p-4">
          <div class="text-lg text-gray-700">应用编排</div>
          <!-- LLM模型配置 -->
          <ModelConfig
            :dialog-round="draftAppConfigForm.dialog_round"
            v-model:model_config="draftAppConfigForm.model_config"
            :app_id="String(route.params.app_id)"
          />
        </div>
        <!-- 底部编排区域 -->
        <div class="grid grid-cols-[13fr_13fr] overflow-hidden h-[calc(100vh-141px)]">
          <!-- 左侧人设与回复逻辑 -->
          <div class="border-r py-4">
            <PresetPromptTextarea
              v-model:preset_prompt="draftAppConfigForm.preset_prompt"
              :app_id="appId"
            />
          </div>
          <!-- 右侧应用能力 -->
          <AgentAppAbility v-model:draft_app_config="draftAppConfigForm"  :app_id="appId" />

        </div>
      </div>
      <!-- 右侧调试会话 -->
      <div class="min-w-[404px]">
        <!-- 头部信息 -->
        <PreviewDebugHeader
          :app_id="appId"
          :long_term_memory="draftAppConfigForm.long_term_memory"
        />
        <!-- 对话窗口 -->
        <PreviewDebugChat
          :suggested_after_answer="draftAppConfigForm.suggested_after_answer"
          :opening_questions="draftAppConfigForm.opening_questions"
          :opening_statement="draftAppConfigForm.opening_statement"
          :app="app"
          :app_id="appId"
         />
      </div>
    </div>
  </div>
</template>

<style lang="less"></style>

<script setup lang="ts">
import { useGetDraftAppConfig } from '@/hooks/use-app'
import type { AppDetail } from '@/models/app'
import { computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import PresetPromptTextarea from './components/PresetPromptTextarea.vue'
import AgentAppAbility from './components/AgentAppAbility.vue'
import PreviewDebugHeader from './components/PreviewDebugHeader.vue'
import PreviewDebugChat from './components/PreviewDebugChat.vue'
import { useAppStore } from '@/stores/app'
import { storeToRefs } from 'pinia'
import ModelConfig from './components/ModelConfig.vue'

defineProps<{
  app: AppDetail
}>()

const route = useRoute()
const appId = computed(() => String(route.params.app_id))

const { draftAppConfigForm, loadDraftAppConfig } = useGetDraftAppConfig(appId.value)

const appStore = useAppStore()
const {setGetDraftAppConfigFlag} = appStore
const { getDraftAppConfigFlag } = storeToRefs(appStore)
watch(
  () => getDraftAppConfigFlag.value,
  async (newValue) => {
    if(newValue) {
      await loadDraftAppConfig(appId.value)
      setGetDraftAppConfigFlag(false)
    }
  }
)

</script>
