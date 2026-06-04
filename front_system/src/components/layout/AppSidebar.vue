<template>
  <div class="sidebar">
    <div class="brand">
      <div class="brand-mark">AI</div>
      <div>
        <strong>航拍检测</strong>
        <span>智能分析平台</span>
      </div>
    </div>

    <el-menu :default-active="route.path" router background-color="transparent" text-color="#b9c4d6" active-text-color="#fff">
      <el-menu-item v-for="item in menus" :key="item.path" :index="item.path">
        <el-icon><component :is="item.icon" /></el-icon>
        <span>{{ item.title }}</span>
      </el-menu-item>
    </el-menu>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { mainRoutes } from '@/router'
import { useUserStore } from '@/stores/user'
import { filterMenuRoutes } from '@/utils/permission'

const route = useRoute()
const userStore = useUserStore()
const menus = computed(() => filterMenuRoutes(mainRoutes, userStore.role))
</script>

<style scoped>
.sidebar {
  min-height: 100vh;
  padding: 18px 12px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 10px 24px;
}

.brand-mark {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  font-weight: 800;
  color: #fff;
  background: linear-gradient(135deg, #2f6fed, #00a2ae);
  border-radius: 12px;
}

.brand strong,
.brand span {
  display: block;
}

.brand span {
  margin-top: 4px;
  color: #94a3b8;
  font-size: 12px;
}

:deep(.el-menu) {
  border-right: 0;
}

:deep(.el-menu-item) {
  margin: 4px 0;
  border-radius: 10px;
}

:deep(.el-menu-item.is-active) {
  background: var(--app-sidebar-active);
}
</style>
