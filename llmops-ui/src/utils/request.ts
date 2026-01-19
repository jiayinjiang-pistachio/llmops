// 1. 接口超时100s
// 2. 不需要写api前缀，比如http://localhost:5000
// 3. 经常使用get、post，需要对这两个方法进行封装
// 4. 每次获取数据都要使用response.json()才可以获取数据，需要封装

import { apiPrefix, httpCode } from '@/config'
import { Message } from '@arco-design/web-vue'
import { useCredentialStore } from '@/stores/credential'
import router from '@/router'

const TIME_OUT = 100000

// 基础的配置
const baseFetchOptions = {
  method: 'GET',
  mode: 'cors',
  credetials: 'include', // 自动携带cookie、token等信息
  headers: new Headers({
    'Content-Type': 'application/json',
  }),
  redirect: 'follow', // 当接口请求出错，自动处理
}

// fetch 参数类型
type FetchOptionType = Omit<RequestInit, 'body'> & {
  body?: BodyInit | Record<string, unknown> | null
  params?: Record<string, unknown>
}

// 封装基础的fetch请求
const baseFetch = async <T>(url: string, fetchOptions: FetchOptionType): Promise<T> => {
  // 将所有的配置信息合并起来
  const options: typeof baseFetchOptions & FetchOptionType = Object.assign(
    {},
    baseFetchOptions,
    fetchOptions,
  )

  const { credential, clear: clearCredential } = useCredentialStore()
  const access_token = credential.access_token
  if (access_token) {
    options.headers.set('Authorization', `Bearer ${access_token}`)
  }

  // 组装 url
  let urlWithPrefix = `${apiPrefix}${url.startsWith('/') ? url : `/${url}`}`

  // 解构出对应的请求方法、params、body参数
  const { method, params, body } = options

  // 如果是get方法并且传递了params参数
  if (method === 'GET' && params) {
    const paramsArray: string[] = []
    Object.keys(params).forEach((key) => {
      const value = params[key] as string
      paramsArray.push(`${key}=${encodeURIComponent(value)}`)
    })

    if (urlWithPrefix.search(/\?/) !== -1) {
      urlWithPrefix += `&${paramsArray.join('&')}`
    } else {
      urlWithPrefix += `?${paramsArray.join('&')}`
    }

    delete options.params
  }

  if (body) {
    options.body = JSON.stringify(body)
  }

  return Promise.race([
    // 使用定时器来检测是否超时
    new Promise((_, reject) => {
      setTimeout(() => {
        reject('接口已超时')
      }, TIME_OUT)
    }),
    // 发起一个正常请求
    new Promise((resolve, reject) => {
      fetch(urlWithPrefix, options as RequestInit)
        .then(async (res) => {
          const json = await res.json()
          if (json.code === httpCode.success) {
            resolve(json)
          } else if (json.code === httpCode.unauthorized) {
            clearCredential()
            await router.replace({ path: '/auth/login' })
          } else {
            Message.error(json.message || '请求出错，请稍后重试')
            reject(json.message || '请求出错')
          }
        })
        .catch((err) => {
          Message.error(err.message || '请求出错，请稍后重试')
          reject(err)
        })
    }),
  ]) as Promise<T>
}

// // 封装基于post的sse（流式事件响应）请求
// export const ssePost = async (
//   url: string,
//   fetchOptions: FetchOptionType,
//   onData: (data: { [key: string]: any }) => void,
//   signal?: AbortSignal,
// ) => {
//   // 组装基础的fetch请求配置
//   // 关键：将信号传入 fetch
//   const options = Object.assign(
//     {},
//     baseFetchOptions,
//     {
//       method: 'POST',
//       headers: new Headers({
//         'Content-Type': 'application/json',
//         Connection: 'close', // 核心：告诉后端不要 Keep-Alive
//         'Cache-Control': 'no-cache',
//       }),
//       signal,
//     },
//     fetchOptions,
//   )
//   const { credential } = useCredentialStore()
//   const access_token = credential.access_token
//   if (access_token) {
//     options.headers.set('Authorization', `Bearer ${access_token}`)
//   }

//   // 组装请求URL
//   const urlWithPrefix = `${apiPrefix}${url.startsWith('/') ? url : `/${url}`}`

//   const { body } = fetchOptions
//   console.log('body: ', body)

//   if (body) {
//     console.log('body...')
//     options.body = JSON.stringify(body)
//   }

//   console.log('not body...')

//   return handleStream(urlWithPrefix, options as RequestInit, onData)
// }

