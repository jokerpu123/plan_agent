<template>
  <!-- 新增 id="app" 的根容器，匹配 main.js 的 mount('#app') -->
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
// 确保脚本有有效内容
const emptyPlaceholder = true
</script>

<style scoped>
/* 关键：让根容器占满视口，避免内容看不见 */
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  /* 新增：占满屏幕高度，否则 Login.vue 的 100vh 会失效 */
  width: 100%;
  height: 100vh;
  margin: 0;
  padding: 0;
}
</style>