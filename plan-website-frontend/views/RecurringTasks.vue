<template>
  <div class="recurring-page">
    <div class="page-head">
      <div><h2>重复任务</h2><p>规则生效后，会在每日规划中自动生成对应日期的任务。</p></div>
      <el-button type="primary" @click="openCreate">新建重复任务</el-button>
    </div>
    <el-empty v-if="!loading && !rules.length" description="还没有重复任务" />
    <div class="rule-grid" v-loading="loading">
      <el-card v-for="rule in rules" :key="rule.id" class="rule-card">
        <template #header><div class="card-head"><strong>{{ rule.content }}</strong><el-tag :type="rule.active ? 'success' : 'info'">{{ rule.active ? '启用' : '停用' }}</el-tag></div></template>
        <p>重复：{{ weekdayText(rule.weekdays) }}</p>
        <p>区间：{{ rule.startDate }} 至 {{ rule.endDate || '长期' }}</p>
        <p v-if="rule.startTime">时间：{{ shortTime(rule.startTime) }}{{ rule.endTime ? ` - ${shortTime(rule.endTime)}` : '' }}</p>
        <p>优先级：{{ priorityText[rule.priority] }}</p>
        <p v-if="rule.reminderEnabled">提醒：截止前 {{ rule.reminderMinutesBefore }} 分钟发送邮件</p>
        <div class="actions"><el-button link type="primary" @click="openEdit(rule)">编辑</el-button><el-button link type="danger" @click="remove(rule)">删除</el-button></div>
      </el-card>
    </div>

    <el-dialog v-model="visible" :title="form.id ? '编辑重复任务' : '新建重复任务'" width="620px">
      <el-form label-width="90px">
        <el-form-item label="任务内容" required><el-input v-model="form.content" /></el-form-item>
        <el-form-item label="重复星期" required>
          <el-checkbox-group v-model="form.weekdays"><el-checkbox-button v-for="day in weekdays" :key="day.value" :value="day.value">{{ day.label }}</el-checkbox-button></el-checkbox-group>
        </el-form-item>
        <el-form-item label="日期区间" required>
          <el-date-picker v-model="form.range" type="daterange" value-format="YYYY-MM-DD" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" />
        </el-form-item>
        <div class="form-grid">
          <el-form-item label="开始时间"><el-time-picker v-model="form.startTime" value-format="HH:mm:ss" placeholder="可选" /></el-form-item>
          <el-form-item label="结束时间"><el-time-picker v-model="form.endTime" value-format="HH:mm:ss" placeholder="可选" /></el-form-item>
          <el-form-item label="优先级"><el-select v-model="form.priority"><el-option label="低" value="LOW"/><el-option label="普通" value="MEDIUM"/><el-option label="高" value="HIGH"/><el-option label="紧急" value="URGENT"/></el-select></el-form-item>
          <el-form-item label="预计用时"><el-input-number v-model="form.estimatedMinutes" :min="0" :step="15" /></el-form-item>
          <el-form-item label="是否启用"><el-switch v-model="form.active" /></el-form-item>
          <el-form-item label="邮箱提醒"><el-switch v-model="form.reminderEnabled" /></el-form-item>
          <el-form-item v-if="form.reminderEnabled" label="提前提醒"><el-select v-model="form.reminderMinutesBefore"><el-option label="10分钟" :value="10"/><el-option label="30分钟" :value="30"/><el-option label="1小时" :value="60"/><el-option label="1天" :value="1440"/></el-select></el-form-item>
        </div>
      </el-form>
      <template #footer><el-button @click="visible=false">取消</el-button><el-button type="primary" :loading="saving" @click="save">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const user = JSON.parse(localStorage.getItem('user') || 'null')
const rules = ref([]), loading = ref(false), visible = ref(false), saving = ref(false)
const weekdays = [{label:'一',value:1},{label:'二',value:2},{label:'三',value:3},{label:'四',value:4},{label:'五',value:5},{label:'六',value:6},{label:'日',value:7}]
const priorityText = { LOW:'低', MEDIUM:'普通', HIGH:'高', URGENT:'紧急' }
const form = reactive({})
const defaults = () => ({ id:null, content:'', weekdays:[1,2,3,4,5], range:[], startTime:'00:00:00', endTime:null, priority:'MEDIUM', estimatedMinutes:0, active:true, reminderEnabled:false, reminderMinutesBefore:30 })
const openCreate = () => { Object.assign(form, defaults()); visible.value = true }
const openEdit = rule => { Object.assign(form, defaults(), rule, { weekdays: rule.weekdays.split(',').map(Number), range:[rule.startDate, rule.endDate] }); visible.value = true }
const shortTime = value => value?.slice(0,5)
const weekdayText = value => value.split(',').map(Number).map(n => '周' + weekdays.find(d => d.value === n)?.label).join('、')
const load = async () => { loading.value=true; try { rules.value=(await axios.get(`/api/recurring-tasks?email=${encodeURIComponent(user.email)}`)).data } catch(e){ ElMessage.error('加载失败：'+e.message) } finally { loading.value=false } }
const save = async () => {
  if (!form.content.trim() || !form.weekdays.length || form.range.length !== 2) return ElMessage.warning('请填写内容、星期和日期区间')
  if (form.startTime && form.endTime && form.startTime >= form.endTime) return ElMessage.warning('结束时间必须晚于开始时间')
  saving.value=true
  const payload={ content:form.content.trim(), weekdays:[...form.weekdays].sort().join(','), startDate:form.range[0], endDate:form.range[1], startTime:form.startTime, endTime:form.endTime, priority:form.priority, estimatedMinutes:form.estimatedMinutes, active:form.active, reminderEnabled:form.reminderEnabled, reminderChannel:'EMAIL', reminderMinutesBefore:form.reminderMinutesBefore, user:{id:user.id} }
  try { form.id ? await axios.put(`/api/recurring-task/${form.id}`,payload) : await axios.post('/api/recurring-task',payload); visible.value=false; ElMessage.success('重复任务已保存'); await load() } catch(e){ ElMessage.error('保存失败：'+e.message) } finally { saving.value=false }
}
const remove = async rule => { try { await ElMessageBox.confirm('删除规则后，今天起由它生成的任务也会删除，是否继续？','删除重复任务',{type:'warning'}); await axios.delete(`/api/recurring-task/${rule.id}`); await load(); ElMessage.success('已删除') } catch(e) { if(e !== 'cancel' && e !== 'close') ElMessage.error('删除失败：'+e.message) } }
onMounted(load)
</script>

<style scoped>
.recurring-page { max-width: 1100px; margin: auto; }
.page-head,.card-head,.actions { display:flex; align-items:center; justify-content:space-between; }
.page-head { margin-bottom:20px; }.page-head h2 { margin:0 0 6px; }.page-head p,.rule-card p { color:#606266; }
.rule-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:16px; }
.actions { justify-content:flex-end; }.form-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); column-gap:12px; }
.form-grid :deep(.el-select),.form-grid :deep(.el-date-editor),.form-grid :deep(.el-input-number){width:100%;min-width:0}.form-grid :deep(.el-form-item__content){min-width:0}
@media(max-width:650px){.form-grid{grid-template-columns:1fr}.page-head{align-items:flex-start;gap:12px}}
</style>
