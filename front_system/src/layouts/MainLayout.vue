<template>
  <el-container class="main-layout">
    <el-aside width="236px" class="layout-aside">
      <AppSidebar />
    </el-aside>
    <el-container>
      <el-header class="layout-header">
        <AppHeader />
      </el-header>
      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import AppHeader from '@/components/layout/AppHeader.vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
}

.layout-aside {
  color: #fff;
  background: var(--app-sidebar);
}

.layout-header {
  height: 64px;
  padding: 0 24px;
  background: #fff;
  border-bottom: 1px solid var(--app-border);
}

.layout-main {
  padding: 24px;
  background: var(--app-bg);
}
</style>
