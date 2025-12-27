// api接口前缀
export const apiPrefix = 'http://127.0.0.1:5000'

// 业务状态码
export const httpCode = {
  success: 'success',
  fail: 'fail',
  notFound: 'not_found',
  unauthorized: 'unauthorized',
  forbidden: 'forbidden',
  validateError: 'validate_error',
}

// 类型字符串与中文映射
export const typeMap: Record<string, string> = {
  int: '整型',
  float: '浮点型',
  str: '字符串',
  bool: '布尔值',
}
