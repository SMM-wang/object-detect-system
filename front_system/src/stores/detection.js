import { defineStore } from 'pinia'
import { detectImage, detectVideo, getDetectionModels } from '@/services/detection'
import { getFileType } from '@/utils/upload'

export const useDetectionStore = defineStore('detection', {
  state: () => ({
    modelVersion: '',
    modelOptions: [],
    confidence: 0.25,
    iou: 0.3,
    frameInterval: 5,
    currentFile: null,
    currentResult: null,
    batchQueue: [],
    detecting: false
  }),
  getters: {
    objectCount: (state) => state.currentResult?.objects?.length || state.currentResult?.summary?.totalObjects || 0
  },
  actions: {
    setParams(params) {
      Object.assign(this, params)
    },
    setFile(file) {
      this.currentFile = file
      this.currentResult = null
    },
    setBatchQueue(files) {
      this.batchQueue = files
    },
    resetResult() {
      this.currentResult = null
    },
    async loadModels() {
      const models = await getDetectionModels()
      this.modelOptions = models || []
      if (!this.modelOptions.some((item) => item.value === this.modelVersion)) {
        this.modelVersion = this.modelOptions[0]?.value || ''
      }
      return this.modelOptions
    },
    async submitDetection(file = this.currentFile) {
      if (!file) return null

      this.detecting = true
      try {
        const payload = {
          file,
          modelVersion: this.modelVersion,
          confidence: this.confidence,
          iou: this.iou,
          frameInterval: this.frameInterval
        }
        const result = getFileType(file) === 'video' ? await detectVideo(payload) : await detectImage(payload)
        this.currentResult = result
        return result
      } finally {
        this.detecting = false
      }
    },
    async runBatchQueue() {
      const results = []
      for (const file of this.batchQueue) {
        this.currentFile = file
        const result = await this.submitDetection(file)
        results.push({ file, result })
      }
      return results
    }
  }
})
