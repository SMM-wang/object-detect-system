<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">工作台</h1>
        <p class="page-subtitle">查看检测概览并快速进入核心流程</p>
      </div>
      <el-button type="primary" @click="$router.push('/detect')">开始检测</el-button>
    </div>

    <StatCards :summary="summary" />

    <el-row :gutter="18" class="dashboard-grid">
      <el-col :span="10">
        <el-card class="page-card" shadow="never">
          <template #header>快捷入口</template>
          <div class="quick-actions">
            <el-button type="primary" @click="$router.push('/detect')">上传检测</el-button>
            <el-button @click="$router.push('/records')">查看记录</el-button>
            <el-button v-if="userStore.isAdmin" @click="$router.push('/statistics')">统计分析</el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="14">
        <el-card class="page-card" shadow="never">
          <template #header>最近检测记录</template>
          <RecordsTable :records="records" :loading="loading" @detail="openRecord" />
        </el-card>
      </el-col>
    </el-row>

    <RecordDetailDrawer v-model="drawerVisible" :record-id="selectedId" />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import StatCards from '@/components/statistics/StatCards.vue'
import RecordsTable from '@/components/records/RecordsTable.vue'
import RecordDetailDrawer from '@/components/records/RecordDetailDrawer.vue'
import { getRecords } from '@/services/records'
import { getStatisticsSummary } from '@/services/statistics'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const summary = ref({})
const records = ref([])
const loading = ref(false)
const drawerVisible = ref(false)
const selectedId = ref('')

function normalizeList(data) {
  return data?.records || data?.list || data?.items || []
}

function openRecord(row) {
  selectedId.value = row.id || row.recordId
  drawerVisible.value = true
}

onMounted(async () => {
  loading.value = true
  try {
    const [summaryData, recordsData] = await Promise.all([
      getStatisticsSummary({}),
      getRecords({ page: 1, pageSize: 5 })
    ])
    summary.value = summaryData || {}
    records.value = normalizeList(recordsData)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.dashboard-grid {
  margin-top: 18px;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.quick-actions .el-button {
  margin-left: 0;
}
</style>
