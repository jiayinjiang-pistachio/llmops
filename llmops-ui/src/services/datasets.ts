import type { BaseResponse } from '@/models/base'
import type { CreateDatasetReq, GetDatasetResp, GetDatasetsWithPageResp, UpdateDatasetReq } from '@/models/dataset'
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
    body: req
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
