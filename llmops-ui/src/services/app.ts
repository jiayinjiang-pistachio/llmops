import type { DebugAppsResponse } from '@/models/app'
import { post } from '@/utils/request'

export const debugApps = async (app_id: string, query: string) => {
  return post<DebugAppsResponse>(`/app/${app_id}/debug`, {
    body: {
      query,
    },
  })
}
