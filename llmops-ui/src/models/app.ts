import type { BasePaginationResponse, BasePaginatorReq, BaseResponse } from './base'

// 获取应用信息响应结构
export interface AppDetail {
  id: string
  debug_conversation_id: string
  name: string
  icon: string
  description: string
  status: string
  draft_updated_at: number
  updated_at: number
  created_at: number
}
export type GetAppResp = BaseResponse<AppDetail>

// 新增应用请求
export type CreateAppReq = {
  name: string
  icon: string
  description: string
}

// 回去特定应用的草稿配置响应结构
export interface DraftAppConfig {
  id: string
  modal_config: {
    provider: string
    model: string
    api_key?: string // todo
    base_url?: string // todo
    parameters: Record<string, any>
  }
  dialog_round: number
  preset_prompt: string
  tools: {
    type: string
    provider: {
      id: string
      name: string
      label: string
      icon: string
      description: string
    }
    tool: {
      id: string
      name: string
      label: string
      description: string
      params: Record<string, any>
    }
  }[]
  workflows: {
    id: string
    name: string
    icon: string
    description: string
  }[]
  datasets: {
    id: string
    name: string
    description: string
  }[]
  retrieval_config: {
    retrieval_strategy: string
    k: number
    score: number
  }
  long_term_memory: {
    enable: boolean
  }
  opening_statement: string
  opening_questions: string[]
  speech_to_text: {
    enable: boolean
  }
  text_to_speech: {
    enable: boolean
    voice: string
    auto_play: boolean
  }
  suggested_after_answer: {
    enable: boolean
  }
  review_config: {
    enable: boolean
    keywords: string[]
    inputs_config: {
      enable: boolean
      preset_response: string
    }
    outputs_config: {
      enable: boolean
    }
  }
  updated_at: number
  created_at: number
}
export type GetDraftAppConfigResp = BaseResponse<DraftAppConfig>

// 更新特定应用的草稿配置请求结构
export type UpdateDraftAppConfigReq = {
  model?: {
    provider: string
    model: string
    api_key?: string // todo
    base_url?: string // todo
    parameters: Record<string, any>
  }
  dialog_round?: number
  preset_prompt?: string
  tools?: {
    type: string
    provider_id: string
    tool_id: string
    params: Record<string, any>
  }[]
  workflows?: string[]
  datasets?: string[]
  retrieval_config?: {
    retrieval_strategy: string
    k: number
    score: number
  }
  long_term_memory?: {
    enable: boolean
  }
  opening_statements?: string
  opening_questions?: string[]
  speech_to_text?: {
    enable: boolean
  }
  text_to_speech?: {
    enable: boolean
    voice: string
    auto_play: boolean
  }
  suggested_after_answer?: {
    enable: boolean
  }
  review_config?: {
    enable: boolean
    keywords: string[]
    inputs_config: {
      enable: boolean
      preset_response: string
    }
    outputs_config: {
      enable: boolean
    }
  }
}

// 获取应用的调试会话消息列表响应结构
export interface DebugConversationMessageItem {
  id: string
  conversation_id: string
  query: string
  answer: string
  total_token_count: number
  latency: number
  agent_thoughts: {
    id: string
    position: number
    event: string
    thought: string
    observation: string
    tool: string
    tool_input: Record<string, any>
    latency: number
    created_at: number
  }[]
  created_at: number
}
export type GetDebugConversationMessagesWithPageResp = BasePaginationResponse<DebugConversationMessageItem>

// 获取应用的发布历史配置列表分页响应结构
export interface PublishHistoryItem {
  id: string
  version: number
  created_at: number
}

export type GetPublishHistoriesWithPageResp = BasePaginationResponse<PublishHistoryItem>

// 获取应用的调试会话消息列表请求结构
export type GetDebugConversationMessagesWithPageReq = BasePaginatorReq & {
  created_at?: number
}
