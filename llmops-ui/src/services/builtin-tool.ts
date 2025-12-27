import type { GetBUiltinToolsResponse, GetCategoriesResponse } from '@/models/builtin-tool'
import { get } from '@/utils/request'

// 获取内置分类列表信息
export const getCategories = () => {
  return get<GetCategoriesResponse>('/builtin-tools/categories')
}

// 获取所有内置工具提供者列表
export const getBuiltinTools = () => {
  return get<GetBUiltinToolsResponse>('/builtin-tools')
}
