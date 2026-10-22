<template>
  <div class="plan-layout">
    <div class="plan-center">
      <div class="month-toolbar">
        <el-button :icon="ArrowLeft" circle @click="prevMonth" title="上一月" />
        <div class="month-range">
          <span class="range-text">{{ monthTitle }}</span>
          <el-button type="primary" plain size="small" @click="goThisMonth">本月</el-button>
        </div>
        <el-button :icon="ArrowRight" circle @click="nextMonth" title="下一月" />
      </div>

      <div class="week-grid">
        <div
          v-for="week in monthWeeks"
          :key="week.weekStart"
          class="week-card"
          :class="{
            current: week.isCurrentWeek,
            selected: week.weekStart === currentWeekStart,
            past: isWeekPast(week.weekStart)
          }"
          @click="selectWeek(week)"
        >
          <div class="week-label">{{ week.label }}</div>
          <div class="week-dates">{{ week.rangeText }}</div>
          <div class="task-badge" v-if="getTaskCount(week.weekStart) > 0">
            {{ getTaskCount(week.weekStart) }} 项任务
          </div>
          <div class="task-badge empty" v-else>暂无任务</div>
        </div>
      </div>

      <div class="task-panel" v-if="currentWeekStart">
        <div class="task-panel-header">
          <h3>{{ currentWeekLabel }} 任务</h3>
          <el-button
            v-if="!isPastWeek"
            type="primary"
            size="small"
            @click="openAddDialog"
          >
            添加任务
          </el-button>
        </div>
        <div v-if="currentTasks.length === 0" class="empty-tip">这一周还没有任务</div>
        <ul v-else class="task-list">
          <li v-for="task in currentTasks" :key="task.id" class="task-item">
            <div class="task-main">
              <el-checkbox
                v-if="!task.completed"
                :model-value="false"
                :disabled="isPastWeek || updatingId === task.id"
                @change="completeTask(task)"
              />
              <span class="task-content" :class="{ 'is-done': task.status === 'COMPLETED' || task.completed }">
                {{ task.content }}
              </span>
            </div>
            <div class="task-actions">
              <el-tag size="small" :type="task.priority === 'URGENT' ? 'danger' : task.priority === 'HIGH' ? 'warning' : 'info'">{{ priorityText[task.priority] || '普通' }}</el-tag>
              <el-button v-if="!isPastWeek" size="small" link type="primary" @click="openEditDialog(task)">编辑</el-button>
              <el-button
                v-if="!isPastWeek"
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

      <section class="deco-footer">
        <div class="deco-card">
          <img :src="decoBow" alt="" class="deco-sticker deco-left" />
          <div class="deco-copy">
            <p class="deco-title">按周拆分目标，一步步完成～</p>
            <p class="deco-sub">点击某一周添加任务 · 勾选标记完成</p>
          </div>
          <img :src="decoHood" alt="" class="deco-sticker deco-right" />
        </div>
      </section>

      <TaskEditorDialog v-model="dialogVisible" :date="currentWeekStart" plan-type="weekly" :task="editingTask" :user="user" @saved="loadMonthTasks" />
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
  getMonthWeeks,
  getMonthTitle,
  getWeekRangeText,
  isWeekPast
} from '../utils/date.js'
import TaskEditorDialog from '../components/TaskEditorDialog.vue'
import decoBow from '../image/e293d7c6ead9901b34678dab327f4722.png'
import decoHood from '../image/718d03e4f7efe24344af87b108eac230.png'

const user = JSON.parse(localStorage.getItem('user') || 'null')
const now = new Date()

const viewYear = ref(now.getFullYear())
const viewMonth = ref(now.getMonth() + 1)
const currentWeekStart = ref('')
const currentTasks = ref([])
const tasksByWeek = ref({})
const dialogVisible = ref(false)
const editingTask = ref(null)
const updatingId = ref(null)
const priorityText = { LOW: '低', MEDIUM: '普通', HIGH: '高', URGENT: '紧急' }

const monthWeeks = computed(() => getMonthWeeks(viewYear.value, viewMonth.value))
const monthTitle = computed(() => getMonthTitle(viewYear.value, viewMonth.value))

const currentWeekLabel = computed(() => {
  const week = monthWeeks.value.find((w) => w.weekStart === currentWeekStart.value)
  if (!week) return currentWeekStart.value
  return `${week.label}（${getWeekRangeText(week.weekStart)}）`
})

