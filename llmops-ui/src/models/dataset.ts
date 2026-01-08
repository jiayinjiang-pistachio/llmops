import type { BasePaginationResponse } from './base';

// 获取知识库分页列表接口响应结构
export interface DatasetItem {
  id: string
  name: string
  icon: string
  description: string
  document_count: number
  character_count: number
  related_app_count: number
  updated_at: number
  created_at: number
}

export type GetDatasetsWithPageResp = BasePaginationResponse<DatasetItem>
