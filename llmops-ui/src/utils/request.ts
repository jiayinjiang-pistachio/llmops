// 1. 接口超时100s
// 2. 不需要写api前缀，比如http://localhost:5000
// 3. 经常使用get、post，需要对这两个方法进行封装
// 4. 每次获取数据都要使用response.json()才可以获取数据，需要封装

import { apiPrefix } from '@/config';

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
  body?: BodyInit | Record<string, unknown> | null;
  params?: Record<string, unknown>
}

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
      }, TIME_OUT);
    }),
    // 发起一个正常请求
    new Promise((resolve, reject) => {
      globalThis.fetch(urlWithPrefix, options as RequestInit).then((res) => {
        resolve(res.json())
      }).catch(err => {
        reject(err)
      })
    })
  ]) as Promise<T>
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
