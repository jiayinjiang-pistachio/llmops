import type { BaseResponse } from './base';

export interface UploadImageRespData {
  image_url: string
}

export type UploadImageResp = BaseResponse<UploadImageRespData>

export interface UploadFileRespData {
  id: string
  account_id: string
  name: string
  key: string
  size: number
  extension: string
  mime_type: string
  created_at: number
}
export type UploadFileResp = BaseResponse<UploadFileRespData>
