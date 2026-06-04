<template>
  <div class="state-page">
    <el-result icon="error" title="404" sub-title="页面不存在">
      <template #extra>
        <el-button type="primary" @click="$router.replace('/dashboard')">返回工作台</el-button>
      </template>
    </el-result>
  </div>
</template>

<style scoped>
.state-page {
  display: grid;
  min-height: 100vh;
  place-items: center;
  background: var(--app-bg);
}
</style>
