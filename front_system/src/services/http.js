import axios from 'axios'
import { ElMessage } from 'element-plus'
import { removeStorageItem, TOKEN_KEY, USER_KEY } from '@/utils/storage'

const http = axios.create({
  baseURL: '/api/v1',
  timeout: 120000
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${JSON.parse(token)}`
  }
  return config
})

http.interceptors.response.use(
  (response) => {
    const body = response.data
    if (!body || typeof body !== 'object' || !('code' in body)) return body

    if (body.code === 0 || body.code === 200) return body.data

    const error = new Error(body.msg || '请求失败')
    error.code = body.code
    throw error
  },
  (error) => Promise.reject(error)
)

http.interceptors.response.use(undefined, (error) => {
  const status = error.response?.status || error.code
  const message = error.response?.data?.msg || error.message || '请求失败'

  if (status === 401) {
    removeStorageItem(TOKEN_KEY)
    removeStorageItem(USER_KEY)
    ElMessage.error('登录状态已失效，请重新登录')
    if (window.location.pathname !== '/login') window.location.href = '/login'
  } else if (status === 403) {
    ElMessage.error('没有权限访问该资源')
  } else if (status === 503) {
    ElMessage.error('检测服务繁忙，请稍后重试')
  } else if (status === 500) {
    ElMessage.error('服务器异常，请稍后重试')
  } else if (message) {
    ElMessage.error(message)
  }

  return Promise.reject(error)
})

export default http
