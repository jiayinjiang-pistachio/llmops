import type { GetAPiToolProvidersWithPageResponse } from '@/models/api-tool'
import { get } from '@/utils/request'

// 获取自定义API列表分页数据
export const getApiToolProvidersWithPage = (
  current_page: number = 1,
  page_size: number = 20,
  search_word: string = '',
) => {
  return get<GetAPiToolProvidersWithPageResponse>('/api-tools', {
    params: {
      current_page,
      page_size,
      search_word,
    },
  })
}
