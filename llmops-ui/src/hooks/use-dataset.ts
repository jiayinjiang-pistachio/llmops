import type { Paginator } from '@/models/base'
import type { DatasetItem } from '@/models/dataset'
import type { FormInstance } from '@arco-design/web-vue'
import {
  createDataset,
  deleteDataset,
  getDatasetsWithPage,
  updateDataset,
} from '@/services/datasets'
import { Message, Modal } from '@arco-design/web-vue'
import { onMounted, reactive, ref, useTemplateRef, watch } from 'vue'
import { useRoute } from 'vue-router'

export function useGeDatasetsWithPage() {
  const defaultPaginator: Paginator = {
    current_page: 1,
    page_size: 20,
    total_page: 0,
    total_record: 0,
  }
  const paginator = reactive({ ...defaultPaginator })

  const datasets = reactive<DatasetItem[]>([])
  const loading = ref(false)
  const route = useRoute()

  watch(
    () => route.query.search,
    async () => {
      await initData()
    },
  )

  // 加载更多数据
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

      const resp = await getDatasetsWithPage(
        targetPage,
        paginator.page_size,
        (route.query.search as string) || '',
      )
      const data = resp.data

      // 更新分页器
      const { current_page, page_size, total_page, total_record } = data.paginator
      updatePaginator({
        current_page,
        page_size,
        total_page,
        total_record,
      })

      // 追加或是覆盖
      if (init) {
        datasets.splice(0, datasets.length, ...data.list)
      } else {
        datasets.push(...data.list)
      }
    } finally {
      loading.value = false
    }
  }

  onMounted(async () => {
    await initData()
  })

  async function initData() {
    // 初始化分页数据
    updatePaginator({ ...defaultPaginator })

    // 调用数据加载完成初始化
    loadMoreData(true)
  }

  // 更新分页器
  const updatePaginator = (data: Paginator) => {
    paginator.current_page = data.current_page
    paginator.page_size = data.page_size
    paginator.total_page = data.total_page
    paginator.total_record = data.total_record
  }

  return {
    loading,
    datasets,
    paginator,
    loadMoreData,
    initData,
  }
}

export function useDeleteDataset() {
  const handleDelete = (dataset_id: string, callback?: () => void) => {
    Modal.warning({
      title: '要删除知识库吗？',
      content:
        '删除知识库后，关联该知识库的应用将无法再使用该知识库，所有的提示配置和文档都将被永久删除',
      hideCancel: false,
      onOk: async () => {
        try {
          if (dataset_id == undefined) {
            Message.error('该知识库id不存在')
            return
          }

          const resp = await deleteDataset(dataset_id)
          Message.success(resp.message)
        } catch (error) {
          console.log(error)
        } finally {
          callback?.()
        }
      },
    })
  }
  return {
    handleDelete,
  }
}

export function useCreateOrUpdateDataset() {
  const loading = ref(false)
  const defaultForm = {
    icon: 'https://picsum.photos/400',
    name: '',
    description: '',
  }
  const form = reactive({ ...defaultForm })
  const formRef = useTemplateRef<FormInstance>('formRef')
  const showUpdateModal = ref(false)

  // 更新 showUpdateModal
  const updateShowUpdateModal = (new_value: boolean, callback?: () => void) => {
    showUpdateModal.value = new_value
    callback?.()
  }

  // 表单提交
  const saveDataset = async (dataset_id?: string) => {
    try {
      loading.value = true
      if (dataset_id != undefined && dataset_id !== '') {
        // 更新
        const resp = await updateDataset(dataset_id, form)
        Message.success(resp.message)
      } else {
        const resp = await createDataset(form)
        Message.success(resp.message)
      }
    } catch (error) {
      console.log(error)
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    form,
    formRef,
    showUpdateModal,
    updateShowUpdateModal,
    saveDataset,
  }
}
