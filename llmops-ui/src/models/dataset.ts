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

// 上传文档列表到知识库请求
export interface CreateDocumentsReq {
  upload_file_ids: string[]
  process_type: 'custom' | 'automatic'
  rule: {
    pre_process_rules: {
      id: 'remove_extra_space' | 'remove_url_and_email'
      enabled: boolean
    }[]
    segment: {
      separators: string[]
      chunk_size: number
      chunk_overlap: number
    }
  }
}

// 上传文档列表到知识库响应
export interface CreateDocument {
  batch: string
  documents: {
    id: string
    name: string
    status: string
    created_at: string
  }
}
export type CreateDocumentsResp = BaseResponse<CreateDocument>

// 批处理标识获取处理进度响应
export interface DocumentStatusItem {
  id: string
  name: string
  size: number
  extension: string
  mime_type: string
  position: number
  segment_count: number
  completed_segment_count: number
  error: string
  status: string
  processing_started_at: number
  parsing_completed_at: number
  splitting_completed_at: number
  indexing_completed_at: number
  completed_at: number
  stopped_at:number
  created_at: number
}
export type GetDocumentsStatusResp = BaseResponse<DocumentStatusItem[]>

// 获取指定文档的片段列表请求结构
export interface GetSegmentsWithPageReq {
  current_page: number
  page_size: number
  search_word: string
}

// 获取指定文档的片段列表响应
export interface SegmentItem {
  id: string
  dataset_id: string
  documentt_id: string
  position: number
  content: string
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

export type GetSegmentsWithPageResp = BasePaginationResponse<SegmentItem>

// 新增文档片段请求
export interface CreateSegmentReq {
  content: string
  keywords: string[]
}

// 修改文档片段请求
export interface UpdateSegmentReq {
  content: string
  keywords: string[]
}

// 查询文档片段响应
export interface SegmentDetail {
  id: string
  document_id: string
  dataset_id: string
  position: number
  content: string
  keywords: string[]
  character_count: number
  token_count: number
  hit_count: number
  hash: string
  enabled: boolean
  status: string
  error: string
  updated_at: number
  created_at: number
}

export type GetSegmentResp = BaseResponse<SegmentDetail>
