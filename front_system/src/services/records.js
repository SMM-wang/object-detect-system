import http from './http'

export function getRecords(params) {
  return http.get('/records', { params })
}

export function getRecordDetail(id) {
  return http.get(`/records/${id}`)
}
