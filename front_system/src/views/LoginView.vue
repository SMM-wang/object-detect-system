<template>
  <div class="login-page">
    <el-card class="login-card">
      <div class="login-title">
        <h1>航拍图像智能检测系统</h1>
        <p>登录后进入检测工作台</p>
      </div>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @keyup.enter="submit">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" size="large" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" size="large" show-password />
        </el-form-item>
        <el-button type="primary" size="large" class="login-button" :loading="loading" @click="submit">登录</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)
const form = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function submit() {
  await formRef.value.validate()
  loading.value = true
  try {
    await userStore.login(form)
    ElMessage.success('登录成功')
    router.replace(route.query.redirect || '/dashboard')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: grid;
  min-height: 100vh;
  place-items: center;
  background:
    radial-gradient(circle at 20% 20%, rgb(47 111 237 / 20%), transparent 30%),
    linear-gradient(135deg, #0f172a, #1e3a8a);
}

.login-card {
  width: 420px;
  border: 0;
  border-radius: 18px;
}

.login-title {
  margin-bottom: 28px;
  text-align: center;
}

.login-title h1 {
  margin: 0;
  font-size: 26px;
}

.login-title p {
  color: var(--app-muted);
}

.login-button {
  width: 100%;
}
</style>
