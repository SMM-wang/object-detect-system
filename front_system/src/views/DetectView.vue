<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">智能检测</h1>
        <p class="page-subtitle">上传航拍图片或视频，选择模型参数后提交检测</p>
      </div>
      <div class="detect-actions">
        <el-button :disabled="!files.length || !params.modelVersion || detectionStore.detecting" :loading="detectionStore.detecting" type="primary" @click="submitDetection">
          提交检测
        </el-button>
        <el-button v-if="isRealtimeVideoRunning" @click="toggleRealtimePause">{{ isRealtimePaused ? '继续' : '暂停' }}</el-button>
        <el-button v-if="isRealtimeVideoRunning" type="danger" @click="stopRealtimeVideo">终止</el-button>
      </div>
    </div>

    <el-row :gutter="18">
      <el-col :span="8">
        <el-card class="page-card" shadow="never">
          <template #header>上传文件</template>
          <DetectUploadPanel @change="handleFilesChange" />
        </el-card>
        <el-card class="page-card params-card" shadow="never">
          <template #header>检测参数</template>
          <DetectParamsForm :model-value="params" :model-options="detectionStore.modelOptions" @update:model-value="updateParams" />
        </el-card>
      </el-col>
      <el-col :span="16">
        <el-card class="page-card" shadow="never">
          <template #header>
            <div class="result-header">
              <span>检测结果</span>
              <div class="result-selector">
                <el-button size="small" :disabled="!canGoPrevious" @click="selectPrevious">‹</el-button>
                <span class="result-file-name">{{ selectedFileName }}</span>
                <el-button size="small" :disabled="!canGoNext" @click="selectNext">›</el-button>
              </div>
              <el-checkbox v-model="showLabels">显示标签</el-checkbox>
            </div>
          </template>
          <ResultCanvas :image-url="imageUrl" :objects="objects" :image-width="result?.imageWidth" :image-height="result?.imageHeight" :show-labels="showLabels" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="18" class="result-grid">
      <el-col :span="14">
        <el-card class="page-card" shadow="never">
          <template #header>结果摘要</template>
          <DetectionSummary :result="batchImageSummary || result" />
          <el-table v-if="batchImageRows.length" :data="batchImageRows" class="batch-result-table" size="small" border>
            <el-table-column prop="fileName" label="图片名称" min-width="180" show-overflow-tooltip />
            <el-table-column prop="objectCount" label="目标数" width="90" />
            <el-table-column prop="elapsedMs" label="耗时(ms)" width="110" />
            <el-table-column label="类别分布" min-width="180">
              <template #default="{ row }">
                <el-tag v-for="item in row.classes" :key="item.name" class="class-tag">{{ item.name }}：{{ item.count }}</el-tag>
                <span v-if="!row.classes.length">暂无</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="90">
              <template #default="{ row }">
                <el-button link type="primary" @click="selectResult(row.index)">查看</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="10">
        <AiAnalysisPanel :analysis="analysisText" />
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import AiAnalysisPanel from '@/components/detect/AiAnalysisPanel.vue'
import DetectParamsForm from '@/components/detect/DetectParamsForm.vue'
import DetectionSummary from '@/components/detect/DetectionSummary.vue'
import DetectUploadPanel from '@/components/detect/DetectUploadPanel.vue'
import ResultCanvas from '@/components/detect/ResultCanvas.vue'
import { controlVideoStream, streamDetectVideo } from '@/services/detection'
import { useDetectionStore } from '@/stores/detection'
import { getFileType } from '@/utils/upload'

const detectionStore = useDetectionStore()
const files = ref([])
const imageUrl = ref('')
const selectedIndex = ref(0)
const batchResults = ref([])
const showLabels = ref(true)
const isRealtimePaused = ref(false)
const isRealtimeVideoRunning = ref(false)
const realtimeStreamId = ref('')
let realtimeAbortController = null
const params = reactive({
  modelVersion: detectionStore.modelVersion,
  confidence: detectionStore.confidence,
  iou: detectionStore.iou,
  frameInterval: detectionStore.frameInterval
})
const selectedFile = computed(() => files.value[selectedIndex.value] || null)
const selectedBatchItem = computed(() => batchResults.value[selectedIndex.value] || null)
const selectedFileName = computed(() => selectedFile.value?.webkitRelativePath || selectedFile.value?.name || '未选择图片')
const canGoPrevious = computed(() => selectedIndex.value > 0)
const canGoNext = computed(() => selectedIndex.value < files.value.length - 1)
const result = computed(() => selectedBatchItem.value?.result || detectionStore.currentResult)
const objects = computed(() => result.value?.objects || [])
const analysisText = computed(() => result.value?.analysis || result.value?.analysisText || '')
const batchImageRows = computed(() => {
  if (files.value.length <= 1 || files.value.some((file) => getFileType(file) === 'video')) return []
  return batchResults.value
    .map((item, index) => ({
      index,
      fileName: item.file?.webkitRelativePath || item.file?.name || `图片 ${index + 1}`,
      objectCount: item.result?.objects?.length || 0,
      elapsedMs: item.result?.elapsedMs ?? '-',
      classes: getClassItems(item.result?.objects || [])
    }))
    .filter((item) => item.fileName)
})
const batchImageSummary = computed(() => {
  if (!batchImageRows.value.length) return null
  const objects = batchResults.value.flatMap((item) => item.result?.objects || [])
  return {
    recordId: '批量检测',
    elapsedMs: batchResults.value.reduce((sum, item) => sum + Number(item.result?.elapsedMs || 0), 0),
    objectCount: objects.length,
    processedFrames: batchImageRows.value.length,
    objects
  }
})

