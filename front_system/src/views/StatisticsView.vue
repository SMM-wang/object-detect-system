<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">统计分析</h1>
        <p class="page-subtitle">从后端聚合接口查看检测总量、类别分布、耗时趋势和模型使用情况</p>
      </div>
      <el-date-picker
        v-model="timeRange"
        type="datetimerange"
        start-placeholder="开始时间"
        end-placeholder="结束时间"
        value-format="YYYY-MM-DD HH:mm:ss"
        @change="loadSummary"
      />
    </div>

    <div v-loading="loading">
      <StatCards :summary="summary" />
      <el-row :gutter="18" class="chart-grid">
        <el-col :span="8">
          <EChartCard title="类别分布" :options="classOptions" />
        </el-col>
        <el-col :span="8">
          <EChartCard title="耗时趋势" :options="elapsedOptions" />
        </el-col>
        <el-col :span="8">
          <EChartCard title="模型使用" :options="modelOptions" />
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import EChartCard from '@/components/statistics/EChartCard.vue'
import StatCards from '@/components/statistics/StatCards.vue'
import { getStatisticsSummary } from '@/services/statistics'

const loading = ref(false)
const summary = ref({})
const timeRange = ref([])

function toEntries(value) {
  if (Array.isArray(value)) return value.map((item) => ({ name: item.name || item.className || item.modelVersion || item.date, value: item.count || item.value || item.elapsedMs || 0 }))
  if (value && typeof value === 'object') return Object.entries(value).map(([name, value]) => ({ name, value }))
  return []
}

const classOptions = computed(() => ({
  tooltip: { trigger: 'item' },
  series: [{ type: 'pie', radius: ['42%', '70%'], data: toEntries(summary.value.classDistribution || summary.value.classes) }]
}))

const elapsedOptions = computed(() => {
  const data = toEntries(summary.value.elapsedTrend || summary.value.elapsed)
  return {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: data.map((item) => item.name) },
    yAxis: { type: 'value' },
    series: [{ type: 'line', smooth: true, data: data.map((item) => item.value) }]
  }
})

const modelOptions = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: toEntries(summary.value.modelUsage || summary.value.models).map((item) => item.name) },
  yAxis: { type: 'value' },
  series: [{ type: 'bar', data: toEntries(summary.value.modelUsage || summary.value.models).map((item) => item.value) }]
}))

async function loadSummary() {
  loading.value = true
  try {
    summary.value = await getStatisticsSummary({
      startTime: timeRange.value?.[0] || '',
      endTime: timeRange.value?.[1] || ''
    })
  } finally {
    loading.value = false
  }
}

onMounted(loadSummary)
</script>

<style scoped>
.chart-grid {
  margin-top: 18px;
}
</style>
