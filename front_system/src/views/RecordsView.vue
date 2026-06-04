<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">检测记录</h1>
        <p class="page-subtitle">按时间、类别、模型和状态筛选历史检测任务</p>
      </div>
    </div>

    <RecordsFilter :model-options="detectionStore.modelOptions" @search="handleSearch" />

    <el-card class="page-card" shadow="never">
      <RecordsTable :records="records" :loading="loading" @detail="openDetail" />
      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          background
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
          @change="loadRecords"
        />
      </div>
    </el-card>

    <RecordDetailDrawer v-model="drawerVisible" :record-id="selectedId" />
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import RecordDetailDrawer from '@/components/records/RecordDetailDrawer.vue'
import RecordsFilter from '@/components/records/RecordsFilter.vue'
import RecordsTable from '@/components/records/RecordsTable.vue'
import { getRecords } from '@/services/records'
import { useDetectionStore } from '@/stores/detection'

const detectionStore = useDetectionStore()
const records = ref([])
const loading = ref(false)
const query = reactive({})
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })
const drawerVisible = ref(false)
const selectedId = ref('')

function normalizeRecords(data) {
  records.value = data?.records || data?.list || data?.items || []
  pagination.total = data?.total || data?.totalCount || records.value.length
}

async function loadRecords() {
  loading.value = true
  try {
    const data = await getRecords({ ...query, page: pagination.page, pageSize: pagination.pageSize })
    normalizeRecords(data)
  } finally {
    loading.value = false
  }
}

function handleSearch(params) {
  Object.assign(query, params)
  pagination.page = 1
  loadRecords()
}

function openDetail(row) {
  selectedId.value = row.id || row.recordId
  drawerVisible.value = true
}

onMounted(() => {
  detectionStore.loadModels()
  loadRecords()
})
</script>

<style scoped>
.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}
</style>
