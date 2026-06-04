<template>
  <el-drawer :model-value="modelValue" title="检测记录详情" size="46%" @close="$emit('update:modelValue', false)">
    <div v-loading="loading">
      <el-empty v-if="!detail" description="请选择记录" />
      <template v-else>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="文件名">{{ detail.fileName || '-' }}</el-descriptions-item>
          <el-descriptions-item label="文件类型">{{ detail.fileType || '-' }}</el-descriptions-item>
          <el-descriptions-item label="模型版本">{{ detail.modelVersion || '-' }}</el-descriptions-item>
          <el-descriptions-item label="置信度">{{ detail.confidence ?? '-' }}</el-descriptions-item>
          <el-descriptions-item label="IoU">{{ detail.iou ?? '-' }}</el-descriptions-item>
          <el-descriptions-item label="耗时">{{ detail.elapsedMs ?? '-' }} ms</el-descriptions-item>
          <el-descriptions-item label="目标数量">{{ detail.objectCount ?? objects.length }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ STATUS_LABELS[detail.status] || detail.status || '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">{{ detail.createdAt || '-' }}</el-descriptions-item>
        </el-descriptions>

        <div v-if="previewUrl" class="detail-preview">
          <ResultCanvas :image-url="previewUrl" :objects="objects" :image-width="detail.imageWidth" :image-height="detail.imageHeight" />
        </div>

        <el-card class="detail-section" shadow="never">
          <template #header>AI 研判</template>
          <div class="analysis-text">{{ detail.analysisText || detail.analysis || '暂无 AI 研判内容' }}</div>
        </el-card>

        <el-card class="detail-section" shadow="never">
          <template #header>结果 JSON</template>
          <pre>{{ prettyResult }}</pre>
        </el-card>
      </template>
    </div>
  </el-drawer>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { getRecordDetail } from '@/services/records'
import { STATUS_LABELS } from '@/constants'
import ResultCanvas from '@/components/detect/ResultCanvas.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  recordId: {
    type: [String, Number],
    default: ''
  }
})
const emit = defineEmits(['update:modelValue'])
const loading = ref(false)
const detail = ref(null)

const resultJson = computed(() => {
  const value = detail.value?.resultJson || detail.value?.result || detail.value
  if (typeof value === 'string') {
    try {
      return JSON.parse(value)
    } catch {
      return value
    }
  }
  return value || {}
})
const objects = computed(() => resultJson.value?.objects || detail.value?.objects || [])
const previewUrl = computed(() => detail.value?.imageUrl || detail.value?.originUrl || detail.value?.fileUrl || '')
const prettyResult = computed(() => JSON.stringify(resultJson.value, null, 2))

async function loadDetail() {
  if (!props.recordId || !props.modelValue) return
  loading.value = true
  try {
    detail.value = await getRecordDetail(props.recordId)
  } finally {
    loading.value = false
  }
}

watch(() => [props.recordId, props.modelValue], loadDetail)
</script>

<style scoped>
.detail-preview,
.detail-section {
  margin-top: 18px;
}

.analysis-text {
  line-height: 1.8;
  white-space: pre-wrap;
}

pre {
  max-height: 280px;
  padding: 12px;
  overflow: auto;
  background: #f8fafc;
  border-radius: 8px;
}
</style>
