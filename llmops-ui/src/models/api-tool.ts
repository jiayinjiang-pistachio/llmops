import type { BasePaginationResponse } from './base'

// 获取自定义API插件响应接口
export type ApiToolProviderItem = {
  id: string
  name: string
  icon: string
  description: string
  headers: any[]
  tools: {
    name: string
    description: string
    inputs: {
      name: string
      type: string
      required: boolean
      description: string
    }[]
  }[]
  created_at: number
}
export type GetAPiToolProvidersWithPageResponse = BasePaginationResponse<ApiToolProviderItem>

// 新增自定义API插件提供者请求结构
export type CreateApiToolProviderRequest = {
  name: string
  icon: string
  openapi_schema: string
  headers: Record<string, any>[]
}

// 更新自定义API工具提供者请求与响应结构
export type UpdateApiToolProviderRequest = {
  name: string
  icon: string
  openapi_schema: string
  headers: Record<string, any>[]
}

// 获取自定义API工具提供者响应结构体
export type GetApiToolProviderResponse = {
  id: string
  name: string
  icon: string
  openapi_schema: string
  headers: { key: string; value: any; }[]
  created_at: number
}
