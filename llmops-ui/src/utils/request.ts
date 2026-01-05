// 1. 接口超时100s
// 2. 不需要写api前缀，比如http://localhost:5000
// 3. 经常使用get、post，需要对这两个方法进行封装
// 4. 每次获取数据都要使用response.json()才可以获取数据，需要封装

import { apiPrefix, httpCode } from '@/config'
import { Message } from '@arco-design/web-vue'

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

// 封装基于post的sse（流式事件响应）请求
export const ssePost = async (
  url: string,
  fetchOptions: FetchOptionType,
  onData: (data: { [key: string]: any }) => void,
) => {
  // 组装基础的fetch请求配置
  const options = Object.assign({}, baseFetchOptions, { method: 'POST' }, fetchOptions)

  // 组装请求URL
  const urlWithPrefix = `${apiPrefix}${url.startsWith('/') ? url : `/${url}`}`

  const { body } = fetchOptions
  // debugger
  if (body) {
    options.body = JSON.stringify(body)
    const response = await fetch(urlWithPrefix, options as RequestInit)
    return handleStream(response, onData)
  }
}

function handleStream(response: Response, onData: (data: { [key: string]: any }) => void) {
  // 1. 检测网络请求是否正常
  if (!response.ok) {
    throw new Error('网络请求失败')
  }

  // 构建reader及decoder
  const reader = response.body?.getReader()
  const decoder = new TextDecoder('utf-8')

  let buffer = ''

  // 3. 构建read函数用于去读取数据
  const read = () => {
    let hasError = false
    reader?.read().then((result: any) => {
      if (result.done) return

      buffer += decoder.decode(result.value, { stream: true })
      const lines = buffer.split('\n')

      let event = ''
      let data = ''

      try {
        lines.forEach((line) => {
          line = line.trim()
          if (line.startsWith('event:')) {
            event = line.slice(6).trim()
          } else if (line.startsWith('data:')) {
            data = line.slice(5).trim()
          }

          if (line === '') {
            if (event !== '' && data !== '') {
              onData({
                event: event,
                data: JSON.parse(data),
              })
              event = ''
              data = ''
            }
          }
        })
        buffer = lines.pop() || ''
      } catch (e) {
        hasError = true
        console.log(e)
      }

      if (!hasError) {
        read()
      }
    })
  }

  // 4. 调用read函数去执行对应的数据
  read()
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
