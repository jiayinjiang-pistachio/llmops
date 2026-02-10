import { type BasePaginatorReq, type BasePaginationResponse } from '@/models/base'

// 获取指定会话消息列表请求结构
export type GetConversationMessagesWithPageRequest = BasePaginatorReq & {
  created_at: number
}

// 获取指定会话消息列表响应结构
export interface AgentThoughtItem {
  id: string
  position: number
  event: string
  thought: string
  observation: string
  tool: string
  tool_input: Record<string, any>
  latency: number
  created_at: number
}
export type GetConversationMessagesWithPageResponse = BasePaginationResponse<{
  id: string
  conversation_id: string
  query: string
  answer: string
  total_token_count: number
  latency: number
  agent_thoughts: AgentThoughtItem[]
  created_at: number
}>
