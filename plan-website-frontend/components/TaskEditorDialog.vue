<template>
  <el-dialog v-model="visible" :title="task?.id ? '编辑任务' : '添加任务'" width="640px" destroy-on-close>
    <el-form label-width="92px">
      <el-form-item label="任务内容" required>
        <el-input v-model="form.content" type="textarea" :rows="2" placeholder="请输入任务内容" />
      </el-form-item>
      <div class="form-grid">
        <el-form-item label="状态">
          <el-select v-model="form.status"><el-option v-for="item in statuses" :key="item.value" v-bind="item" /></el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="form.priority"><el-option v-for="item in priorities" :key="item.value" v-bind="item" /></el-select>
        </el-form-item>
        <el-form-item label="开始时间"><el-time-picker v-model="form.startTime" value-format="HH:mm:ss" placeholder="可选" /></el-form-item>
        <el-form-item label="结束时间"><el-time-picker v-model="form.endTime" value-format="HH:mm:ss" placeholder="可选" /></el-form-item>
        <el-form-item label="截止时间">
          <el-date-picker v-model="form.deadline" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="可选" />
        </el-form-item>
        <el-form-item label="预计用时">
          <el-input-number v-model="form.estimatedMinutes" :min="0" :step="15" /> <span class="unit">分钟</span>
        </el-form-item>
        <el-form-item label="实际用时">
          <el-input-number v-model="form.actualMinutes" :min="0" :step="15" /> <span class="unit">分钟</span>
        </el-form-item>
      </div>

      <el-form-item label="检查清单">
        <div class="subtasks">
          <div v-for="(item, index) in form.subtasks" :key="index" class="subtask-row">
            <el-checkbox v-model="item.completed" />
            <el-input v-model="item.content" placeholder="子任务内容" />
            <el-button link type="danger" @click="form.subtasks.splice(index, 1)">删除</el-button>
          </div>
          <el-button link type="primary" @click="form.subtasks.push({ content: '', completed: false })">＋ 添加检查项</el-button>
        </div>
      </el-form-item>

      <el-form-item label="任务提醒">
        <el-switch v-model="form.reminderEnabled" />
      </el-form-item>
      <div v-if="form.reminderEnabled" class="form-grid">
        <el-form-item label="提醒渠道">
          <el-radio-group v-model="form.reminderChannel">
            <el-radio value="EMAIL">邮箱</el-radio>
            <el-radio value="SMS" disabled>短信（待配置）</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="提前提醒">
          <el-select v-model="form.reminderMinutesBefore">
            <el-option label="提前10分钟" :value="10" /><el-option label="提前30分钟" :value="30" />
            <el-option label="提前1小时" :value="60" /><el-option label="提前1天" :value="1440" />
          </el-select>
        </el-form-item>
      </div>
    </el-form>
    <template #footer>
      <el-button :disabled="saving" @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="save">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const props = defineProps({ modelValue: Boolean, date: String, task: Object, user: Object, planType: { type: String, default: 'daily' } })
const emit = defineEmits(['update:modelValue', 'saved'])
const visible = ref(false)
const saving = ref(false)
const statuses = [
  { label: '待开始', value: 'TODO' }, { label: '进行中', value: 'IN_PROGRESS' },
  { label: '已完成', value: 'COMPLETED' }, { label: '已延期', value: 'POSTPONED' },
  { label: '已取消', value: 'CANCELLED' }
]
const priorities = [
  { label: '低', value: 'LOW' }, { label: '普通', value: 'MEDIUM' },
  { label: '高', value: 'HIGH' }, { label: '紧急', value: 'URGENT' }
]
const form = reactive({})

const reset = () => Object.assign(form, {
  content: props.task?.content || '', status: props.task?.status || (props.task?.completed ? 'COMPLETED' : 'TODO'),
  priority: props.task?.priority || 'MEDIUM', startTime: props.task?.startTime || '00:00:00',
  endTime: props.task?.endTime || null, deadline: props.task?.deadline || null,
  estimatedMinutes: props.task?.estimatedMinutes ?? 0, actualMinutes: props.task?.actualMinutes ?? 0,
  reminderEnabled: props.task?.reminderEnabled || false,
  reminderChannel: props.task?.reminderChannel || 'EMAIL',
  reminderMinutesBefore: props.task?.reminderMinutesBefore ?? 30,
  subtasks: (props.task?.subtasks || []).map(item => ({ content: item.content, completed: item.completed }))
})

watch(() => props.modelValue, value => { visible.value = value; if (value) reset() }, { immediate: true })
watch(visible, value => emit('update:modelValue', value))

const save = async () => {
  if (!form.content?.trim()) return ElMessage.warning('请输入任务内容')
  if (form.reminderEnabled && !form.deadline) return ElMessage.warning('开启提醒后必须设置截止时间')
  if (form.startTime && form.endTime && form.startTime >= form.endTime) return ElMessage.warning('结束时间必须晚于开始时间')
  saving.value = true
  const payload = {
    ...form, id: props.task?.id || null, content: form.content.trim(), taskDate: props.date, planType: props.task?.planType || props.planType,
    completed: form.status === 'COMPLETED', user: { id: props.user.id },
    subtasks: form.subtasks.filter(item => item.content.trim()).map((item, index) => ({ ...item, content: item.content.trim(), sortOrder: index }))
  }
  try {
    const analysis = (await axios.post('/api/task/analyze', payload)).data
    if (analysis.warnings?.length) {
      await ElMessageBox.confirm(
        `系统发现以下安排风险：\n\n${analysis.warnings.map((item, index) => `${index + 1}. ${item}`).join('\n')}\n\n是否仍然保存？`,
        '任务合理性检测',
        { confirmButtonText: '仍然保存', cancelButtonText: '返回调整', type: 'warning' }
      )
    }
    if (props.task?.id) await axios.put(`/api/task/${props.task.id}`, payload)
    else await axios.post('/api/task', payload)
    ElMessage.success('任务已保存')
    visible.value = false
    emit('saved')
  } catch (error) {
    if (error === 'cancel' || error === 'close') return
    ElMessage.error('保存失败：' + (error.response?.data?.message || error.message))
  } finally { saving.value = false }
}
</script>

<style scoped>
.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); column-gap: 16px; }
.form-grid :deep(.el-select), .form-grid :deep(.el-date-editor), .form-grid :deep(.el-input-number) { width: 100%; min-width: 0; }
.form-grid :deep(.el-form-item__content) { min-width: 0; }
.subtasks { width: 100%; }
.subtask-row { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.unit { margin-left: 8px; color: #909399; }
@media (max-width: 680px) { .form-grid { grid-template-columns: 1fr; } }
</style>
