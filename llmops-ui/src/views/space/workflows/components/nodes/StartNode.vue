<template>
  <div
    class="flex flex-col gap-3 rounded-3xl p-3 bg-white border-[2px] border-transparent shadow-sm hover:shadow-md transition-all selected-border w-[240px]"
  >
    <!-- 顶部的节点标题 -->
    <div class="flex items-center gap-2">
      <a-avatar shape="square" :size="24" class="bg-blue-700 rounded-lg flex-shrink-0">
        <icon-home :size="16" />
      </a-avatar>
      <div class="text-gray-700 font-semibold">
        {{ data?.title }}
      </div>
    </div>
    <!-- 底部输入变量列表 -->
    <div class="flex flex-col items-start bg-gray-100 rounded-lg p-3">
      <!-- 标题 -->
      <div class="flex items-center gap-2 mb-2 text-gray-700">
        <icon-caret-down />
        <div class="text-xs font-semibold">输入数据</div>
      </div>
      <!-- 变量列表 -->
      <div class="flex flex-col gap-2">
        <div
          v-for="input in data?.inputs"
          :key="input.name"
          class="flex items-center gap-2 text-xs"
        >
          <div class="flex items-center gap-1 max-w-[180px]">
            <div class="text-gray-700 line-clamp-1 break-all">{{ input.name }}</div>
            <div v-if="input.required" class="flex-shrink-0 text-red-700">*</div>
          </div>
          <div class="text-gray-500 bg-gray-200 px-1 py-0.5 rounded">{{ input.type }}</div>
        </div>
      </div>
    </div>
    <!-- 边起点句柄位置在右侧 -->
    <Handle
      type="source"
      :position="Position.Right"
      class="!w-4 !h-4 !bg-blue-700 !text-white flex items-center justify-center"
    >
      <icon-plus :size="12" class="pointer-events-none" />
    </Handle>
  </div>
</template>

<style scoped>
.selected {
  .selected-border {
    @apply border-blue-700;
  }
}
</style>

<script setup lang="ts">
import { type NodeProps, Handle, Position } from '@vue-flow/core'
import {} from 'vue'

// 定义自定义组件所需数据
defineProps<NodeProps>()
</script>
