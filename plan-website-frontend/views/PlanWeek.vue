<template>
  <div class="plan-layout">
    <div class="plan-center">
    <!-- 周切换工具栏 -->
    <div class="week-toolbar">
      <el-button :icon="ArrowLeft" circle @click="prevWeek" title="上一周" />
      <div class="week-range">
        <span class="range-text">{{ weekRangeText }}</span>
        <el-button type="primary" plain size="small" @click="goThisWeek">本周</el-button>
      </div>
      <el-button :icon="ArrowRight" circle @click="nextWeek" title="下一周" />
    </div>

    <!-- 一周 7 天 -->
    <div class="week-grid">
      <div
        v-for="day in weekDays"
        :key="day.date"
        class="day-card"
        :class="{
          today: day.isToday,
          selected: day.date === currentDate,
          past: isPast(day.date)
        }"
        @click="selectDay(day)"
      >
        <img :src="day.iconImage" alt="" class="day-icon-img" />
        <div class="weekday">{{ day.weekdayLabel }}</div>
        <div class="date-num">{{ day.month }}/{{ day.dateNum }}</div>
        <div class="task-badge" v-if="getTaskCount(day.date) > 0">
          {{ getTaskCount(day.date) }} 项任务
        </div>
        <div class="task-badge empty" v-else>暂无任务</div>
      </div>
    </div>

    <!-- 选中日期的任务列表 -->
    <div class="task-panel" v-if="currentDate">
      <div class="task-panel-header">
        <h3>{{ currentDate }} 任务</h3>
        <el-button
          v-if="!isPastDate"
          type="primary"
          size="small"
          @click="openAddDialog"
        >
          添加任务
        </el-button>
      </div>
      <div v-if="currentTasks.length === 0" class="empty-tip">这一天还没有任务</div>
      <ul v-else class="task-list">
        <li v-for="task in currentTasks" :key="task.id" class="task-item">
          <div class="task-main">
            <el-checkbox
              :model-value="task.status === 'COMPLETED' || task.completed"
              :disabled="isPastDate || updatingId === task.id"
              @change="value => completeTask(task, value)"
            />
            <el-select
              class="task-status-select"
              :model-value="task.status || (task.completed ? 'COMPLETED' : 'TODO')"
              size="small"
              :disabled="isPastDate"
              @change="value => changeStatus(task, value)"
            >
              <el-option v-for="item in statusOptions" :key="item.value" v-bind="item" />
            </el-select>
            <div class="task-detail">
              <div><el-tag size="small" :type="priorityType[task.priority]">{{ priorityText[task.priority] || '普通' }}</el-tag>
                <span class="task-content" :class="{ 'is-done': task.status === 'COMPLETED' || task.completed }">{{ task.content }}</span>
              </div>
              <div class="task-meta">
                <span v-if="task.startTime || task.endTime">🕐 {{ shortTime(task.startTime) }}{{ task.endTime ? ` - ${shortTime(task.endTime)}` : '' }}</span>
                <span v-if="task.deadline">截止 {{ formatDeadline(task.deadline) }}</span>
                <span v-if="task.estimatedMinutes">预计 {{ task.estimatedMinutes }} 分钟</span>
                <span v-if="task.reminderEnabled">🔔 邮箱提醒</span>
              </div>
              <div v-if="task.subtasks?.length" class="subtask-list">
                <el-checkbox v-for="item in task.subtasks" :key="item.id" :model-value="item.completed"
                  :disabled="isPastDate" @change="value => toggleSubtask(item, value)">{{ item.content }}</el-checkbox>
              </div>
            </div>
          </div>
          <div class="task-actions">
            <el-button v-if="!isPastDate" size="small" link type="primary" @click="openEditDialog(task)">编辑</el-button>
            <el-button
              v-if="!isPastDate"
              size="small"
              link
              type="danger"
              :loading="updatingId === task.id"
              :disabled="updatingId !== null"
              @click="deleteTask(task)"
            >
              删除
            </el-button>
          </div>
        </li>
      </ul>
    </div>

    <!-- 底部装饰（留白区） -->
    <section class="deco-footer">
      <div class="deco-card">
        <img :src="decoBow" alt="" class="deco-sticker deco-left" />
        <div class="deco-copy">
          <p class="deco-title">本周也要开心完成计划呀～</p>
          <p class="deco-sub">点击日期添加任务 · 勾选标记完成</p>
        </div>
        <img :src="decoHood" alt="" class="deco-sticker deco-right" />
      </div>
    </section>

    <TaskEditorDialog v-model="dialogVisible" :date="currentDate" :task="editingTask" :user="user" @saved="loadWeekTasks" />
    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import axios from 'axios'
