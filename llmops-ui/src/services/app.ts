import { ssePost } from '@/utils/request'

export const debugApps = async (
  app_id: string,
  query: string,
  onData: (eventResponse: { [key: string]: any }) => void,
) => {
  return ssePost(
    `/apps/${app_id}/conversations`,
    {
      body: {
        query,
      },
    },
    onData,
  )
}