watch(params, (value) => detectionStore.setParams(value), { deep: true })

function getClassItems(objects) {
  const counts = {}
  objects.forEach((item) => {
    const name = item.className || '目标'
    counts[name] = (counts[name] || 0) + 1
  })
  return Object.entries(counts).map(([name, count]) => ({ name, count }))
}

function updateParams(value) {
  Object.assign(params, value)
  detectionStore.setParams(value)
}

async function loadModels() {
  await detectionStore.loadModels()
  params.modelVersion = detectionStore.modelVersion
}

function revokePreview() {
  if (imageUrl.value?.startsWith('blob:')) URL.revokeObjectURL(imageUrl.value)
  imageUrl.value = ''
}

function updatePreview() {
  revokePreview()
  if (selectedFile.value && getFileType(selectedFile.value) === 'image') {
    imageUrl.value = URL.createObjectURL(selectedFile.value)
  }
}

function handleFilesChange(nextFiles) {
  files.value = nextFiles
  selectedIndex.value = 0
  batchResults.value = []
  detectionStore.setBatchQueue(nextFiles)
  detectionStore.setFile(nextFiles[0] || null)
  updatePreview()
}

function selectPrevious() {
  if (!canGoPrevious.value) return
  selectedIndex.value -= 1
  detectionStore.setFile(selectedFile.value)
  updatePreview()
}

function selectNext() {
  if (!canGoNext.value) return
  selectedIndex.value += 1
  detectionStore.setFile(selectedFile.value)
  updatePreview()
}

function selectResult(index) {
  selectedIndex.value = index
  detectionStore.setFile(selectedFile.value)
  updatePreview()
}

async function toggleRealtimePause() {
  if (!realtimeStreamId.value) return
  const action = isRealtimePaused.value ? 'resume' : 'pause'
  await controlVideoStream(realtimeStreamId.value, action)
  isRealtimePaused.value = !isRealtimePaused.value
}

async function stopRealtimeVideo() {
  if (realtimeStreamId.value) {
    await controlVideoStream(realtimeStreamId.value, 'stop')
  }
  realtimeAbortController?.abort()
  isRealtimeVideoRunning.value = false
  isRealtimePaused.value = false
  realtimeStreamId.value = ''
  detectionStore.detecting = false
}

async function submitRealtimeVideo(file) {
  realtimeAbortController = new AbortController()
  isRealtimeVideoRunning.value = true
  isRealtimePaused.value = false
  detectionStore.detecting = true
  detectionStore.currentResult = null
  batchResults.value = [{ file, result: null }]

  let streamError = null

  try {
    await streamDetectVideo(
      {
        file,
        modelVersion: params.modelVersion,
        confidence: params.confidence,
        iou: params.iou,
        frameInterval: params.frameInterval
      },
      (message) => {
        if (message.type === 'started') {
          realtimeStreamId.value = message.streamId
        }

        if (message.type === 'frame') {
          if (isRealtimePaused.value) return
          const frameResult = {
            imageWidth: message.imageWidth,
            imageHeight: message.imageHeight,
            frameIndex: message.frameIndex,
            frameCount: message.frameCount,
            processedFrames: message.processedFrames,
            objects: message.objects || []
          }
          imageUrl.value = `data:image/jpeg;base64,${message.image}`
          detectionStore.currentResult = frameResult
          batchResults.value[0] = { file, result: frameResult }
        }

        if (message.type === 'done') {
          const doneResult = { ...message, objects: detectionStore.currentResult?.objects || [] }
          detectionStore.currentResult = doneResult
          batchResults.value[0] = { file, result: doneResult }
        }

        if (message.type === 'error') {
          streamError = new Error(message.msg || '视频实时检测失败')
        }
      },
      realtimeAbortController.signal
    )
    if (streamError) throw streamError
  } catch (error) {
    if (error.name !== 'AbortError') throw error
  } finally {
    isRealtimeVideoRunning.value = false
    isRealtimePaused.value = false
    realtimeStreamId.value = ''
    realtimeAbortController = null
    detectionStore.detecting = false
  }
}

async function submitDetection() {
  if (!files.value.length) {
    ElMessage.warning('请先选择待检测文件')
    return
  }

  if (files.value.length === 1 && getFileType(files.value[0]) === 'video') {
    selectedIndex.value = 0
    detectionStore.setFile(files.value[0])
    await submitRealtimeVideo(files.value[0])
  } else if (files.value.length === 1) {
    const singleResult = await detectionStore.submitDetection(files.value[0])
    batchResults.value = [{ file: files.value[0], result: singleResult }]
    selectedIndex.value = 0
    detectionStore.setFile(selectedFile.value)
    updatePreview()
  } else {
    batchResults.value = await detectionStore.runBatchQueue()
    selectedIndex.value = 0
    detectionStore.setFile(selectedFile.value)
    updatePreview()
  }

  ElMessage.success('检测任务已完成')
}

onMounted(loadModels)
onBeforeUnmount(() => {
  if (realtimeStreamId.value) controlVideoStream(realtimeStreamId.value, 'stop')
  realtimeAbortController?.abort()
  revokePreview()
})
</script>

<style scoped>
.detect-actions {
  display: flex;
  gap: 10px;
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.result-selector {
  display: flex;
  min-width: 0;
  flex: 1;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.result-file-name {
  max-width: 360px;
  overflow: hidden;
  color: var(--app-muted);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.batch-result-table {
  margin-top: 18px;
}

.class-tag {
  margin: 0 6px 6px 0;
}

.params-card,
.result-grid {
  margin-top: 18px;
}
</style>
