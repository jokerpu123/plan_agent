<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2>计划安排系统</h2>
      <el-form :model="loginForm" label-width="80px" @submit.prevent="login">
        <el-form-item label="邮箱">
          <el-input v-model="loginForm.email" type="email" placeholder="请输入登录邮箱"></el-input>
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="login">登录</el-button>
          <el-button type="text" @click="register">注册</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const loginForm = ref({
  email: '',
  password: ''
})

// 登录方法
const login = async () => {
  if (!loginForm.value.email?.trim() || !loginForm.value.password) {
    ElMessage.warning('请填写邮箱和密码')
    return
  }
  try {
    const res = await axios.post('/api/login', {
      email: loginForm.value.email.trim(),
      password: loginForm.value.password
    })
    if (res.data) {
      localStorage.setItem('user', JSON.stringify({ id: res.data.id, email: res.data.email }))
      ElMessage.success('登录成功')
      router.push('/plan')
    }
  } catch (err) {
    ElMessage.error('登录失败：' + (err.response?.data || err.message))
  }
}

const register = async () => {
  if (!loginForm.value.email?.trim() || !loginForm.value.password) {
    ElMessage.warning('请填写邮箱和密码')
    return
  }
  try {
    await axios.post('/api/register', {
      email: loginForm.value.email.trim(),
      password: loginForm.value.password
    })
    ElMessage.success('注册成功，请登录')
  } catch (err) {
    ElMessage.error('注册失败：' + (err.response?.data || err.message))
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f5f5;
}
.login-card {
  width: 400px;
  padding: 20px;
}
</style>