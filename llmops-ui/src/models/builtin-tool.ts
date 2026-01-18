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

// 获取指定内置插件详情
export type GetBuiltinToolResponse = BaseResponse<{
  name: string
  label: string
  description: string
  provider: {
    name: string
    label: string
    category: string
    background: string
    description: string
  }
  params: {
    name: string
    label: string
    type: string
    required: boolean
    default: any
    min: number
    max: number
    options: { value: string; label: string }[]
  }[]
  inputs: {
    type: string
    name: string
    required: boolean
    description: string
  }[]
  created_at: number
}>
