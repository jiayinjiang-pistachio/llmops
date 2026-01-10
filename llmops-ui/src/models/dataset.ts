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

// 获取指定的知识库文档列表分页请求
export interface GetDocumentsWithPageRequest {
  current_page: number
  page_size: number
  search_word: string
}

// 获取指定知识库文档分页列表响应结构
export interface DocumentItem {
  id: string
  name: string
  character_count: number
  hit_count: number
  position: number
  enabled: boolean
  disabled_at: number
  status: string
  error: string
  updated_at: number
  created_at: number
}
export type GetDocumentsWithPageResponse = BasePaginationResponse<DocumentItem>

// 获取指定文档详情响应结构
export interface DocumentDetail {
  id: string
  dataset_id: string
  name: string
  segment_count: number
  character_count: number
  hit_count: number
  position: number
  enabled: boolean
  disabled_at: number
  status: string
  error: string
  updated_at: number
  created_at: number
}
export type GetDocumentResponse = BaseResponse<DocumentDetail>

// 知识库召回测试请求
export interface HitReq {
  retrieval_strategy: string
  k: number
  query: string
  score: number
}

// 知识库召回测试响应
export interface HitItem {
  id: string
  document: {
    id: string
    name: string
    extension: string
    mime_type: string
  }
  content: string
  dataset_id: string
  score: number
  position: number
  keywords: string[]
  character_count: number
  token_count: number
  hit_count: number
  enabled: boolean
  disabled_at: number
  status: string
  error: string
  updated_at: number
  created_at: number
}
export type HitResp = BaseResponse<HitItem[]>

// 知识库最新查询列表
export interface DatasetQueryItem {
  id: string
  query: string
  source: string
  dataset_id: string
  created_at: number
}
export type GetDaatsetQueriesResp = BaseResponse<DatasetQueryItem[]>
