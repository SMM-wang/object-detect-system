import { TOKEN_KEY } from '@/utils/storage'
import http from './http'

function buildDetectionForm({ file, modelVersion, confidence, iou, frameInterval }) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('modelVersion', modelVersion)
  formData.append('confidence', confidence)
  formData.append('iou', iou)
  if (frameInterval) formData.append('frameInterval', frameInterval)
  return formData
}

export function getDetectionModels() {
  return http.get('/detect/models')
}

export function detectImage(payload) {
  return http.post('/detect/image', buildDetectionForm(payload), {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function detectVideo(payload) {
  return http.post('/detect/video', buildDetectionForm(payload), {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function controlVideoStream(streamId, action) {
  return http.post(`/detect/video/stream/${streamId}/control`, { action })
}

export async function streamDetectVideo(payload, onMessage, signal) {
  const token = localStorage.getItem(TOKEN_KEY)
  const response = await fetch('/api/v1/detect/video/stream', {
    method: 'POST',
    headers: token ? { Authorization: `Bearer ${JSON.parse(token)}` } : {},
    body: buildDetectionForm(payload),
    signal
  })

  if (!response.ok || !response.body) {
    throw new Error('视频实时检测请求失败')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''

    for (const line of lines) {
      if (line.trim()) onMessage(JSON.parse(line))
    }
  }

  if (buffer.trim()) onMessage(JSON.parse(buffer))
}
