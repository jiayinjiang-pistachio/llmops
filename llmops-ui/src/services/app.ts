import { ssePost } from '@/utils/request'

export const debugApps = async (
  app_id: string,
  query: string,
  onData: (eventResponse: { [key: string]: any }) => void,
) => {
  return ssePost(
    `/app/${app_id}/debug`,
    {
      body: {
        query,
      },
    },
    onData,
  )
}
