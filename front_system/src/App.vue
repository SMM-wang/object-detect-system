<template>
  <el-config-provider namespace="el">
    <router-view />
    <div v-if="appStore.isLoading" class="global-loading-mask">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>处理中...</span>
    </div>
  </el-config-provider>
</template>

<script setup>
import { Loading } from '@element-plus/icons-vue'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()
</script>
