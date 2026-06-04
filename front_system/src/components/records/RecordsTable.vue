<template>
  <el-table :data="records" v-loading="loading" stripe>
    <el-table-column prop="id" label="ID" width="90" />
    <el-table-column prop="fileName" label="文件名" min-width="180" show-overflow-tooltip />
    <el-table-column prop="fileType" label="类型" width="90" />
    <el-table-column prop="modelVersion" label="模型版本" min-width="140" />
    <el-table-column prop="objectCount" label="目标数" width="90" />
    <el-table-column prop="elapsedMs" label="耗时(ms)" width="110" />
    <el-table-column prop="status" label="状态" width="100">
      <template #default="{ row }">
        <el-tag :type="STATUS_TAG_TYPES[row.status] || 'info'">{{ STATUS_LABELS[row.status] || row.status }}</el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="createdAt" label="创建时间" min-width="170" />
    <el-table-column label="操作" width="100" fixed="right">
      <template #default="{ row }">
        <el-button link type="primary" @click="$emit('detail', row)">详情</el-button>
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup>
import { STATUS_LABELS, STATUS_TAG_TYPES } from '@/constants'

defineProps({
  records: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['detail'])
</script>
