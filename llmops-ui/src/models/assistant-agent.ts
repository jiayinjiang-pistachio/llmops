import type { BasePaginatorReq, BasePaginationResponse } from '@/models/base'

// 获取辅助Agent会话消息分页列表请求结构
export type GetAssistantAgentMessagesWithPageRequest = BasePaginatorReq & {
  created_at?: number
}

// 获取辅助Agent会话消息分页列表响应结构
export interface AssistantAgentMessageItem {
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
export type GetAssistantAgentMessagesWithPageResponse =
  BasePaginationResponse<AssistantAgentMessageItem>
