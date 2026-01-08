<template>
  <a-spin
    :loading="loading"
    class="block h-full w-full overflow-scroll scrollbar-w-none"
    @scroll.passive="handleScroll"
  >
    <!-- 底部插件列表 -->
    <a-row :gutter="[20, 20]" class="flex-1">
      <!-- 有数据的UI状态 -->
      <a-col v-for="(provider, idx) in providers" :key="provider.name" :span="6">
        <a-card hoverable class="cursor-pointer rounded-lg" @click="showIdx = idx">
          <!-- 顶部提供商名称 -->
          <div class="flex items-center gap-3 mb-3">
            <!-- 左侧图标 -->
            <a-avatar :size="40" shape="square" :image-url="provider.icon"> </a-avatar>
            <!-- 右侧工具信息 -->
            <div class="flex flex-col">
              <div class="text-base text-gray-900 font-bold">{{ provider.name }}</div>
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
              慕小课 · 编辑时间 {{ moment(provider.created_at).format('MM-DD HH:mm') }}
            </div>
          </div>
        </a-card>
      </a-col>
      <!-- 没数据的UI状态 -->
      <a-col v-if="!providers.length" :span="24">
        <a-empty
          description="没有可用的API插件"
          class="h-[400px] flex flex-col items-center justify-center"
        />
      </a-col>
    </a-row>
    <!-- 加载器 -->
    <a-row v-if="providers.length > 0">
      <!-- 加载数据中 -->
      <a-col v-if="paginator.current_page < paginator.total_page" :span="24" align="center">
        <a-space class="my-4">
          <a-spin />
          <div class="text-gray-400">加载中</div>
        </a-space>
      </a-col>
      <!-- 加载数据完成 -->
      <a-col v-else-if="paginator.total_page > 1" :span="24" align="center">
        <div class="text-gray-400 my-4">数据已加载完成</div>
      </a-col>
    </a-row>
    <!-- 卡片抽屉 -->
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
          <a-avatar :size="40" shape="square" :image-url="currentShowProvider.icon"> </a-avatar>
          <!-- 右侧工具信息 -->
          <div class="flex flex-col">
            <div class="text-base text-gray-900 font-bold">{{ currentShowProvider.name }}</div>
            <div class="text-xs text-gray-500 line-clamp-1">
              提供商 {{ currentShowProvider.name }} · {{ currentShowProvider.tools?.length }} 插件
            </div>
          </div>
        </div>
        <!-- 提供商的描述信息 -->
        <div class="leading-[18px] text-gray-500 mb-2">
          {{ currentShowProvider.description }}
        </div>
        <!-- 编辑按钮 -->
        <a-button
          class="rounded-lg mb-2"
          long
          :loading="showUpdateModalMoading"
          @click="handleUpdate"
        >
          <template #icon>
            <icon-settings />
          </template>
          编辑工具
        </a-button>
        <!-- 分隔符 -->
        <hr class="my-4" />
        <!-- 提供者工具 -->
        <div class="flex flex-col gap-2">
          <div class="text-xs text-gray-500">
            包含 {{ currentShowProvider.tools?.length }} 个工具
          </div>
          <!-- 工具列表 -->
          <a-card
            v-for="tool in currentShowProvider.tools"
            :key="tool.name"
            class="cursor-pointer rounded-xl flex flex-col"
          >
            <!-- 工具名称 -->
            <div class="font-bold text-gray-900 mb-2">{{ tool.name }}</div>
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
                    <div class="text-gray-500">{{ typeMap[input.type] }}</div>
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
    <!-- 新建/修改模态窗 -->
    <a-modal
      :visible="createType === 'tool' || showUpdateModal"
      :hide-title="true"
      :footer="false"
      :width="630"
      modal-class="rounded-lg"
      @cancel="handleCancel"
    >
      <!-- 顶部标题 -->
      <div class="flex items-center justify-between">
        <div class="text-lg font-bold text-gray-700">{{ modalTitle }}</div>
        <a-button type="text" class="!text-gray-700" size="small" @click="handleCancel">
          <template #icon>
            <icon-close />
          </template>
        </a-button>
      </div>
      <!-- 中间表单 -->
      <div class="pt-6">
        <a-form ref="formRef" :model="form" layout="vertical" @submit="handleSubmit">
          <a-form-item
            field="icon"
            hide-label
            :rules="[{ required: true, message: '插件图标不能为空' }]"
          >
            <a-upload
              v-model="form.icon"
              :limit="1"
              list-type="picture-card"
              accept="image/png, image/jpeg"
              class="!w-auto mx-auto"
            />
          </a-form-item>
          <a-form-item
            field="name"
            label="插件名称"
            asterisk-position="end"
            :rules="[{ required: true, message: '插件名称不能为空' }]"
          >
            <a-input
              v-model="form.name"
              placeholder="请输入插件名称，确保名称含义清晰"
              show-word-limit
              :max-length="60"
            />
          </a-form-item>
          <a-form-item
            field="openapi_schema"
            label="OpenAPI Schema"
            asterisk-position="end"
            :rules="[{ required: true, message: 'OpenAPI Schema 不能为空' }]"
          >
            <a-textarea
              v-model="form.openapi_schema"
              :auto-size="{ minRows: 4, maxRows: 6 }"
              placeholder="在此处输入您的 OpenAPI Schema"
              @blur="handleValidateOpenapiSchema"
            />
          </a-form-item>
          <a-form-item label="可用工具">
            <!-- 可用工具表格 -->
            <div class="rounded-lg border border-gray-200 w-full overflow-x-auto">
              <table class="w-full leading-[18px] text-xs text-gray-700 font-normal">
                <thead class="text-gray-500">
                  <tr class="border-b border-gray-200">
                    <th class="p-2 pl-3 font-medium">名称</th>
                    <th class="p-2 pl-3 font-medium w-[236px]">描述</th>
                    <th class="p-2 pl-3 font-medium">方法</th>
                    <th class="p-2 pl-3 font-medium">路径</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(tool, idx) in tools"
                    :key="idx"
                    class="border-b last:border-0 border-gray-200 text-gray-700"
                  >
                    <td class="p-2 pl-3">{{ tool.name }}</td>
                    <td class="p-2 pl-3 w-[236px]">{{ tool.description }}</td>
                    <td class="p-2 pl-3">{{ tool.method }}</td>
                    <td class="p-2 pl-3 w-[62px]">{{ tool.path }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </a-form-item>
          <a-form-item label="Headers">
            <!-- 请求头表单 -->
            <div class="rounded-lg border border-gray-200 w-full overflow-x-auto">
              <table class="w-full leading-[18px] text-xs text-gray-200 font-normal mb-3">
                <thead class="text-gray-500">
                  <tr class="border-b border-gray-200">
                    <th class="p-2 pl-3 font-medium">Key</th>
                    <th class="p-2 pl-3 font-medium">value</th>
                    <th class="p-2 pl-3 font-medium w-[50px]">操作</th>
                  </tr>
                </thead>
                <tbody v-if="form.headers.length > 0" class="border-b border-gray-200">
                  <tr
                    v-for="(header, idx) in form.headers"
                    :key="idx"
                    class="bordre-b last:border-0 border-gray-200"
                  >
                    <td class="p-2 pl-3">
                      <a-form-item :field="`headers[${idx}].key`" hide-label class="m-0">
                        <a-input v-model="header.key" placeholder="请输入请求头键名" />
                      </a-form-item>
                    </td>
                    <td class="p-2 pl-3">
                      <a-form-item :field="`headers[${idx}].value`" hide-label class="m-0">
                        <a-input v-model="header.value" placeholder="请输入请求头键值内容" />
                      </a-form-item>
                    </td>
                    <td class="p-2 pl-3">
                      <a-button
                        size="mini"
                        type="text"
                        class="!text-gray-700"
                        @click="form.headers.splice(idx, 1)"
                      >
                        <template #icon>
                          <icon-delete />
                        </template>
                      </a-button>
                    </td>
                  </tr>
                </tbody>
              </table>
              <a-button
                size="mini"
                class="rounded ml-3 mb-3 !text-gray-700"
                @click="form.headers.push({ key: '', value: '' })"
              >
                <template #icon>
                  <icon-plus />
                </template>
                增加参数
              </a-button>
            </div>
          </a-form-item>
          <!-- 底部按钮 -->
          <div class="flex items-center justify-between">
            <div>
              <a-button
                v-if="showUpdateModal"
                class="rounded-lg !text-red-700"
                @click="handleDelete"
                >删除</a-button
              >
            </div>
            <a-space :size="16">
              <a-button class="rounded-lg" @click="handleCancel">取消</a-button>
              <a-button
                :loading="submitLoading"
                class="rounded-lg"
                type="primary"
                html-type="submit"
                >保存</a-button
              >
            </a-space>
          </div>
        </a-form>
      </div>
    </a-modal>
  </a-spin>
</template>

<style lang="less"></style>

<script setup lang="ts">
import { typeMap } from '@/config'
import type { ApiToolProviderItem } from '@/models/api-tool'
import {
  createApiProvider,
  deleteApiToolProvider,
  getApiToolProvider,
  getApiToolProvidersWithPage,
  updateAPiToolProvider,
  validateOpenAPISchema,
} from '@/services/api-tool'
import moment from 'moment'
import { onMounted, reactive, ref, computed, watch, useTemplateRef } from 'vue'
import { useRoute } from 'vue-router'
import { Message, Modal, type FormInstance } from '@arco-design/web-vue'

const props = defineProps<{
  createType: string
}>()
const emit = defineEmits<{
  (e: 'update-create-type', value: string): void
}>()
const showUpdateModal = ref(false)
const showUpdateModalMoading = ref(false)
const submitLoading = ref(false)
const providerId = computed(() => providers[showIdx.value]?.id)
const modalTitle = computed(() => (props.createType === 'tool' ? '新建插件' : '编辑插件'))

const handleCancel = () => {
  // 1. 重置整个表单的数据
  formRef.value?.resetFields()

  // 隐藏表单模态窗
  emit('update-create-type', '')
  showUpdateModal.value = false
}

const handleUpdate = async () => {
  try {
    showUpdateModalMoading.value = true
    // 根据拿到的provider_id去获取对应的提供商信息
    if (providerId.value == undefined) {
      return
    }

    const resp = await getApiToolProvider(providerId.value)
    const data = resp.data

    // 更新form表单数据
    formRef.value?.resetFields?.()
    form.icon = data.icon
    form.name = data.name
    form.openapi_schema = data.openapi_schema
    form.headers = data.headers
  } catch (error) {
    console.log(error)
  } finally {
    showUpdateModalMoading.value = false
    showUpdateModal.value = true
  }
}

const providers = reactive<ApiToolProviderItem[]>([])
const paginator = reactive({
  current_page: 1,
  page_size: 10,
  total_page: 0,
  total_record: 0,
})
const loading = ref(false)
const route = useRoute()

const initData = async () => {
  // 重置分页器
  paginator.current_page = 1
  paginator.total_page = 0
  paginator.total_record = 0
  // 加载数据
  await loadMoreData(true)
}

watch(
  () => route.query.search,
  async () => {
    await initData()
  },
)
const loadMoreData = async (init = false) => {
  // 检测是否需要加载新数据
  if (!init && (loading.value || paginator.current_page >= paginator.total_page)) {
    return
  }
  // 加载更多数据并更新状态
  try {
    loading.value = true

    // 如果不是初始化，则请求下一页
    const targetPage = init ? 1 : paginator.current_page + 1

    const resp = await getApiToolProvidersWithPage(
      targetPage,
      paginator.page_size,
      (route.query.search as string) || '',
    )
    const data = resp.data

    // 更新分页器
    paginator.current_page = data.paginator.current_page
    paginator.total_page = data.paginator.total_page
    paginator.total_record = data.paginator.total_record

    // 追加或是覆盖
    if (init) {
      providers.splice(0, providers.length, ...data.list)
    } else {
      providers.push(...data.list)
    }
  } finally {
    loading.value = false
  }
}

const handleScroll = async (event: Event) => {
  const target = event.target as HTMLElement
  if (target.scrollHeight - target.scrollTop - target.clientHeight < 10) {
    if (loading.value) {
      return
    }
    await loadMoreData()
  }
}

onMounted(async () => {
  await initData()
})

const showIdx = ref(-1)
const currentShowProvider = computed(() => providers[showIdx.value] ?? ({} as ApiToolProviderItem))

const form = reactive({
  icon: 'https://picsum.photos/400',
  name: '',
  openapi_schema: '',
  headers: [] as Array<{ key: string; value: any }>,
})
const tools = computed(() => {
  try {
    const avaliableTools = []
    // 解析openapi_schema
    const oepnapi_schema = JSON.parse(form.openapi_schema)

    // 检测是否存在path路径
    if ('paths' in oepnapi_schema) {
      // 循环所有path并提取工具
      for (const path in oepnapi_schema.paths) {
        // 遍历path下的get/post方法
        const methods = oepnapi_schema.paths[path]
        for (const method in methods) {
          if (['get', 'post'].includes(method)) {
            // 提供工具信息，并校验是否存在name、description字段
            const tool = methods[method]
            if ('operationId' in tool && 'description' in tool) {
              avaliableTools.push({
                name: tool.operationId as string,
                description: tool.description as string,
                method: method as string,
                path: path as string,
              })
            }
          }
        }
      }
    }

    return avaliableTools
  } catch (error) {
    console.log('解析openapi_schema出错', error)
    return []
  }
})
const handleValidateOpenapiSchema = async () => {
  if (form.openapi_schema.trim() !== '') {
    // 调用验证open_api接口
    await validateOpenAPISchema(form.openapi_schema)
  }
}

const formRef = useTemplateRef<FormInstance>('formRef')

const handleSubmit = async ({ values, errors }: { values: any; errors: any }) => {
  if (errors) {
    return
  }

  try {
    submitLoading.value = true
    if (props.createType === 'tool') {
      const resp = await createApiProvider(values)
      Message.success(resp.message)
    } else if (showUpdateModal.value) {
      if (providerId.value == undefined) {
        Message.error('api工具提供商id不存在')
        return
      }
      const resp = await updateAPiToolProvider(providerId.value, values)
      Message.success(resp.message)
    }

    // 执行后续操作，隐藏模态窗、隐藏抽屉
    handleCancel()
    showIdx.value = -1

    // 重新加载数据
    await initData()
  } catch (error) {
    console.log(error)
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = () => {
  Modal.warning({
    title: '删除这个工具？',
    content: '删除操作不可逆，AI应用将无法再访问您的工具',
    hideCancel: false,
    onOk: async () => {
      try {
        if (providerId.value == undefined) {
          Message.error('该工具的提供商id不存在')
          return
        }

        const resp = await deleteApiToolProvider(providerId.value)
        Message.success(resp.message)
      } catch (error) {
        console.log(error)
      } finally {
        handleCancel()
        showIdx.value = -1

        // 重新加载数据
        await initData()
      }
    },
  })
}
</script>
