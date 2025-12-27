import type { BaseResponse } from './base'

// 获取内置插件分类响应接口
export type CategoryItem = {
  category: string
  icon: string
  name: string
}
export type GetCategoriesResponse = BaseResponse<CategoryItem[]>

// 获取所有内置插件列表
export type BuiltinToolItem = {
  name: string
  label: string
  description: string
  inputs: {
    name: string
    required: boolean
    type: string
    description: string
  }[]
}
export type BuiltinProviderItem = {
  background: string
  category: string
  created_at: number
  description: string
  label: string
  name: string
  tools: BuiltinToolItem[]
}
export type GetBUiltinToolsResponse = BaseResponse<BuiltinProviderItem[]>
