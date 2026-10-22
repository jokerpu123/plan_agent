<template>
  <div class="calendar-container">
    <el-header>
      <el-button @click="logout">退出登录</el-button>
      <span class="user-info">当前用户：{{ user.email }}</span>
    </el-header>
    <el-main>
      <!-- 日历组件 -->
      <FullCalendar :options="calendarOptions" />
      
      <!-- 任务编辑弹窗 -->
      <el-dialog v-model="dialogVisible" title="编辑任务" width="400px">
        <el-form :model="taskForm" label-width="80px">
          <el-form-item label="任务内容">
            <el-input v-model="taskForm.content" type="textarea"></el-input>
          </el-form-item>
        </el-form>
        <template v-slot:footer>
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveTask">保存</el-button>
        </template>
      </el-dialog>
      
      <!-- 任务列表 -->
      <div class="task-list" v-if="currentTasks.length > 0">
        <h3>{{ currentDate }} 任务列表</h3>
        <el-list>
          <el-list-item v-for="task in currentTasks" :key="task.id">
            <el-checkbox 
              v-model="task.completed" 
              @change="updateTaskStatus(task)"
              :disabled="isPastDate"
            >
              {{ task.content }} 
              <span v-if="task.completed" style="color: green;">✅ 已完成</span>
              <span v-else style="color: red;">❌ 未完成</span>
            </el-checkbox>
          </el-list-item>
        </el-list>
      </div>
    </el-main>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import interactionPlugin from '@fullcalendar/interaction'
import axios from 'axios'

const router = useRouter()
// 获取当前登录用户
const user = JSON.parse(localStorage.getItem('user'))
// 弹窗控制
const dialogVisible = ref(false)
// 当前选中日期
const currentDate = ref('')
// 当前日期的任务列表
const currentTasks = ref([])
// 任务表单
const taskForm = ref({
  content: '',
  taskDate: '',
  userId: user.id
})

// 判断是否是过去的日期（过去日期不可编辑）
const isPastDate = computed(() => {
  const today = new Date()
  const selectedDate = new Date(currentDate.value)
  return selectedDate < today.setHours(0, 0, 0, 0)
})

// 日历配置
const calendarOptions = reactive({
  plugins: [dayGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  dateClick: (info) => {
    // 点击日期时触发
    currentDate.value = info.dateStr
    loadTasks()
    // 未来日期可编辑
    if (!isPastDate.value) {
      taskForm.value.taskDate = info.dateStr
      dialogVisible.value = true
    }
  },
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,dayGridWeek,dayGridDay'
  }
})

// 加载指定日期的任务
const loadTasks = async () => {
  try {
    const res = await axios.get(`/api/tasks?email=${user.email}&date=${currentDate.value}`)
    currentTasks.value = res.data
  } catch (err) {
    ElMessage.error('加载任务失败：' + err.message)
  }
}

// 保存任务
const saveTask = async () => {
  if (!taskForm.value.content) {
    ElMessage.warning('请输入任务内容')
    return
  }
  try {
    const task = {
      content: taskForm.value.content,
      taskDate: currentDate.value,
      user: { id: user.id },
      completed: false
    }
    await axios.post('/api/task', task)
    ElMessage.success('任务保存成功')
    dialogVisible.value = false
    loadTasks()  // 重新加载任务
    taskForm.value.content = ''  // 清空表单
  } catch (err) {
    ElMessage.error('保存任务失败：' + err.message)
  }
}

// 更新任务完成状态
const updateTaskStatus = async (task) => {
  try {
    await axios.put(`/api/task/${task.id}/complete?completed=${task.completed}`)
    ElMessage.success('状态更新成功')
  } catch (err) {
    ElMessage.error('状态更新失败：' + err.message)
    task.completed = !task.completed  // 回滚状态
  }
}

// 退出登录
const logout = () => {
  localStorage.removeItem('user')
  router.push('/login')
}

// 页面加载时初始化
onMounted(() => {
  if (!user) {
    router.push('/login')
  }
})
</script>

<style scoped>
.calendar-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}
.el-header {
  text-align: right;
  font-size: 12px;
  border-bottom: 1px solid #e6e6e6;
  padding: 0 20px;
  line-height: 60px;
}
.el-main {
  flex: 1;
  padding: 20px;
}
.user-info {
  margin-left: 20px;
}
.task-list {
  margin-top: 20px;
  padding: 10px;
  border: 1px solid #e6e6e6;
  border-radius: 4px;
}
</style>