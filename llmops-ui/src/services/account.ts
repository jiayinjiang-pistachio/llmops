import type { GetCurrentUserResp } from '@/models/account'
import type { BaseResponse } from '@/models/base'
import { get, post } from '@/utils/request'

// 获取当前账号信息
export const getCurrentUser = () => {
  return get<GetCurrentUserResp>('/account')
}

// 修改当前登录账号密码
export const updatePassword = (password: string) => {
  return post<BaseResponse<string>>('/account/password', {
    body: {
      password,
    },
  })
}

// 修改当前登录账号名称
export const updateName = (name: string) => {
  return post<BaseResponse<string>>('/account/name', {
    body: { name },
  })
}

// 修改当前登录账号头像
export const updateAvatar = (avatar: string) => {
  return post<BaseResponse<string>>('/account/avatar', {
    body: {avatar}
  })
}
