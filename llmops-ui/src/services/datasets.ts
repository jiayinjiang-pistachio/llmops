import type { BaseResponse } from '@/models/base'
import type {
  CreateDatasetReq,
  CreateDocumentsReq,
  CreateDocumentsResp,
  CreateSegmentReq,
  GetDaatsetQueriesResp,
  GetDatasetResp,
  GetDatasetsWithPageResp,
  GetDocumentResponse,
  GetDocumentsStatusResp,
  GetDocumentsWithPageRequest,
  GetDocumentsWithPageResponse,
  GetSegmentResp,
  GetSegmentsWithPageReq,
  GetSegmentsWithPageResp,
  HitReq,
  HitResp,
  UpdateDatasetReq,
  UpdateSegmentReq,
} from '@/models/dataset'
import { get, post } from '@/utils/request'

export const getDatasetsWithPage = (current_page = 1, page_size = 20, search_word = '') => {
  return get<GetDatasetsWithPageResp>('/datasets', {
    params: {
      current_page,
      page_size,
      search_word,
    },
  })
}

// 新增知识库
export const createDataset = (req: CreateDatasetReq) => {
  return post<BaseResponse<string>>('/datasets', {
    body: req,
  })
}

// 更新知识库
export const updateDataset = (dataset_id: string, req: UpdateDatasetReq) => {
  return post<BaseResponse<string>>(`/datasets/${dataset_id}`, {
    body: req,
  })
}

// 删除知识库
export const deleteDataset = (dataset_id: string) => {
  return post<BaseResponse<string>>(`/datasets/${dataset_id}/delete`)
}

// 查看知识库详情
export const getDataset = (dataset_id: string) => {
  return get<GetDatasetResp>(`/datasets/${dataset_id}`)
}

// 获取文档分页列表数据
export const getDocumentsWithPage = (
  dataset_id: string,
  req: GetDocumentsWithPageRequest = {
    current_page: 1,
    page_size: 20,
    search_word: '',
  },
) => {
  return get<GetDocumentsWithPageResponse>(`/datasets/${dataset_id}/documents`, {
    params: req,
  })
}

// 获取指定文档详情
export const getDocument = (dataset_id: string, document_id: string) => {
  return get<GetDocumentResponse>(`/datasets/${dataset_id}/documents/${document_id}`)
}

// 更新指定文档的启用状态
export const updateDocumentEnabled = (
  dataset_id: string,
  document_id: string,
  enabled: boolean,
) => {
  return post<BaseResponse<string>>(`/datasets/${dataset_id}/documents/${document_id}/enabled`, {
    body: {
      enabled,
    },
  })
}

// 删除指定文档信息
export const deleteDocument = (dataset_id: string, document_id: string) => {
  return post<BaseResponse<string>>(`/datasets/${dataset_id}/documents/${document_id}/delete`)
}

// 更新文档名字
export const updateDocumentName = (dataset_id: string, document_id: string, name: string) => {
  return post<BaseResponse<string>>(`/datasets/${dataset_id}/documents/${document_id}/name`, {
    body: {
      name,
    },
  })
}

// 知识库召回测试
export const hit = (dataset_id: string, req: HitReq) => {
  return post<HitResp>(`/datasets/${dataset_id}/hit`, {
    body: req,
  })
}

// 最近查询记录
export const getDatasetQueries = (dataset_id: string) => {
  return get<GetDaatsetQueriesResp>(`/datasets/${dataset_id}/queries`)
}

// 上传文档到知识库
export const createDocuments = (dataset_id: string, req: CreateDocumentsReq) => {
  return post<CreateDocumentsResp>(`/datasets/${dataset_id}/documents`, {
    body: req,
  })
}

// 根据批处理获取文档的处理状态
export const getDocumentsStatus = (dataset_id: string, batch: string) => {
  return get<GetDocumentsStatusResp>(`/datasets/${dataset_id}/documents/batch/${batch}`)
}

// 获取指定的文档片段列表
export const getSegmentsWithPage = (
  dataset_id: string,
  document_id: string,
  req: GetSegmentsWithPageReq,
) => {
  return get<GetSegmentsWithPageResp>(`/datasets/${dataset_id}/documents/${document_id}/segments`, {
    params: req,
  })
}

// 新增文档片段信息
export const createSegment = (dataset_id: string, document_id: string, req: CreateSegmentReq) => {
  return post<BaseResponse<string>>(`/datasets/${dataset_id}/documents/${document_id}/segments`, {
    body: req,
  })
}

// 删除指定文档片段信息
export const deleteSegment = (dataset_id: string, document_id: string, segment_id: string) => {
  return post<BaseResponse<string>>(
    `/datasets/${dataset_id}/documents/${document_id}/segments/${segment_id}/delete`,
  )
}

// 修改文档片段内容
export const updateSegment = (
  dataset_id: string,
  document_id: string,
  segment_id: string,
  req: UpdateSegmentReq,
) => {
  return post<BaseResponse<string>>(
    `/datasets/${dataset_id}/documents/${document_id}/segments/${segment_id}`,
    {
      body: req,
    },
  )
}

// 更新文档片段的启用状态
export const updateSegmentEnabled = (
  dataset_id: string,
  document_id: string,
  segment_id: string,
  enabled: boolean,
) => {
  return post<BaseResponse<string>>(
    `/datasets/${dataset_id}/documents/${document_id}/segments/${segment_id}/enabled`,
    {
      body: { enabled },
    },
  )
}

// 查询文档片段详情
export const getSegment = (dataset_id: string, document_id: string, segment_id: string) => {
  return get<GetSegmentResp>(
    `/datasets/${dataset_id}/documents/${document_id}/segments/${segment_id}`,
  )
}