import {
  getMonday,
  addDays,
  getWeekDays,
  getWeekRangeText,
  formatDate,
  parseDate
} from '../utils/date.js'
import TaskEditorDialog from '../components/TaskEditorDialog.vue'
import decoBow from '../image/e293d7c6ead9901b34678dab327f4722.png'
import decoHood from '../image/718d03e4f7efe24344af87b108eac230.png'

const user = JSON.parse(localStorage.getItem('user') || 'null')

const weekStart = ref(getMonday(new Date()))
const currentDate = ref('')
const currentTasks = ref([])
const tasksByDate = ref({})
const dialogVisible = ref(false)
const editingTask = ref(null)
const updatingId = ref(null)

const weekDays = computed(() => getWeekDays(weekStart.value))
const weekRangeText = computed(() => getWeekRangeText(weekStart.value))

const isPastDate = computed(() => {
  if (!currentDate.value) return false
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return parseDate(currentDate.value) < today
})

const isPast = (dateStr) => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return parseDate(dateStr) < today
}

const getTaskCount = (date) => (tasksByDate.value[date] || []).length

const syncCurrentTasks = () => {
  currentTasks.value = tasksByDate.value[currentDate.value] || []
}

const loadWeekTasks = async () => {
  if (!user?.email) return
  try {
    const results = await Promise.all(
      weekDays.value.map((day) =>
        axios
          .get(`/api/tasks?email=${user.email}&date=${day.date}&planType=daily`)
          .then((res) => ({ date: day.date, tasks: res.data }))
      )
    )
    const map = {}
    results.forEach(({ date, tasks }) => {
      map[date] = tasks
    })
    tasksByDate.value = map
    syncCurrentTasks()
  } catch (err) {
    ElMessage.error('加载任务失败：' + (err.message || '未知错误'))
  }
}

const selectDay = (day) => {
  currentDate.value = day.date
  syncCurrentTasks()
}

const openAddDialog = () => {
  editingTask.value = null
  dialogVisible.value = true
}

const openEditDialog = (task) => {
  editingTask.value = task
  dialogVisible.value = true
}

const statusOptions = [
  { label: '待开始', value: 'TODO' }, { label: '进行中', value: 'IN_PROGRESS' },
  { label: '已完成', value: 'COMPLETED' }, { label: '已延期', value: 'POSTPONED' },
  { label: '已取消', value: 'CANCELLED' }
]
const priorityText = { LOW: '低', MEDIUM: '普通', HIGH: '高', URGENT: '紧急' }
const priorityType = { LOW: 'info', MEDIUM: '', HIGH: 'warning', URGENT: 'danger' }
const shortTime = value => value ? value.slice(0, 5) : ''
const formatDeadline = value => value ? value.replace('T', ' ').slice(0, 16) : ''

const prevWeek = () => {
  weekStart.value = addDays(weekStart.value, -7)
}

const nextWeek = () => {
  weekStart.value = addDays(weekStart.value, 7)
}

const goThisWeek = () => {
  weekStart.value = getMonday(new Date())
  currentDate.value = formatDate(new Date())
}

const completeTask = async (task, completed) => {
  if (updatingId.value !== null) return
  updatingId.value = task.id
  try {
    await axios.put(`/api/task/${task.id}/complete?completed=${completed}`)
    await loadWeekTasks()
  } catch (err) {
    ElMessage.error('状态更新失败：' + (err.message || '未知错误'))
  } finally {
    updatingId.value = null
  }
}

const changeStatus = async (task, status) => {
  await axios.put(`/api/task/${task.id}/status?status=${status}`)
  await loadWeekTasks()
}

const toggleSubtask = async (item, completed) => {
  try { await axios.put(`/api/subtask/${item.id}/complete?completed=${completed}`); await loadWeekTasks() }
  catch (err) { ElMessage.error('检查项更新失败：' + err.message) }
}

const deleteTask = async (task) => {
  if (updatingId.value !== null) return
  try {
    await ElMessageBox.confirm('删除后无法恢复，确定删除该任务？', '删除任务', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
  } catch {
    return
  }
  updatingId.value = task.id
  try {
    await axios.delete(`/api/task/${task.id}`)
    ElMessage.success('任务已删除')
    await loadWeekTasks()
  } catch (err) {
    ElMessage.error('删除失败：' + (err.message || '未知错误'))
  } finally {
    updatingId.value = null
  }
}

watch(weekStart, () => {
  loadWeekTasks()
})

watch(dialogVisible, (visible) => {
  if (!visible) {
    editingTask.value = null
  }
})

const handleAgentDataChanged = (event) => {
  if (event.detail?.resource === 'tasks' || event.detail?.resource === 'recurring_tasks') {
    loadWeekTasks()
  }
}

onMounted(() => {
  currentDate.value = formatDate(new Date())
  loadWeekTasks()
  window.addEventListener('plan-data-changed', handleAgentDataChanged)
})

onBeforeUnmount(() => window.removeEventListener('plan-data-changed', handleAgentDataChanged))
</script>

<style scoped>
.plan-layout {
  display: flex;
  gap: 20px;
  align-items: stretch;
  min-height: calc(100vh - 96px);
}

.plan-center {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}


.week-toolbar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  margin-bottom: 24px;
  padding: 16px 20px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.week-range {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  min-width: 280px;
}

.range-text {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.week-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}

.day-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px 12px;
  text-align: center;
  cursor: pointer;
  border: 2px solid transparent;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
}

