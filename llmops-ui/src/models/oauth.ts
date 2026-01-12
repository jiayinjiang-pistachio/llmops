import type { BaseResponse } from '@/models/base';

export interface AuthProviderRedirect {
  redirect_ur: string
}

export type ProviderResp = BaseResponse<AuthProviderRedirect>

export interface OAuthCredentialInfo {
  access_token: string
  expire_at: number
}

export type AuthorizeResp = BaseResponse<OAuthCredentialInfo>
