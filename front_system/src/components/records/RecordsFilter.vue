<template>
  <el-form :inline="true" :model="filters" class="records-filter">
    <el-form-item label="时间范围">
      <el-date-picker
        v-model="filters.timeRange"
        type="datetimerange"
        start-placeholder="开始时间"
        end-placeholder="结束时间"
        value-format="YYYY-MM-DD HH:mm:ss"
      />
    </el-form-item>
    <el-form-item label="类别">
      <el-input v-model="filters.className" placeholder="目标类别" clearable />
    </el-form-item>
    <el-form-item label="模型">
      <el-select v-model="filters.modelVersion" placeholder="全部模型" clearable style="width: 180px">
        <el-option v-for="item in modelOptions" :key="item.value" :label="item.label" :value="item.value" />
      </el-select>
    </el-form-item>
    <el-form-item label="状态">
      <el-select v-model="filters.status" placeholder="全部状态" clearable style="width: 140px">
        <el-option v-for="(label, value) in STATUS_LABELS" :key="value" :label="label" :value="value" />
      </el-select>
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="emitSearch">查询</el-button>
      <el-button @click="reset">重置</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { reactive } from 'vue'
import { STATUS_LABELS } from '@/constants'

defineProps({
  modelOptions: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['search'])
const filters = reactive({
  timeRange: [],
  className: '',
  modelVersion: '',
  status: ''
})

function buildParams() {
  return {
    startTime: filters.timeRange?.[0] || '',
    endTime: filters.timeRange?.[1] || '',
    className: filters.className,
    modelVersion: filters.modelVersion,
    status: filters.status
  }
}

function emitSearch() {
  emit('search', buildParams())
}

function reset() {
  filters.timeRange = []
  filters.className = ''
  filters.modelVersion = ''
  filters.status = ''
  emitSearch()
}
</script>

<style scoped>
.records-filter {
  padding: 18px 18px 0;
  margin-bottom: 18px;
  background: #fff;
  border-radius: 12px;
}
</style>
