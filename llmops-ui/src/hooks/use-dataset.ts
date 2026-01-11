import type { Paginator } from '@/models/base'
import type {
  DatasetDetail,
  DatasetItem,
  DocumentDetail,
  DocumentItem,
  SegmentItem,
} from '@/models/dataset'
import type { FormInstance } from '@arco-design/web-vue'
import {
  createDataset,
  deleteDataset,
  deleteDocument,
  deleteSegment,
  getDataset,
  getDatasetsWithPage,
  getDocument,
  getDocumentsWithPage,
  getSegmentsWithPage,
  updateDataset,
  updateDocumentEnabled,
  updateSegmentEnabled,
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
    fileList: [] as any[],
    icon: '',
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

export const useGetDataset = (dataset_id: string) => {
  const loading = ref(false)
  const dataset: DatasetDetail = reactive({} as DatasetDetail)

  const loadDataset = async (dataset_id: string) => {
    try {
      loading.value = true
      const resp = await getDataset(dataset_id)
      const data = resp.data
      Object.assign(dataset, { ...data })
    } catch (error) {
      console.log(error)
    } finally {
      loading.value = false
    }
  }

  onMounted(() => {
    loadDataset(dataset_id)
  })

  return {
    loading,
    dataset,
    loadDataset,
  }
}

export const useGetDocumentsWithPage = (dataset_id: string) => {
  const route = useRoute()
  const loading = ref(false)
  const documents: DocumentItem[] = reactive([])
  const defaultPaginator = {
    current_page: 1,
    page_size: 20,
    total_page: 0,
    total_record: 0,
  }
  const paginator = reactive({ ...defaultPaginator })

  const loadDocuments = async (init = false) => {
    if (!init && paginator.current_page > paginator.total_page) {
      return
    }

    try {
      loading.value = true
      const resp = await getDocumentsWithPage(dataset_id, {
        current_page: Number(route.query?.current_page) || 1,
        page_size: Number(route.query?.page_size) || 20,
        search_word: (route.query?.search_word as string) || '',
      })

      const data = resp.data

      updatePaginator(data.paginator)

      documents.splice(0, documents.length, ...data.list)
    } catch (error) {
      console.log(error)
    } finally {
      loading.value = false
    }
  }

  const initPaginator = () => {
    Object.assign(paginator, { ...defaultPaginator })
  }

  const updatePaginator = (data: Paginator) => {
    paginator.current_page = data.current_page
    paginator.page_size = data.page_size
    paginator.total_page = data.total_page
    paginator.total_record = data.total_record
  }

  onMounted(async () => {
    await loadDocuments(true)
  })

  watch(
    () => route.query,
    async (newQuery, oldQuery) => {
      if (newQuery.search_word !== oldQuery.search_word) {
        initPaginator()
        await loadDocuments(true)
      } else if (newQuery.current_page !== oldQuery.current_page) {
        await loadDocuments()
      }
    },
  )

  return {
    loading,
    documents,
    paginator,
    loadDocuments,
  }
}

export const useDeleteDocument = () => {
  const handleDelete = (dataset_id: string, document_id: string, callback?: () => void) => {
    Modal.warning({
      title: '要删除该文档吗？',
      content: `删除文档后，知识库/向量数据库将无法检索到该文档，如需暂时关闭该文档的检索，可以选择禁用功能`,
      hideCancel: false,
      onOk: async () => {
        try {
          const resp = await deleteDocument(dataset_id, document_id)
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

export const useUpdatedDocumentEnabled = () => {
  const handleUpdate = async (
    dataset_id: string,
    document_id: string,
    enabled: boolean,
    callback?: () => void,
  ) => {
    try {
      const resp = await updateDocumentEnabled(dataset_id, document_id, enabled)
      const { message } = resp
      Message.success(message)
      callback?.()
    } catch (error) {
      console.log(error)
    }
  }

  return {
    handleUpdate,
  }
}

export const useGetDocument = (dataset_id: string, document_id: string) => {
  const loading = ref(false)
  const document = reactive({} as DocumentDetail)

  const loadDocument = async (dataset_id: string, document_id: string) => {
    try {
      loading.value = true
      const resp = await getDocument(dataset_id, document_id)
      const data = resp.data

      Object.assign(document, { ...data })
    } finally {
      loading.value = false
    }
  }

  onMounted(async () => {
    await loadDocument(dataset_id, document_id)
  })

  return {
    loading,
    document,
    loadDocument,
  }
}

export const useGetSegmentsWithPage = (dataset_id: string, document_id: string) => {
  const route = useRoute()
  const loading = ref(false)
  const segments = reactive<SegmentItem[]>([])
  const defaultPaginator: Paginator = {
    current_page: 1,
    page_size: 20,
    total_page: 0,
    total_record: 0,
  }
  const paginator: Paginator = reactive({ ...defaultPaginator })

  const loadSegments = async (init = false) => {
    if (init) {
      Object.assign(paginator, { ...defaultPaginator })
    } else if (paginator.current_page >= paginator.total_page) {
      return
    }

    try {
      loading.value = true

      // 如果不是初始化，则请求下一页
      const targetPage = init ? 1 : paginator.current_page + 1

      const resp = await getSegmentsWithPage(dataset_id, document_id, {
        current_page: targetPage,
        page_size: paginator.page_size,
        search_word: String(route.query?.search_word || ''),
      })
      const data = resp.data

      // 更新分页器
      updatePaginator(data.paginator)

      // 追加或覆盖数据
      if (init) {
        segments.splice(0, segments.length, ...data.list)
      } else {
        segments.push(...data.list)
      }
    } finally {
      loading.value = false
    }
  }

  const updatePaginator = (data: Paginator) => {
    paginator.current_page = data.current_page
    paginator.page_size = data.page_size
    paginator.total_page = data.total_page
    paginator.total_record = data.total_record
  }

  onMounted(async () => {
    await loadSegments(true)
  })

  watch(
    () => route.query?.search_word,
    async () => {
      await loadSegments(true)
    },
  )

  return {
    loading,
    segments,
    paginator,
    loadSegments,
  }
}

export const useDeleteSegment = () => {
  const handleDelete = async (
    dataset_id: string,
    document_id: string,
    segment_id: string,
    callback?: () => void,
  ) => {
    Modal.warning({
      title: '要删除该文档片段吗？',
      content: `删除文档片段后，知识库/向量数据库将无法检索到该文档片段，如需暂时关闭该片段的检索，可以选择禁用功能`,
      hideCancel: false,
      onOk: async () => {
        try {
          const resp = await deleteSegment(dataset_id, document_id, segment_id)
          Message.success(resp.message)
          callback?.()
        } finally {
        }
      },
    })
  }
  return {
    handleDelete,
  }
}

export const useUpdateSegmentEnabled = () => {
  const handleUpdate = async (
    dataset_id: string,
    document_id: string,
    segment_id: string,
    enabled: boolean,
    callback?: () => void,
  ) => {
    const resp = await updateSegmentEnabled(dataset_id, document_id, segment_id, enabled)
    Message.success(resp.message)
    callback?.()
  }

  return {
    handleUpdate,
  }
}