export const ssePost = async (
  url: string,
  fetchOptions: FetchOptionType,
  onData: (data: { [key: string]: any }) => void,
  signal?: AbortSignal,
) => {
  const { credential } = useCredentialStore()

  // 创建标准的 Headers 对象
  const headers = new Headers(fetchOptions.headers)
  headers.set('Content-Type', 'application/json')
  headers.set('Connection', 'close') // 强制短连接
  headers.set('Cache-Control', 'no-cache')

  const access_token = credential.access_token
  if (access_token) {
    headers.set('Authorization', `Bearer ${access_token}`)
  }

  const options: RequestInit = {
    ...fetchOptions,
    method: 'POST',
    headers: headers,
    signal: signal, // 必须在这里传入，handleStream 里的 fetch 才会响应 abort()
    body: fetchOptions.body ? JSON.stringify(fetchOptions.body) : undefined,
  }

  const urlWithPrefix = `${apiPrefix}${url.startsWith('/') ? url : `/${url}`}`
  return handleStream(urlWithPrefix, options, onData)
}

async function handleStream(
  urlWithPrefix: string,
  options: RequestInit,
  onData: (data: { [key: string]: any }) => void,
) {
  console.log('before fetch ...')
  const response = await fetch(urlWithPrefix, options)
  console.log('after fetch...')

  if (!response.ok) throw new Error('网络请求失败')

  const reader = response.body?.getReader()
  const decoder = new TextDecoder('utf-8')
  if (!reader) return

  let buffer = ''

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })

      // SSE 标准事件是以两个换行符分隔的
      const parts = buffer.split('\n\n')
      // 最后一部分可能不完整，留到下次处理
      buffer = parts.pop() || ''

      for (const part of parts) {
        if (!part.trim()) continue

        let event = ''
        let data = ''
        const lines = part.split('\n')

        lines.forEach((line) => {
          const trimmed = line.trim()
          if (trimmed.startsWith('event:')) event = trimmed.slice(6).trim()
          else if (trimmed.startsWith('data:')) data = trimmed.slice(5).trim()
        })

        if (event && data) {
          try {
            onData({ event, data: JSON.parse(data) })
          } catch (e) {
            console.error('解析数据失败:', data, e)
          }
        }
      }
    }
  } catch (error: any) {
    if (error.name === 'AbortError') {
      console.log('Fetch aborted by user')
    } else {
      console.error('Stream read error:', error)
      throw error
    }
  } finally {
    // 【核心修改】强制取消读取器，释放浏览器 TCP 连接通道
    await reader.cancel()
    reader.releaseLock()
    console.log('Reader lock and connection released')
  }
}

export const request = <T>(url: string, options = {}) => {
  return baseFetch<T>(url, options)
}

export const get = <T>(url: string, options = {}) => {
  return baseFetch<T>(url, Object.assign({}, options, { method: 'GET' }))
}

export const post = <T>(url: string, options = {}) => {
  return baseFetch<T>(url, Object.assign({}, options, { method: 'POST' }))
}

export const upload = <T>(url: string, options: any = {}): Promise<T> => {
  // 组装请求url
  const urlWithPrefix = `${apiPrefix}${url.startsWith('/') ? url : `/${url}`}`

  // 组装xhr请求配置信息
  const defaultOptions = {
    method: 'POST',
    url: urlWithPrefix,
    headers: {},
    data: {},
  }

  options = {
    ...defaultOptions,
    ...options,
    headers: { ...defaultOptions.headers, ...options.headers },
  }
  const { credential, clear: clearCredential } = useCredentialStore()
  const access_token = credential.access_token
  if (access_token) {
    options.headers['Authorization'] = `Bearer ${access_token}`
  }

  // 构建promise并使用xhr完成文件上传
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()

    xhr.open(options.method, options.url)
    for (const key in options.headers) {
      xhr.setRequestHeader(key, options.headers[key])
    }

    // 设置xhr响应格式并携带授权凭证（例如cookie）
    xhr.withCredentials = true
    xhr.responseType = 'json'

    // 坚挺xhr状态变化并导出数据
    xhr.onreadystatechange = async () => {
      // 判断xhr的状态是不是4，如果为4则代表已经传输完成（涵盖成功与失败）
      if (xhr.readyState === 4) {
        if (xhr.status === 200) {
          // 判断业务状态码是否正常
          const response = xhr.response
          if (response.code === httpCode.success) {
            resolve(xhr.response)
          } else if (response.code === httpCode.unauthorized) {
            clearCredential()
            await router.replace({
              path: '/auth/login',
            })
          }
        } else {
          reject(xhr)
        }
      }
    }

    // 添加xhr进度监听
    xhr.upload.onprogress = options.onprogress

    // 发送请求
    xhr.send(options.data)
  })
}
