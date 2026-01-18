<script setup lang="ts">
import { useUpdateDraftAppConfig } from '@/hooks/use-app'
import type { DraftAppConfig } from '@/models/app'

// 1.定义自定义组件所需数据
const props = defineProps({
  app_id: { type: String, default: '', required: true },
})
const { handleUpdateDraftAppConfig } = useUpdateDraftAppConfig()

const long_term_memory = defineModel<DraftAppConfig['long_term_memory']>('long_term_memory', {
  required: true,
})

const handleSelect = async (value: unknown) => {
  const newEnable = Boolean(value);

  if (Boolean(value) !== long_term_memory.value.enable) {

    // 【核心变化】：直接给 .value 赋值，会自动触发父组件的更新
    long_term_memory.value.enable = newEnable

    await handleUpdateDraftAppConfig(props.app_id, {
      long_term_memory: { enable: newEnable },
    })
  }
}
</script>

<template>
  <div class="">
    <a-collapse-item key="long_term_memory" class="app-ability-item">
      <template #header>
        <div class="text-gray-700 font-bold">长期记忆</div>
      </template>
      <template #extra>
        <a-dropdown @select="handleSelect">
          <a-button size="mini" class="rounded-lg flex items-center gap-1 px-1" @click.stop>
            {{ long_term_memory?.enable ? '开启' : '关闭' }}
            <icon-down />
          </a-button>
          <template #content>
            <a-doption :value="1" class="text-xs py-1.5 text-gray-700">开启</a-doption>
            <a-doption :value="0" class="text-xs py-1.5 text-red-700">关闭</a-doption>
          </template>
        </a-dropdown>
      </template>
      <div class="text-xs text-gray-500 leading-[22px]">
        总结聊天对话内容，并用于更好的响应用户的信息。
      </div>
    </a-collapse-item>
  </div>
</template>

<style scoped></style>
