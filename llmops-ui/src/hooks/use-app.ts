import type {
  AppDetail,
  DebugConversationMessageItem,
  DraftAppConfig,
  PublishHistoryItem,
  UpdateDraftAppConfigReq,
} from '@/models/app'
import type { Paginator } from '@/models/base'
import {
  cancelPublish,
  debugChat,
  deleteDebugConversation,
  fallbackHistoryDraft,
  getApp,
  getDebugConaversationMessagesWithPage,
  getDebugConversationSummary,
  getDraftAppConfig,
  getPublishHistoriesWithPage,
  publish,
  stopDebugChat,
  updateDebugConversationSummary,
  updateDraftAppConfig,
} from '@/services/app'
import { Message, Modal } from '@arco-design/web-vue'
import { onMounted, reactive, ref } from 'vue'

export const useGetApp = (app_id: string) => {
  const loading = ref(false)
  const app = reactive({} as AppDetail)

  const loadApp = async (app_id: string, loadingFlag = true) => {
    try {
      if (loadingFlag) {
        loading.value = true
      }
      const resp = await getApp(app_id)
      const data = resp.data

      Object.assign(app, { ...data })
    } finally {
      if (loadingFlag) {
        loading.value = false
      }
    }
  }

  onMounted(async () => await loadApp(app_id))

  return {
    loading,
    app,
    loadApp,
  }
}

export const usePublish = () => {
  const loading = ref(false)

  const handlePublish = async (app_id: string) => {
    try {
      loading.value = true
      const resp = await publish(app_id)
      Message.success(resp.message)
    } finally {
      loading.value = false
    }
  }

  return { loading, handlePublish }
}

export const useCancelPublish = () => {
  const loading = ref(false)

  const handleCancelPublish = async (app_id: string, callback?: () => void) => {
    Modal.warning({
      title: '要取消发布该 Agent应用吗？',
      content:
        '取消发布后，WebApp以及发布的社交平台均无法使用该Agent，如需要更新WebApp地址，请使用地址重新生成功能',
      hideCancel: false,
      onOk: async () => {
        try {
          loading.value = true
          const resp = await cancelPublish(app_id)
          Message.success(resp.message)
        } finally {
          loading.value = false
          callback?.()
        }
      },
    })
  }

  return { loading, handleCancelPublish }
}

