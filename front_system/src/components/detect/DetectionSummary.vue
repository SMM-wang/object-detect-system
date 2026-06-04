<template>
  <el-descriptions v-if="result" :column="2" border>
    <el-descriptions-item label="记录编号">{{ result.recordId || '-' }}</el-descriptions-item>
    <el-descriptions-item label="耗时">{{ result.elapsedMs ?? '-' }} ms</el-descriptions-item>
    <el-descriptions-item label="目标数量">{{ objectCount }}</el-descriptions-item>
    <el-descriptions-item label="当前帧" v-if="result.frameIndex !== undefined">{{ result.frameIndex }} / {{ result.frameCount || '-' }}</el-descriptions-item>
    <el-descriptions-item label="处理帧数">{{ result.processedFrames ?? '-' }}</el-descriptions-item>
    <el-descriptions-item label="图像尺寸" v-if="result.imageWidth || result.imageHeight">
      {{ result.imageWidth || '-' }} × {{ result.imageHeight || '-' }}
    </el-descriptions-item>
    <el-descriptions-item label="类别分布" :span="2">
      <el-tag v-for="item in classItems" :key="item.name" class="class-tag">{{ item.name }}：{{ item.count }}</el-tag>
      <span v-if="!classItems.length">暂无类别统计</span>
    </el-descriptions-item>
  </el-descriptions>
  <el-empty v-else description="暂无检测结果" />
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  result: {
    type: Object,
    default: null
  }
})

const objectCount = computed(() => props.result?.objects?.length || props.result?.summary?.totalObjects || props.result?.objectCount || 0)
const classItems = computed(() => {
  const classes = props.result?.summary?.classes
  if (Array.isArray(classes)) return classes.map((item) => ({ name: item.className || item.name, count: item.count }))
  if (classes && typeof classes === 'object') return Object.entries(classes).map(([name, count]) => ({ name, count }))

  const counts = {}
  ;(props.result?.objects || []).forEach((item) => {
    const name = item.className || '目标'
    counts[name] = (counts[name] || 0) + 1
  })
  return Object.entries(counts).map(([name, count]) => ({ name, count }))
})
</script>

<style scoped>
.class-tag {
  margin: 0 8px 8px 0;
}
</style>
