import type { BaseResponse } from '@/models/base';

export interface CurrentUser {
  id: string
  name: string
  email: string
  avatar: string
  last_login_ip: string
  last_login_at: number
  created_at: number
}

export type GetCurrentUserResp = BaseResponse<CurrentUser>
