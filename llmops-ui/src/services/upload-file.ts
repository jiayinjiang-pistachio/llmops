import type { UploadImageResp } from '@/models/upload-file'
import { upload } from '@/utils/request'

export const uploadImage = (image: File) => {
  // 构建表单并添加图片数据
  const formData = new FormData()
  formData.append('file', image)

  // 调用upload服务实现图片上传
  return upload<UploadImageResp>(`/upload-files/image`, {
    data: formData,
  })
}
