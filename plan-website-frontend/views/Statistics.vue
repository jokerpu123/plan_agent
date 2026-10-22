<template>
  <div class="statistics-page">
    <div class="toolbar"><div><h2>复盘与统计</h2><p>用真实完成和专注数据回顾计划执行情况。</p></div><el-date-picker v-model="range" type="daterange" value-format="YYYY-MM-DD" range-separator="至" @change="load" /></div>
    <div class="metric-grid" v-loading="loading">
      <div class="metric"><span>完成率</span><strong>{{ data.completionRate || 0 }}%</strong><el-progress :percentage="data.completionRate || 0" :show-text="false" /></div>
      <div class="metric"><span>完成任务</span><strong>{{ data.completedTasks || 0 }} / {{ data.totalTasks || 0 }}</strong></div>
      <div class="metric"><span>逾期任务</span><strong class="danger">{{ data.overdueTasks || 0 }}</strong></div>
      <div class="metric"><span>专注时间</span><strong>{{ formatMinutes(data.focusMinutes) }}</strong><small>{{ data.focusSessions || 0 }} 次专注</small></div>
      <div class="metric"><span>预计用时</span><strong>{{ formatMinutes(data.estimatedMinutes) }}</strong></div>
      <div class="metric"><span>实际用时</span><strong>{{ formatMinutes(data.actualMinutes) }}</strong></div>
    </div>
    <div class="review-grid">
      <section class="panel"><h3>每日完成情况</h3><div v-for="(item,date) in data.daily" :key="date" class="daily-row"><span>{{ date }}</span><el-progress :percentage="item.total ? Math.round(item.completed*100/item.total) : 0" :format="()=>`${item.completed}/${item.total}`" /></div></section>
      <section class="panel"><h3>状态分布</h3><div v-for="item in statusRows" :key="item.key" class="distribution"><span>{{ item.label }}</span><strong>{{ item.value }}</strong></div><h3 class="sub-title">优先级分布</h3><div v-for="item in priorityRows" :key="item.key" class="distribution"><span>{{ item.label }}</span><strong>{{ item.value }}</strong></div></section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
const user=JSON.parse(localStorage.getItem('user')||'null'),data=ref({}),loading=ref(false)
const localDate=date=>{const y=date.getFullYear(),m=String(date.getMonth()+1).padStart(2,'0'),d=String(date.getDate()).padStart(2,'0');return `${y}-${m}-${d}`}
const today=new Date(),start=new Date();start.setDate(today.getDate()-6);const range=ref([localDate(start),localDate(today)])
const labels={TODO:'待开始',IN_PROGRESS:'进行中',COMPLETED:'已完成',POSTPONED:'已延期',CANCELLED:'已取消',LOW:'低',MEDIUM:'普通',HIGH:'高',URGENT:'紧急'}
const rows=obj=>Object.entries(obj||{}).map(([key,value])=>({key,label:labels[key]||key,value}))
const statusRows=computed(()=>rows(data.value.statusCounts)),priorityRows=computed(()=>rows(data.value.priorityCounts))
const formatMinutes=value=>`${Math.floor((value||0)/60)}小时 ${Math.round((value||0)%60)}分钟`
const load=async()=>{if(!range.value?.length)return;loading.value=true;try{data.value=(await axios.get('/api/statistics',{params:{email:user.email,from:range.value[0],to:range.value[1]}})).data}catch(e){ElMessage.error('加载统计失败：'+e.message)}finally{loading.value=false}}
onMounted(load)
</script>

<style scoped>
.statistics-page{max-width:1200px;margin:auto}.toolbar{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}.toolbar h2{margin:0 0 6px}.toolbar p{margin:0;color:#909399}
.metric-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.metric,.panel{background:#fff;border-radius:14px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,.06)}.metric{display:flex;flex-direction:column;gap:10px}.metric span,.metric small{color:#909399}.metric strong{font-size:28px;color:#30466d}.metric strong.danger{color:#f56c6c}
.review-grid{display:grid;grid-template-columns:2fr 1fr;gap:16px;margin-top:16px}.panel h3{margin-top:0}.daily-row{display:grid;grid-template-columns:105px 1fr;align-items:center;gap:12px;margin:14px 0}.distribution{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #f2f2f2}.sub-title{margin-top:24px!important}
@media(max-width:800px){.metric-grid{grid-template-columns:repeat(2,1fr)}.review-grid{grid-template-columns:1fr}.toolbar{align-items:flex-start;gap:14px;flex-direction:column}}@media(max-width:500px){.metric-grid{grid-template-columns:1fr}}
</style>
