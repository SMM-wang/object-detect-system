import http from './http'

export function loginApi(payload) {
  return http.post('/auth/login', payload)
}
