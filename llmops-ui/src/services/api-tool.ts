import type { CreateApiToolProviderRequest, GetApiToolProviderResponse, GetAPiToolProvidersWithPageResponse, UpdateApiToolProviderRequest } from '@/models/api-tool'
import type { BaseResponse } from '@/models/base'
import { get, post } from '@/utils/request'

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

// 校验openapi schema数据
export const validateOpenAPISchema = (openapi_schema: string) => {
  return post<BaseResponse<string>>('/api-tools/validate-openapi-schema', {
    body: {
      openapi_schema,
    },
  })
}

// 创建自定义API工具提供者
export const createApiProvider = (req: CreateApiToolProviderRequest) => {
  return post<BaseResponse<string>>('/api-tools', {
    body: req,
  })
}

// 删除自定义API工具提供者
export const deleteApiToolProvider = (provider_id: string) => {
return post<BaseResponse<string>>(`/api-tools/${provider_id}/delete`)
}

// 更新自定义API工具提供者
export const updateAPiToolProvider = (provider_id: string, req: UpdateApiToolProviderRequest) => {
  return post<BaseResponse<string>>(`/api-tools/${provider_id}`, {
    body: req,
  })
}

// 查看API工具提供者
export const getApiToolProvider = (provider_id: string) => {
  return get<BaseResponse<GetApiToolProviderResponse>>(`/api-tools/${provider_id}`)
}