export const useGetPublishHistoriesWithPage = () => {
  const loading = ref(false)
  const defaultPaginator: Paginator = {
    current_page: 1,
    page_size: 10,
    total_page: 0,
    total_record: 0,
  }
  const publishHistories = reactive<PublishHistoryItem[]>([])
  const paginator = reactive({ ...defaultPaginator })

  const loadPublishHistories = async (app_id: string, init = false) => {
    if (!init && paginator.current_page > paginator.total_page) {
      return
    }

    try {
      loading.value = true

      // 如果不是初始化，则请求下一页
      const targetPage = init ? 1 : paginator.current_page + 1

      const resp = await getPublishHistoriesWithPage(app_id, {
        current_page: targetPage,
        page_size: paginator.page_size,
      })

      const data = resp.data

      updatePaginator(data.paginator)

      // 追加或是覆盖
      if (init) {
        publishHistories.splice(0, publishHistories.length, ...data.list)
      } else {
        publishHistories.push(...data.list)
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

  return {
    loading,
    publishHistories,
    paginator,
    loadPublishHistories,
  }
}

export const useFallbackHistoryToDraft = () => {
  const loading = ref(false)

  const handleFallbackHistoryToDraft = async (
    app_id: string,
    app_config_version_id: string,
    callback?: () => void,
  ) => {
    try {
      loading.value = true
      const resp = await fallbackHistoryDraft(app_id, app_config_version_id)

      Message.success(resp.message)
    } finally {
      loading.value = false
      callback?.()
    }
  }

  return { loading, handleFallbackHistoryToDraft }
}

export const useGetDraftAppConfig = (app_id: string) => {
  const loading = ref(false)
  const draftAppConfigForm = reactive({} as DraftAppConfig)

  const loadDraftAppConfig = async (app_id: string) => {
    try {
      loading.value = true
      const resp = await getDraftAppConfig(app_id)
      const data = resp.data

      Object.assign(draftAppConfigForm, {
        preset_prompt: data.preset_prompt,
        long_term_memory: data.long_term_memory,
        opening_statement: data.opening_statement,
        opening_questions: data.opening_questions,
        suggested_after_answer: data.suggested_after_answer,
        review_config: data.review_config,
        datasets: data.datasets,
        retrieval_config: data.retrieval_config,
        tools: data.tools,
      } as DraftAppConfig)
    } finally {
      loading.value = false
    }
  }

  onMounted(async () => {
    await loadDraftAppConfig(app_id)
  })

  return {
    loading,
    draftAppConfigForm,
    loadDraftAppConfig,
  }
}

export const useUpdateDraftAppConfig = () => {
  const loading = ref(false)

  const handleUpdateDraftAppConfig = async (
    app_id: string,
    draft_app_config: UpdateDraftAppConfigReq,
  ) => {
    try {
      loading.value = true

      await updateDraftAppConfig(app_id, draft_app_config)
      // Message.success(resp.message)
    } finally {
      loading.value = false
    }
  }

  return { loading, handleUpdateDraftAppConfig }
}

export const useGetDebugConversationSummary = () => {
  const loading = ref(false)
  const debug_conversation_summary = ref('')

  const loadDebugConversationSummary = async (app_id: string) => {
    try {
      loading.value = true

      const resp = await getDebugConversationSummary(app_id)
      const data = resp.data

      debug_conversation_summary.value = data.summary
    } finally {
      loading.value = false
    }
  }

  return { loading, debug_conversation_summary, loadDebugConversationSummary }
}

export const useUpdateDebugConversationSummary = () => {
  const loading = ref(false)

  const handleUpdateDebugConversationSummary = async (app_id: string, summary: string) => {
    try {
      loading.value = true
      const resp = await updateDebugConversationSummary(app_id, summary)
      Message.success(resp.message)
    } finally {
      loading.value = false
    }
  }

  return { loading, handleUpdateDebugConversationSummary }
}

export const useDeleteDebugConversation = () => {
  const loading = ref(false)

  const handleDeleteDebugConversation = async (app_id: string) => {
    try {
      loading.value = true
      const resp = await deleteDebugConversation(app_id)
      Message.success(resp.message)
    } finally {
      loading.value = false
    }
  }

  return { loading, handleDeleteDebugConversation }
}

export const useGetDebugConversationMessagesWithPage = () => {
  const loading = ref(false)
  const messages = ref<DebugConversationMessageItem[]>([])
  const created_at = ref(0)
  const defaultPaginator: Paginator = {
    current_page: 1,
    page_size: 5,
    total_page: 0,
    total_record: 0,
  }
  const paginator = ref({ ...defaultPaginator })

  const loadDebugConversationMessages = async (app_id: string, init = false) => {
    if (!init && paginator.value.current_page > paginator.value.total_page) {
      return
    }

    try {
      loading.value = true

      // 如果不是初始化，则请求下一页
      const targetPage = init ? 1 : paginator.value.current_page + 1

      const resp = await getDebugConaversationMessagesWithPage(app_id, {
        current_page: targetPage,
        page_size: paginator.value.page_size,
      })

      const data = resp.data

      paginator.value = data.paginator

      // 追加或是覆盖
      if (init) {
        messages.value = data.list
      } else {
        messages.value.push(...data.list)
        created_at.value = data.list[0]?.created_at ?? 0
      }
    } finally {
      loading.value = false
    }
  }

  return { loading, messages, paginator, loadDebugConversationMessages }
}

export const useDebugChat = () => {
  const loading = ref(false)
  let abortController: AbortController | null = null // 记录当前的控制器

  const handleDebugChat = async (
    app_id: string,
    query: string,
    onData: (event_response: Record<string, any>) => void,
  ) => {
    // 如果上一次还在 loading，先中断它
    if (abortController) {
      abortController.abort()
    }

    abortController = new AbortController()

    try {
      loading.value = true

      console.log('loading...start')
      // 将 signal 传递下去
      await debugChat(app_id, query, onData, abortController.signal)
      console.log('loading end...')
    } catch (err: any) {
      if (err.name === 'AbortError') {
        console.log('请求已被主动取消')
      } else {
        throw err
      }
    } finally {
      loading.value = false
      abortController = null
    }
  }

  return { loading, handleDebugChat }
}

export const useStopDebugChat = () => {
  const loading = ref(false)

  const handleStopDebugChat = async (app_id: string, task_id: string) => {
    try {
      loading.value = true

      await stopDebugChat(app_id, task_id)
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    handleStopDebugChat,
  }
}
