import type { BasePaginationResponse, BaseResponse } from './base';

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

// 新增知识库请求数据
export interface CreateDatasetReq {
  name: string
  icon: string
  description: string
}

// 更新知识库请求数据
export interface UpdateDatasetReq {
  name: string
  icon: string
  description: string
}

// 获取知识库详情请求
export interface DatasetDetail {
  id: string
  name: string
  icon: string
  description: string
  document_count: number
  hit_count: number
  related_app_count: number
  character_count: number
  updated_at: number
  created_at: number
}

export type GetDatasetResp = BaseResponse<DatasetDetail>
