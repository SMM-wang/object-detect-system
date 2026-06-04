<template>
  <div class="header-bar">
    <div>
      <strong>{{ currentTitle }}</strong>
      <span>基于深度学习的航拍图像目标检测与研判</span>
    </div>
    <div class="header-user">
      <el-tag>{{ roleLabel }}</el-tag>
      <span>{{ userStore.displayName }}</span>
      <el-button text type="primary" @click="handleLogout">退出登录</el-button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ROLE_LABELS } from '@/constants'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const currentTitle = computed(() => route.meta.title || '航拍图像智能检测系统')
const roleLabel = computed(() => ROLE_LABELS[userStore.role] || '用户')

function handleLogout() {
  userStore.logout()
  router.replace('/login')
}
</script>

<style scoped>
.header-bar {
  display: flex;
  height: 100%;
  align-items: center;
  justify-content: space-between;
}

.header-bar strong,
.header-bar span {
  display: block;
}

.header-bar span {
  margin-top: 4px;
  color: var(--app-muted);
  font-size: 13px;
}

.header-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-user span {
  margin: 0;
  color: var(--app-text);
}
</style>
