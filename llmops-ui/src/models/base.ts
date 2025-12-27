// 基础响应数据格式
export interface BaseResponse<T> {
  code: string
  message: string
  data: T
}

export interface Paginator {
  total_page: number
  total_record: number
  current_page: number
  page_size: number
}

// 基础分页响应数据格式
export type BasePaginationResponse<T> = BaseResponse<{
  list: Array<T>
  paginator: Paginator
}>
