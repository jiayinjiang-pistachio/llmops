import type { BaseResponse } from '@/models/base';

export interface CredentialInfo {
  access_token: string
  expire_at: number
}

export type PasswordLoginResp = BaseResponse<CredentialInfo>
