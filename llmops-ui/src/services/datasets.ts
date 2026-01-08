import type { GetDatasetsWithPageResp } from '@/models/dataset'
import { get } from '@/utils/request'

export const getDatasetsWithPage = (
  current_page = 1,
  page_size = 20,
  search_word = ''
) => {
  return get<GetDatasetsWithPageResp>('/datasets', {
    params: {
      current_page,
      page_size,
      search_word
    }
  })
}
