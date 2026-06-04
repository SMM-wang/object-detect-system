<template>
  <el-row :gutter="16">
    <el-col v-for="item in cards" :key="item.label" :span="6">
      <el-card class="stat-card" shadow="never">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  summary: {
    type: Object,
    default: () => ({})
  }
})

const cards = computed(() => [
  { label: '检测总数', value: props.summary.totalRecords ?? props.summary.total ?? 0 },
  { label: '成功记录', value: props.summary.successRecords ?? props.summary.success ?? 0 },
  { label: '失败记录', value: props.summary.failedRecords ?? props.summary.failed ?? 0 },
  { label: '平均耗时(ms)', value: props.summary.avgElapsedMs ?? props.summary.averageElapsedMs ?? 0 }
])
</script>

<style scoped>
.stat-card span,
.stat-card strong {
  display: block;
}

.stat-card span {
  color: var(--app-muted);
}

.stat-card strong {
  margin-top: 12px;
  font-size: 28px;
}
</style>
