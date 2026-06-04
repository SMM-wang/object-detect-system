import http from './http'

export function getStatisticsSummary(params) {
  return http.get('/statistics/summary', { params })
}