.day-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 16px rgba(30, 58, 95, 0.15);
}

.day-card.today {
  border-color: #409eff;
  background: linear-gradient(180deg, #ecf5ff 0%, #fff 100%);
}

.day-card.selected {
  border-color: #1e3a5f;
  box-shadow: 0 4px 14px rgba(30, 58, 95, 0.2);
}

.day-card.past {
  opacity: 0.75;
}

.day-icon-img {
  width: 48px;
  height: 48px;
  object-fit: contain;
  margin-bottom: 8px;
  display: block;
  margin-left: auto;
  margin-right: auto;
}

.weekday {
  font-size: 14px;
  font-weight: 600;
  color: #1e3a5f;
  margin-bottom: 4px;
}

.date-num {
  font-size: 13px;
  color: #909399;
  margin-bottom: 10px;
}

.task-badge {
  font-size: 12px;
  color: #409eff;
  background: #ecf5ff;
  padding: 4px 8px;
  border-radius: 20px;
  display: inline-block;
}

.task-badge.empty {
  color: #c0c4cc;
  background: #f4f4f5;
}

.task-panel {
  background: #fff;
  border-radius: 12px;
  padding: 16px 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  margin-bottom: 20px;
}

.deco-footer {
  margin-top: auto;
  padding-top: 8px;
}

.deco-card {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  padding: 20px 28px;
  border-radius: 16px;
  background: linear-gradient(135deg, #fff5f8 0%, #ffe8f0 50%, #fff0f5 100%);
  border: 1px solid rgba(255, 182, 193, 0.45);
  box-shadow: 0 4px 20px rgba(255, 105, 180, 0.12);
  position: relative;
  overflow: hidden;
}

.deco-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: radial-gradient(circle, rgba(255, 255, 255, 0.7) 1px, transparent 1px);
  background-size: 14px 14px;
  opacity: 0.5;
  pointer-events: none;
}

.deco-sticker {
  width: 100px;
  height: 100px;
  object-fit: contain;
  flex-shrink: 0;
  position: relative;
  z-index: 1;
  filter: drop-shadow(0 4px 8px rgba(255, 105, 180, 0.2));
  transition: transform 0.35s ease;
}

.deco-sticker:hover {
  transform: scale(1.08) rotate(-3deg);
}

.deco-left:hover {
  transform: scale(1.08) rotate(-6deg);
}

.deco-right:hover {
  transform: scale(1.08) rotate(6deg);
}

.deco-copy {
  text-align: center;
  position: relative;
  z-index: 1;
  min-width: 200px;
}

.deco-title {
  margin: 0 0 6px;
  font-size: 16px;
  font-weight: 600;
  color: #d4648a;
  letter-spacing: 0.5px;
}

.deco-sub {
  margin: 0;
  font-size: 13px;
  color: #c990a8;
}

.task-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.task-panel-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.empty-tip {
  color: #909399;
  font-size: 14px;
  padding: 12px 0;
}

.task-list {
  list-style: none;
  margin: 0;
  padding: 0 8px 0 0;
  max-height: clamp(220px, 40vh, 400px);
  overflow-y: auto;
  overscroll-behavior: contain;
  scrollbar-gutter: stable;
}

.task-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.task-main {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.task-status-select {
  width: 96px;
  flex: 0 0 96px;
}

.task-content {
  flex: 1;
  word-break: break-word;
  line-height: 1.5;
}

.task-detail { flex: 1; min-width: 0; }
.task-detail .task-content { margin-left: 8px; }
.task-meta { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 6px; font-size: 12px; color: #909399; }
.subtask-list { display: flex; flex-direction: column; margin-top: 8px; padding-left: 8px; }

.task-content.is-done {
  text-decoration: line-through;
  color: #909399;
}

.task-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.task-item:last-child {
  border-bottom: none;
}

.status {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
}

.status.done {
  color: #67c23a;
  background: #f0f9eb;
}

.status.todo {
  color: #e6a23c;
  background: #fdf6ec;
}

@media (max-width: 1100px) {
  .plan-layout {
    flex-direction: column;
  }

}

@media (max-width: 900px) {
  .week-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 600px) {
  .week-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .deco-card {
    flex-wrap: wrap;
    padding: 16px;
  }

  .deco-sticker {
    width: 72px;
    height: 72px;
  }

  .deco-copy {
    order: -1;
    width: 100%;
  }
}
</style>
