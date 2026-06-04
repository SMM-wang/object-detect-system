<template>
  <el-card class="analysis-card" shadow="never">
    <template #header>AI 研判</template>
    <div v-if="displayText" class="analysis-text">{{ displayText }}</div>
    <el-empty v-else description="暂无 AI 研判内容" />
  </el-card>
</template>

<script setup>
import { toRef } from 'vue'
import { useTypewriter } from '@/composables/useTypewriter'

const props = defineProps({
  analysis: {
    type: String,
    default: ''
  }
})

const { displayText } = useTypewriter(toRef(props, 'analysis'))
</script>

<style scoped>
.analysis-card {
  height: 100%;
}

.analysis-text {
  min-height: 120px;
  color: #334155;
  line-height: 1.8;
  white-space: pre-wrap;
}
</style>
