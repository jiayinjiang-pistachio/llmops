import type { BaseResponse } from '@/models/base'
import type {
  CreateDatasetReq,
  GetDatasetResp,
  GetDatasetsWithPageResp,
  GetDocumentResponse,
  GetDocumentsWithPageRequest,
  GetDocumentsWithPageResponse,
  UpdateDatasetReq,
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
    params: req
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
      enabled
    }
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
      name
    }
  })
}
