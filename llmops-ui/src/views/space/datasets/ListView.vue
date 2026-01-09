<template>
  <a-spin
    :loading="loading"
    class="block h-full w-full overflow-scroll scrollbar-w-none"
    @scroll.passive="handleScroll"
  >
    <!-- 底部知识库列表 -->
    <a-row :gutter="[20, 20]" class="flex-1">
      <!-- 有数据的UI状态 -->
      <a-col v-for="dataset in datasets" :key="dataset.id" :span="6">
        <a-card hoverable class="cursor-pointer rounded-lg">
          <!-- 顶部知识库名称 -->
          <div class="flex items-center gap-3 mb-3">
            <!-- 左侧图标 -->
            <a-avatar :size="40" shape="square" :image-url="dataset.icon"> </a-avatar>
            <!-- 右侧知识库信息 -->
            <div class="flex flex-1 justify-between">
              <div class="flex flex-col">
                <router-link
                  :to="{
                    name: 'space-datasets-documents-list',
                    params: { dataset_id: dataset.id },
                  }"
                  class="text-base text-gray-900 font-bold"
                  >{{ dataset.name }}</router-link
                >
                <div class="text-xs text-gray-500 line-clamp-1">
                  {{ dataset.document_count }} 文档 ·
                  {{ Math.round(dataset.character_count / 1000) }} 千字符 ·
                  {{ dataset.related_app_count }} 关联应用
                </div>
              </div>
              <!-- 操作按钮 -->
              <a-dropdown position="br">
                <a-button type="text" size="small" class="rounded-lg !text-gray-700">
                  <template #icon>
                    <icon-more />
                  </template>
                </a-button>
                <template #content>
                  <a-doption @click="goUpdate(dataset.id)">设置</a-doption>
                  <a-doption class="!text-red-500" @click="goDelete(dataset.id)">删除</a-doption>
                </template>
              </a-dropdown>
            </div>
          </div>
          <!-- 知识库的描述信息 -->
          <div class="leading-[18px] text-gray-500 h-[72px] line-clamp-4 mb-2">
            {{ dataset.description }}
          </div>
          <!-- 知识库的归属者信息 -->
          <div class="flex items-center gap-1.5">
            <a-avatar :size="18" class="bg-blue-700">
              <icon-user />
            </a-avatar>
            <div class="text-xs text-gray-400">
              慕小课 · 最近编辑 {{ moment(dataset.created_at).format('MM-DD HH:mm') }}
            </div>
          </div>
        </a-card>
      </a-col>
      <!-- 没数据的UI状态 -->
      <a-col v-if="!datasets.length" :span="24">
        <a-empty
          description="没有可用的知识库"
          class="h-[400px] flex flex-col items-center justify-center"
        />
      </a-col>
    </a-row>
    <!-- 加载器 -->
    <a-row v-if="datasets.length > 0">
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
    <!-- 新建/修改模态窗 -->
    <a-modal
      :visible="createType === 'dataset' || showUpdateModal"
      :hide-title="true"
      :footer="false"
      :width="520"
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
            :rules="[{ required: true, message: '知识库图标不能为空' }]"
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
            label="知识库名称"
            asterisk-position="end"
            :rules="[{ required: true, message: '知识库名称不能为空' }]"
          >
            <a-input
              v-model="form.name"
              placeholder="请输入知识库名称"
              show-word-limit
              :max-length="60"
            />
          </a-form-item>
          <a-form-item field="description" label="知识库描述" asterisk-position="end">
            <a-textarea
              v-model="form.description"
              :auto-size="{ minRows: 4, maxRows: 6 }"
              placeholder="请输入知识库描述"
            />
          </a-form-item>
          <!-- 底部按钮 -->
          <div class="flex items-center justify-between">
            <div></div>
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
import {
  useCreateOrUpdateDataset,
  useDeleteDataset,
  useGeDatasetsWithPage,
} from '@/hooks/use-dataset'
import { getDataset } from '@/services/datasets'
import type { ValidatedError } from '@arco-design/web-vue/es/form/interface'
import moment from 'moment'
import { computed } from 'vue'

const props = defineProps<{
  createType: string
}>()
const emit = defineEmits<{
  (e: 'update-create-type', value: string): void
}>()

const modalTitle = computed(() => (props.createType === 'dataset' ? '新建知识库' : '更新知识库'))

const { loading, datasets, loadMoreData, initData, paginator } = useGeDatasetsWithPage()
const { handleDelete } = useDeleteDataset()
const {
  loading: submitLoading,
  form,
  formRef,
  showUpdateModal,
  updateShowUpdateModal,
  saveDataset,
} = useCreateOrUpdateDataset()

const handleScroll = async (event: Event) => {
  const target = event.target as HTMLElement
  if (target.scrollHeight - target.scrollTop - target.clientHeight < 10) {
    if (loading.value) {
      return
    }
    await loadMoreData()
  }
}

// 删除知识库
const goDelete = (dataset_id: string) => {
  handleDelete(dataset_id, async () => {
    // handleCancel()
    // 重新加载数据
    await initData()
  })
}

let updateDatasetID = ''
// 编辑知识库
const goUpdate = (dataset_id: string) => {
  updateShowUpdateModal(true, async () => {
    // 获取知识库详情
    try {
      const resp = await getDataset(dataset_id)
      const data = resp.data
      updateDatasetID = data.id

      // 更新表单数据
      formRef.value?.resetFields()
      form.name = data.name
      form.icon = data.icon
      form.description = data.description
    } catch (error) {
      console.log(error)
    }
  })
}

// 取消显示模态窗
const handleCancel = () => {
  updateShowUpdateModal(false, () => {
    updateDatasetID = ''

    formRef.value?.resetFields()

    // 隐藏表单模态窗
    emit('update-create-type', '')
  })
}

// 提交模态窗
const handleSubmit = async ({ errors }: { errors: Record<string, ValidatedError> | undefined }) => {
  if (errors) {
    return
  }

  // 调用保存知识库服务
  await saveDataset(updateDatasetID)

  // 关闭模态窗并刷新数据
  handleCancel()
  await initData()
}
</script>
