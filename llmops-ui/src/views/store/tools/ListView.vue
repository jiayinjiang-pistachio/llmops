<template>
  <a-spin :loading="loading" class="block h-full w-full">
    <div class="p-6 flex flex-col">
      <!-- 顶层标题+创建按钮 -->
      <div class="flex items-center justify-between mb-6">
        <!-- 左侧标题 -->
        <div class="flex items-center gap-2">
          <a-avatar :size="32" class="bg-blue-700">
            <icon-common :size="18" />
          </a-avatar>
          <div class="text-lg font-medium text-gray-900">插件广场</div>
        </div>
        <!-- 创建按钮 -->
        <a-button type="primary" class="rounded-lg">创建自定义插件</a-button>
      </div>
      <!-- 插件分类+搜索框 -->
      <div class="flex items-center justify-between mb-6">
        <!-- 左侧分类 -->
        <div class="flex items-center gap-2">
          <a-button
            class="rounded-lg !text-gray-700 px-3"
            :type="category === 'all' ? 'secondary' : 'text'"
            @click="category = 'all'"
            >全部</a-button
          >
          <a-button
            v-for="item in categories"
            :key="item.category"
            :type="category === item.category ? 'secondary' : 'text'"
            @click="category = item.category"
            class="rounded-lg !text-gray-700 px-3"
          >
            {{ item.name }}
          </a-button>
        </div>
        <!-- 右侧搜索 -->
        <a-input-search
          v-model="searchWord"
          placeholder="请输出插件名称"
          class="w-[240px] bg-white rounded-lg border-gray-300"
        />
      </div>
      <!-- 底部插件列表 -->
      <a-row :gutter="[20, 20]" class="flex-1">
        <!-- 有数据的UI状态 -->
        <a-col v-for="(provider, idx) in fiilterProviders" :key="provider.name" :span="6">
          <a-card hoverable class="cursor-pointer rounded-lg" @click="showIdx = idx">
            <!-- 顶部提供商名称 -->
            <div class="flex items-center gap-3 mb-3">
              <!-- 左侧图标 -->
              <a-avatar :size="40" shape="square" :style="{ backgroundColor: provider.background }">
                <img
                  :src="`${apiPrefix}/builtin-tools/${provider.name}/icon`"
                  :alt="provider.name"
                />
              </a-avatar>
              <!-- 右侧工具信息 -->
              <div class="flex flex-col">
                <div class="text-base text-gray-900 font-bold">{{ provider.label }}</div>
                <div class="text-xs text-gray-500 line-clamp-1">
                  提供商 {{ provider.name }} · {{ provider.tools.length }} 插件
                </div>
              </div>
            </div>
            <!-- 提供商的描述信息 -->
            <div class="leading-[18px] text-gray-500 h-[72px] line-clamp-4 mb-2">
              {{ provider.description }}
            </div>
            <!-- 提供商的发布信息 -->
            <div class="flex items-center gap-1.5">
              <a-avatar :size="18" class="bg-blue-700">
                <icon-user />
              </a-avatar>
              <div class="text-xs text-gray-400">
                慕课 · 发布时间 {{ moment(provider.created_at).format('MM-DD HH:mm') }}
              </div>
            </div>
          </a-card>
        </a-col>
        <!-- 没数据的UI状态 -->
        <a-col v-if="!fiilterProviders.length" :span="24">
          <a-empty
            description="没有可用的内置插件"
            class="h-[400px] flex flex-col items-center justify-center"
          />
        </a-col>
      </a-row>
      <a-drawer
        :visible="showIdx != -1"
        :width="350"
        :footer="false"
        title="工具详情"
        :drawer-style="{ background: '#f9faf8' }"
        @cancel="showIdx = -1"
      >
        <div v-show="showIdx != -1">
          <!-- 顶部提供商名称 -->
          <div class="flex items-center gap-3 mb-3">
            <!-- 左侧图标 -->
            <a-avatar
              :size="40"
              shape="square"
              :style="{ backgroundColor: currentShowProvider.background }"
            >
              <img
                :src="`${apiPrefix}/builtin-tools/${currentShowProvider.name}/icon`"
                :alt="currentShowProvider.name"
              />
            </a-avatar>
            <!-- 右侧工具信息 -->
            <div class="flex flex-col">
              <div class="text-base text-gray-900 font-bold">{{ currentShowProvider.label }}</div>
              <div class="text-xs text-gray-500 line-clamp-1">
                提供商 {{ currentShowProvider.name }} · {{ currentShowProvider.tools?.length }} 插件
              </div>
            </div>
          </div>
          <!-- 提供商的描述信息 -->
          <div class="leading-[18px] text-gray-500 mb-2">
            {{ currentShowProvider.description }}
          </div>
          <!-- 分隔符 -->
          <hr class="my-4" />
          <!-- 提供者工具 -->
          <div class="flex flex-col">
            <div class="mb-3 text-xs text-gray-500">
              包含 {{ currentShowProvider.tools?.length }} 个工具
            </div>
            <!-- 工具列表 -->
            <a-card
              v-for="tool in currentShowProvider.tools"
              :key="tool.name"
              class="cursor-pointer rounded-xl flex flex-col"
            >
              <!-- 工具名称 -->
              <div class="font-bold text-gray-900 mb-2">{{ tool.label }}</div>
              <!-- 工具描述 -->
              <div class="text-xs text-gray-500">{{ tool.description }}</div>
              <!-- 工具参数 -->
              <div v-if="tool.inputs.length > 0">
                <!-- 分隔符 -->
                <div class="flex items-center gap-2 my-4">
                  <div class="text-xs font-bold text-gray-500">参数</div>
                  <hr class="flex-1" />
                </div>
                <!-- 参数列表 -->
                <div class="flex flex-col gap-4">
                  <div v-for="input in tool.inputs" :key="input.name" class="flex flex-col gap-2">
                    <!-- 上半部分 -->
                    <div class="flex items-center gap-2 text-xs">
                      <div class="text-gray-900 font-bold">{{ input.name }}</div>
                      <div class="text-gray-500">{{ input.type }}</div>
                      <div v-if="input.required" class="text-red-700">必填</div>
                    </div>
                    <!-- 参数描述信息 -->
                    <div class="text-xs text-gray-500">{{ input.description }}</div>
                  </div>
                </div>
              </div>
            </a-card>
          </div>
        </div>
      </a-drawer>
    </div>
  </a-spin>