const isPastWeek = computed(() => {
  if (!currentWeekStart.value) return false
  return isWeekPast(currentWeekStart.value)
})

const getTaskCount = (weekStart) => (tasksByWeek.value[weekStart] || []).length

const syncCurrentTasks = () => {
  currentTasks.value = tasksByWeek.value[currentWeekStart.value] || []
}

const pickDefaultWeek = () => {
  const current = monthWeeks.value.find((w) => w.isCurrentWeek)
  if (current) {
    currentWeekStart.value = current.weekStart
    return
  }
  const firstFuture = monthWeeks.value.find((w) => !isWeekPast(w.weekStart))
  currentWeekStart.value = (firstFuture || monthWeeks.value[0])?.weekStart || ''
}

const loadMonthTasks = async () => {
  if (!user?.email) return
  try {
    const results = await Promise.all(
      monthWeeks.value.map((week) =>
        axios
          .get(`/api/tasks?email=${user.email}&date=${week.weekStart}&planType=weekly`)
          .then((res) => ({ weekStart: week.weekStart, tasks: res.data }))
      )
    )
    const map = {}
    results.forEach(({ weekStart, tasks }) => {
      map[weekStart] = tasks
    })
    tasksByWeek.value = map
    syncCurrentTasks()
  } catch (err) {
    ElMessage.error('加载周任务失败：' + (err.message || '未知错误'))
  }
}

const selectWeek = (week) => {
  currentWeekStart.value = week.weekStart
  syncCurrentTasks()
}

const openAddDialog = () => {
  editingTask.value = null
  dialogVisible.value = true
}

const openEditDialog = task => { editingTask.value = task; dialogVisible.value = true }

const prevMonth = () => {
  if (viewMonth.value === 1) {
    viewYear.value -= 1
    viewMonth.value = 12
  } else {
    viewMonth.value -= 1
  }
}

const nextMonth = () => {
  if (viewMonth.value === 12) {
    viewYear.value += 1
    viewMonth.value = 1
  } else {
    viewMonth.value += 1
  }
}

const goThisMonth = () => {
  const today = new Date()
  viewYear.value = today.getFullYear()
  viewMonth.value = today.getMonth() + 1
  currentWeekStart.value = getMonday(today)
}

const completeTask = async (task) => {
  if (updatingId.value !== null) return
  updatingId.value = task.id
  try {
    await axios.put(`/api/task/${task.id}/complete?completed=true`)
    ElMessage.success('已标记完成')
    await loadMonthTasks()
  } catch (err) {
    ElMessage.error('状态更新失败：' + (err.message || '未知错误'))
  } finally {
    updatingId.value = null
  }
}

const deleteTask = async (task) => {
  if (updatingId.value !== null) return
  try {
    await ElMessageBox.confirm('删除后无法恢复，确定删除该周任务？', '删除任务', {
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
    await loadMonthTasks()
  } catch (err) {
    ElMessage.error('删除失败：' + (err.message || '未知错误'))
  } finally {
    updatingId.value = null
  }
}

watch([viewYear, viewMonth], async () => {
  pickDefaultWeek()
  await loadMonthTasks()
})

watch(dialogVisible, (visible) => {
  if (!visible) {
    editingTask.value = null
  }
})

const handleAgentDataChanged = (event) => {
  if (event.detail?.resource === 'tasks' || event.detail?.resource === 'recurring_tasks') {
    loadMonthTasks()
  }
}

onMounted(async () => {
  pickDefaultWeek()
  await loadMonthTasks()
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


.month-toolbar {
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

.month-range {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  min-width: 200px;
}

.range-text {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.week-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 24px;
}

.week-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px 16px;
  text-align: center;
  cursor: pointer;
  border: 2px solid transparent;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
}

.week-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 16px rgba(30, 58, 95, 0.15);
}

.week-card.current {
  border-color: #409eff;
  background: linear-gradient(180deg, #ecf5ff 0%, #fff 100%);
}

.week-card.selected {
  border-color: #1e3a5f;
  box-shadow: 0 4px 14px rgba(30, 58, 95, 0.2);
}

.week-card.past {
  opacity: 0.75;
}

.week-label {
  font-size: 18px;
  font-weight: 700;
  color: #1e3a5f;
  margin-bottom: 8px;
}

.week-dates {
  font-size: 13px;
  color: #909399;
  margin-bottom: 12px;
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

.task-content {
  flex: 1;
  word-break: break-word;
  line-height: 1.5;
}

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
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .week-grid {
    grid-template-columns: 1fr;
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
