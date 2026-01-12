import type { PasswordLoginResp } from '@/models/auth'
import type { BaseResponse } from '@/models/base'
import { post } from '@/utils/request'

// 账号密码登录请求
export const passwordLogin = (email: string, password: string) => {
  return post<PasswordLoginResp>('/auth/password-login', {
    body: {
      email,
      password
    }
  })
}

// 退出登录
export const logout = () => {
  return post<BaseResponse<string>>('/auth/logout')
}
