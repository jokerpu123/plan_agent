import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import router from './router'
import axios from 'axios'

const app = createApp(App)
app.use(ElementPlus)
app.use(router)

// 简化 axios 配置（Vite 代理已处理跨域，无需写完整 baseURL）
// app.config.globalProperties.$axios = axios.create({
//   baseURL: '/api' // 仅保留相对路径，由 Vite 代理转发
// })

app.mount('#app')