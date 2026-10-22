<template>
  <el-container class="main-layout">
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <span class="logo-icon">📅</span>
        <span>计划系统</span>
      </div>
      <nav class="nav-menu">
        <router-link to="/plan" class="nav-item" active-class="active">
          <span class="nav-icon">📋</span>
          <span>每日规划</span>
        </router-link>
        <router-link to="/weekly" class="nav-item" active-class="active">
          <span class="nav-icon">🗓️</span>
          <span>每周规划</span>
        </router-link>
        <router-link to="/recurring" class="nav-item" active-class="active">
          <span class="nav-icon">🔁</span>
          <span>重复任务</span>
        </router-link>
        <router-link to="/focus" class="nav-item" active-class="active">
          <span class="nav-icon">⏱️</span>
          <span>专注计时</span>
        </router-link>
        <router-link to="/statistics" class="nav-item" active-class="active">
          <span class="nav-icon">📊</span>
          <span>复盘统计</span>
        </router-link>
      </nav>
    </el-aside>

    <el-container class="main-area">
      <el-header class="top-header">
        <span class="page-title">{{ pageTitle }}</span>
        <div class="header-right">
          <span class="user-info">{{ userEmail }}</span>
          <el-button size="small" @click="logout">退出登录</el-button>
        </div>
      </el-header>
      <el-main class="content-main">
        <router-view />
      </el-main>
    </el-container>
    <AiChatPanel />
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AiChatPanel from '../components/AiChatPanel.vue'

const router = useRouter()
const route = useRoute()

const pageTitle = computed(() => route.meta.title || '计划系统')

const userEmail = computed(() => {
  try {
    const user = JSON.parse(localStorage.getItem('user'))
    return user?.email ?? ''
  } catch {
    return ''
  }
})

const logout = () => {
  localStorage.removeItem('user')
  router.push('/login')
}
</script>

<style scoped>
.main-layout {
  height: 100vh;
  background: #f0f2f5;
}

.sidebar {
  background: linear-gradient(180deg, #e8dff5 0%, #d9ccf0 100%);
  color: #5c4d72;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(140, 120, 180, 0.12);
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 24px 20px;
  font-size: 18px;
  font-weight: 600;
  color: #6b5b8a;
  border-bottom: 1px solid rgba(140, 120, 180, 0.2);
}

.logo-icon {
  font-size: 24px;
}

.nav-menu {
  padding: 16px 12px;
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 8px;
  color: #6b5b8a;
  text-decoration: none;
  transition: background 0.2s, color 0.2s;
  margin-bottom: 4px;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.55);
  color: #4a3d62;
}

.nav-item.active {
  background: rgba(255, 255, 255, 0.75);
  color: #4a3d62;
  font-weight: 600;
}

.nav-icon {
  font-size: 18px;
}

.main-area {
  flex-direction: column;
  overflow: hidden;
}

.top-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  padding: 0 24px;
  height: 56px;
}

.page-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  font-size: 13px;
  color: #909399;
}

.content-main {
  padding: 20px 24px;
  overflow: auto;
  height: calc(100vh - 56px);
}
</style>
