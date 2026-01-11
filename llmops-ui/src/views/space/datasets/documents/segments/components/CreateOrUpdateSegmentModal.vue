<template>
  <a-modal
    :visible="visible"
    :hide-title="true"
    :footer="false"
    :width="520"
    modal-class="rounded-xl"
    @cancel="hideModal"
  >
    <!-- 顶部标题 -->
    <div class="flex items-center justify-between">
      <div class="text-lg font-bold text-gray-700">
        {{ isUpdateOperation ? '更新' : '添加' }}片段
      </div>
      <a-button type="text" class="!text-gray-700" size="small" @click="hideModal">
        <template #icon>
          <icon-close />
        </template>
      </a-button>
    </div>
    <!-- 中间表单 -->
    <div class="pt-6">
      <a-form ref="formRef" :model="form" layout="vertical" @submit="saveSegment">
        <a-form-item
          field="content"
          label="片段内容"
          asterisk-position="end"
          :rules="[{ required: true, message: '片段内容不能为空' }]"
        >
          <a-textarea
            v-model:model-value="form.content"
            placeholder="在这里添加文档片段内容"
            :auto-size="{ minRows: 8, maxRows: 8 }"
          />
        </a-form-item>
        <a-form-item field="keywords" label="关键词">
          <a-input-tag
            v-model="form.keywords"
            :max-tag-count="10"
            placeholder="请输入该文档片段关键词，最多不超过10个，按Enter输入"
           />
        </a-form-item>
        <!-- 底部按钮 -->
        <div class="flex items-center justify-between">
          <div></div>
          <a-space :size="16">
            <a-button class="rounded-lg" @click="hideModal">取消</a-button>
            <a-button :loading="loading" class="rounded-lg" type="primary" html-type="submit"
              >保存</a-button
            >
          </a-space>
        </div>
      </a-form>
    </div>
  </a-modal>
</template>

<script setup lang="ts">
import { createSegment, getSegment, updateSegment } from '@/services/datasets'
import { Message, type Form } from '@arco-design/web-vue'
import type { ValidatedError } from '@arco-design/web-vue/es/form/interface'
import { computed, reactive, ref, watch } from 'vue'

// 定义自定义组件所需数据
const props = defineProps({
  dataset_id: {
    type: String,
    required: false,
  },
  document_id: {
    type: String,
    required: false,
  },
  segment_id: {
    type: String,
    required: false,
  },
  visible: {
    type: Boolean,
    required: true,
  },
  callback: {
    type: Function,
    required: false,
  },
})

const emits = defineEmits(['update:visible'])
const loading = ref(false)
const defaultForm: { content: string; keywords: string[] } = {
  content: '',
  keywords: [],
}
const form = reactive({ ...defaultForm })
const formRef = ref<InstanceType<typeof Form>>()
const isUpdateOperation = computed(() => props.segment_id && props.segment_id !== '')

// 定义隐藏模态窗函数
const hideModal = () => emits('update:visible', false)

// 定义表单提交函数
const saveSegment = async ({ errors }: { errors: Record<string, ValidatedError> | undefined }) => {
  if (errors) {
    return
  }

  try {
    loading.value = true
    // 检测是保存还是新增，调用不同的API接口
    if (isUpdateOperation.value) {
      // 更新文档片段信息
      const resp = await updateSegment(
        props.dataset_id as string,
        props.document_id as string,
        props.segment_id as string,
        form,
      )
      Message.success(resp.message)
    } else {
      // 新增文档片段信息
      const resp = await createSegment(props.dataset_id as string, props.document_id as string, form)
      Message.success(resp.message)
    }

    // 完成保存操作，隐藏模态窗并调用回调函数
    emits('update:visible', false)
    props.callback?.()
  } finally {
    loading.value = false
  }
}

// 监听模态窗显示状态变化
watch(
  () => props.visible,
  async (newValue) => {
    // 清除表单校验信息
    formRef.value?.resetFields()

    if (newValue) {
      // 开启弹窗，需要检测下是更新还是创建操作
      if (isUpdateOperation.value) {
        // 调用接口获取文档片段详情
        const resp = await getSegment(
          props.dataset_id as string,
          props.document_id as string,
          props.segment_id as string,
        )
        const data = resp.data

        // 更新表单数据
        form.content = data.content
        form.keywords = data.keywords
      }
    } else {
      // 关闭弹窗，需要清空表单数据
      formRef.value?.resetFields()
      Object.assign(form, { ...defaultForm })
    }
  },
)
</script>
