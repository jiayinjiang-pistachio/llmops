import type { BasePaginationResponse } from './base'

// 获取自定义API插件响应接口
export type ApiToolProviderItem = {
  id: string
  name: string
  icon: string
  description: string
  headers: any[]
  tools: any[]
  created_at: number
}
export type GetAPiToolProvidersWithPageResponse = BasePaginationResponse<ApiToolProviderItem>
