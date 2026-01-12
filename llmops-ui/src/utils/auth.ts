import storage from './storage'

export default {
  isLogin: () => {
    // 从localStorage中查找授权信息
    const credential = storage.get('credential')
    const now = Math.floor(Date.now() / 1000)

    // 判断授权凭证是否存在access_token，并判断access_token是否过期
    if(!credential || !credential.access_token || !credential.expire_at || credential.expire_at < now) {
      // 账号未登录，需移除LocalStorage中的数据，涵盖用户数据+授权凭证
      storage.clear()
      return false
    }
    
    return true
  }
}
