import type { AuthorizeResp, ProviderResp } from '@/models/oauth'
import { get, post } from '@/utils/request'

// 获取指定第三方授权服务的重定向地址
export const provider = (provider_name: string) => {
  return get<ProviderResp>(`/oauth/${provider_name}`)
}

// 指定第三方授权服务认证地址
export const authorize = (provider_name: string, code: string) => {
  return post<AuthorizeResp>(`/oauth/authorize/${provider_name}`, {
    body: {
      code
    }
  })
}