</template>

<script setup lang="ts">
import { apiPrefix } from '@/config'
import type { BuiltinProviderItem, CategoryItem } from '@/models/builtin-tool'
import { getBuiltinTools, getCategories } from '@/services/builtin-tool'
import moment from 'moment'
import { computed, onMounted, reactive, ref, type ComputedRef } from 'vue'

const categories = reactive<CategoryItem[]>([])
onMounted(async () => {
  const resp = await getCategories()
  Object.assign(categories, resp.data)
})

const providers = reactive<BuiltinProviderItem[]>([])
const loading = ref(false)
onMounted(async () => {
  try {
    const resp = await getBuiltinTools()
    Object.assign(providers, resp.data)
  } finally {
    loading.value = false
  }
})

const category = ref('all')
const searchWord = ref('')
const fiilterProviders: ComputedRef<BuiltinProviderItem[]> = computed(() => {
  return providers.filter((item) => {
    const matchCategory = category.value === 'all' || item.category === category.value
    const matchSearchWord =
      searchWord.value === '' || item.label.toLowerCase().includes(searchWord.value)
    return matchCategory && matchSearchWord
  })
})

const showIdx = ref(-1)
const currentShowProvider = computed(
  () => fiilterProviders.value[showIdx.value] ?? ({} as BuiltinProviderItem),
)
</script>
