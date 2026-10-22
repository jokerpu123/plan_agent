import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()], // 必须启用 Vue 插件
  server: {
    port: 8082, // 保持和原 Vue CLI 一致的端口
    open: false, // 不自动打开浏览器，避免开发服务重启时窗口重新弹出
    cors: true, // 允许跨域
    proxy: {
      // Agent 服务（需先于 /api 规则）
      '/api/ai': {
        target: 'http://localhost:8090',
        changeOrigin: true
      },
      // Spring Boot 业务 API
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true
      }
    }
  },
  resolve: {
    // 路径别名（可选，但避免后续导入路径报错）
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  // 显式指定入口（可选，解决 "Could not auto-determine entry point" 警告）
  build: {
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'index.html')
      }
    }
  }
})
