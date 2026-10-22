<template>
  <div class="focus-page">
    <section class="timer-card">
      <div class="eyebrow">{{ activeSession ? '专注进行中' : '准备开始' }}</div>
      <div class="timer">{{ timerText }}</div>
      <template v-if="activeSession">
        <h2>{{ activeSession.title }}</h2>
        <p>开始于 {{ formatDateTime(activeSession.startedAt) }}</p>
        <el-input v-model="note" type="textarea" :rows="2" placeholder="本次专注备注（可选）" />
        <el-button class="main-button" type="danger" size="large" @click="stopFocus">结束专注</el-button>
      </template>
      <template v-else>
        <el-select v-model="selectedTaskId" clearable placeholder="关联今天的任务（可选）" class="wide">
          <el-option v-for="task in todayTasks" :key="task.id" :label="task.content" :value="task.id" />
        </el-select>
        <el-input v-model="customTitle" placeholder="未关联任务时，填写专注内容" class="wide" />
        <el-button class="main-button" type="primary" size="large" @click="startFocus">开始专注</el-button>
      </template>
    </section>

    <section class="history-card">
      <div class="section-head"><h3>最近七天专注记录</h3><span>共 {{ totalMinutes }} 分钟</span></div>
      <el-empty v-if="!sessions.length" description="还没有专注记录" />
      <div v-for="session in sessions" :key="session.id" class="session-row">
        <div><strong>{{ session.title }}</strong><p>{{ formatDateTime(session.startedAt) }} · {{ session.note || '无备注' }}</p></div>
        <span>{{ durationText(session.durationSeconds) }}</span>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const user = JSON.parse(localStorage.getItem('user') || 'null')
const activeSession = ref(null), sessions = ref([]), todayTasks = ref([])
const selectedTaskId = ref(null), customTitle = ref(''), note = ref(''), now = ref(Date.now())
let ticker
const localDate = date => { const y=date.getFullYear(),m=String(date.getMonth()+1).padStart(2,'0'),d=String(date.getDate()).padStart(2,'0'); return `${y}-${m}-${d}` }
const timerText = computed(() => activeSession.value ? durationText(Math.floor((now.value-new Date(activeSession.value.startedAt).getTime())/1000)) : '00:00:00')
const totalMinutes = computed(() => Math.round(sessions.value.reduce((sum,item)=>sum+(item.durationSeconds||0),0)/60))
const durationText = seconds => { const value=Math.max(0,seconds||0),h=String(Math.floor(value/3600)).padStart(2,'0'),m=String(Math.floor(value%3600/60)).padStart(2,'0'),s=String(value%60).padStart(2,'0'); return `${h}:${m}:${s}` }
const formatDateTime = value => value?.replace('T',' ').slice(0,19)
const load = async () => {
  const today=localDate(new Date()), fromDate=new Date(); fromDate.setDate(fromDate.getDate()-6)
  const [active,tasks,history]=await Promise.all([
    axios.get(`/api/focus/active?email=${encodeURIComponent(user.email)}`),
    axios.get(`/api/tasks?email=${encodeURIComponent(user.email)}&date=${today}&planType=daily`),
    axios.get(`/api/focus/sessions?email=${encodeURIComponent(user.email)}&from=${localDate(fromDate)}&to=${today}`)
  ])
  activeSession.value=active.status===204?null:active.data; todayTasks.value=tasks.data.filter(t=>t.status!=='COMPLETED'&&t.status!=='CANCELLED'); sessions.value=history.data.filter(s=>s.status==='COMPLETED')
}
const startFocus = async () => {
  const task=todayTasks.value.find(item=>item.id===selectedTaskId.value)
  const title=(customTitle.value.trim()||task?.content||'').trim()
  if(!title) return ElMessage.warning('请选择任务或填写专注内容')
  try { activeSession.value=(await axios.post('/api/focus/start',{userId:user.id,taskId:selectedTaskId.value,title})).data; note.value=''; now.value=Date.now() }
  catch(e){ ElMessage.error(e.response?.data||e.message) }
}
const stopFocus = async () => {
  try { await axios.put(`/api/focus/${activeSession.value.id}/stop`,null,{params:{note:note.value||undefined}}); ElMessage.success('专注记录已保存'); activeSession.value=null; selectedTaskId.value=null; customTitle.value=''; await load() }
  catch(e){ ElMessage.error('结束失败：'+e.message) }
}
onMounted(async()=>{ try{await load()}catch(e){ElMessage.error('加载专注数据失败：'+e.message)} ticker=setInterval(()=>now.value=Date.now(),1000) })
onBeforeUnmount(()=>clearInterval(ticker))
</script>

<style scoped>
.focus-page{max-width:900px;margin:auto;display:grid;gap:20px}.timer-card,.history-card{background:#fff;border-radius:16px;padding:28px;box-shadow:0 2px 12px rgba(0,0,0,.06)}
.timer-card{text-align:center;background:linear-gradient(145deg,#f3f8ff,#eef3ff)}.eyebrow{color:#7b8eb5;font-weight:600}.timer{font-size:64px;font-variant-numeric:tabular-nums;color:#30466d;margin:20px 0}.timer-card p{color:#909399}.wide{display:block;max-width:520px;margin:12px auto}.main-button{min-width:180px;margin-top:18px}
.section-head,.session-row{display:flex;justify-content:space-between;align-items:center}.section-head{border-bottom:1px solid #eee}.session-row{padding:16px 0;border-bottom:1px solid #f2f2f2}.session-row p{margin:6px 0 0;color:#909399;font-size:12px}
@media(max-width:600px){.timer{font-size:42px}.timer-card,.history-card{padding:18px}}
</style>
