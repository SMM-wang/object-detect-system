<template>
  <el-card class="chart-card" shadow="never">
    <template #header>{{ title }}</template>
    <div ref="chartRef" class="chart" />
  </el-card>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useECharts } from '@/composables/useECharts'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  options: {
    type: Object,
    required: true
  }
})

const chartRef = ref(null)
const { setOptions } = useECharts(chartRef)

onMounted(() => setOptions(props.options))
watch(() => props.options, (options) => setOptions(options), { deep: true })
</script>

<style scoped>
.chart-card {
  height: 360px;
}

.chart {
  width: 100%;
  height: 280px;
}
</style>
