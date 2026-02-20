import type { BaseResponse } from '@/models/base'
import { ssePost, upload } from '@/utils/request'

export const audioToText = (file: Blob) => {
  // 构建表单并添加音频数据
  const formData = new FormData()

  formData.append('file', file, 'recording.wav')

  // 调用upload服务实现音频上传
  return upload<BaseResponse<{ text: string }>>('/audio/audio-to-text', {
    data: formData,
  })
}

export const messageToAudio = (
  message_id: string,
  onData: (event_response: Record<string, any>) => void,
) => {
  return ssePost(
    '/audio/message-to-audio',
    {
      body: { message_id },
    },
    onData,
  )
}
