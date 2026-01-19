import type {
  CreateAppReq,
  GetAppResp,
  GetDebugConversationMessagesWithPageReq,
  GetDebugConversationMessagesWithPageResp,
  GetDraftAppConfigResp,
  GetPublishHistoriesWithPageResp,
  UpdateDraftAppConfigReq,
} from '@/models/app'
import type { BasePaginatorReq, BaseResponse } from '@/models/base'
import { get, post, ssePost } from '@/utils/request'

// 获取应用基础信息
export const getApp = (app_id: string) => {
  return get<GetAppResp>(`/apps/${app_id}`)
}

// 在个人空间新增应用
export const createApp = (req: CreateAppReq) =>
  post<BaseResponse<{ id: string }>>('/apps', {
    body: req,
  })

// 获取特定应用的草稿配置信息
export const getDraftAppConfig = (app_id: string) =>
  get<GetDraftAppConfigResp>(`/apps/${app_id}/draft-app-config`)

// 更新特定应用的草稿配置信息
export const updateDraftAppConfig = (app_id: string, req: UpdateDraftAppConfigReq) =>
  post<BaseResponse<string>>(`/apps/${app_id}/draft-app-config`, {
    body: req,
  })

// 获取应用的调试长期记忆
export const getDebugConversationSummary = (app_id: string) =>
  get<BaseResponse<{ summary: string }>>(`/apps/${app_id}/summary`)

// 更新应用的调试长期记忆
export const updateDebugConversationSummary = (app_id: string, summary: string) =>
  post<BaseResponse<string>>(`/apps/${app_id}/summary`, {
    body: { summary },
  })

// 应用调试会话，该接口为流式事件输出
export const debugChat = async (
  app_id: string,
  query: string,
  onData: (event_response: Record<string, any>) => void,
  signal?: AbortSignal
) => {
  console.log('debugChat start...')
  const sseResult = await ssePost(
    `/apps/${app_id}/conversations`,
    {
      body: {
        query,
      },
    },
    onData,
    signal
  )
  console.log('debugChat end...')


  return sseResult
}

// 停止某次应用的调试会话
export const stopDebugChat = (app_id: string, task_id: string) =>
  post<BaseResponse<string>>(`/apps/${app_id}/conversations/tasks/${task_id}/stop`)

// 获取应用的调试会话消息列表
export const getDebugConaversationMessagesWithPage = (
  app_id: string,
  req?: GetDebugConversationMessagesWithPageReq,
) =>
  get<GetDebugConversationMessagesWithPageResp>(`/apps/${app_id}/conversations/messages`, {
    params: req,
  })

// 清空应用的调试会话记录
export const deleteDebugConversation = (app_id: string) =>
  post<BaseResponse<string>>(`/apps/${app_id}/conversations/delete-debug-conversation`)

// 发布/更新应用的配置信息(基于草稿配置发布，所以不用传参)
export const publish = (app_id: string) => post<BaseResponse<string>>(`/apps/${app_id}/publish`)

// 取消置顶应用的发布
export const cancelPublish = (app_id: string) =>
  post<BaseResponse<string>>(`/apps/${app_id}/cancel-publish`)

// 获取应用的发布历史列表信息
export const getPublishHistoriesWithPage = (app_id: string, req: BasePaginatorReq) =>
  get<GetPublishHistoriesWithPageResp>(`/apps/${app_id}/publish-histories`, {
    params: req,
  })

// 回退指定的历史配置到草稿
export const fallbackHistoryDraft = (app_id: string, app_config_version_id: string) =>
  post<BaseResponse<string>>(`/apps/${app_id}/fallback-history`, {
    body: {
      app_config_version_id,
    },
  })
