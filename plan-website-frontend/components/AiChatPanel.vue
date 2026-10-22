<template>
  <Teleport to="body">
  <button class="agent-trigger" :class="{ open: expanded }" @click.stop="expanded = !expanded">
    <span class="trigger-icon">✦</span><span>{{ expanded ? '收起助手' : '计划助手' }}</span>
  </button>
  <transition name="agent-pop">
    <section v-if="expanded" class="agent-workspace">
      <aside class="conversation-sidebar">
        <div class="brand"><span>✦</span><strong>Plan Agent</strong></div>
        <el-button class="new-chat" type="primary" @click="newConversation">＋ 新对话</el-button>
        <div class="conversation-label">最近会话</div>
        <div class="conversation-list">
          <button v-for="item in conversations" :key="item.id" class="conversation-item"
            :class="{ active: item.id === currentConversationId }" @click="openConversation(item.id)">
            <span class="conversation-title">{{ item.title }}</span>
            <span class="delete-chat" title="删除会话" @click.stop="removeConversation(item.id)">×</span>
          </button>
          <div v-if="!conversations.length" class="empty-conversations">还没有会话</div>
        </div>
      </aside>
      <div class="chat-area">
        <header class="chat-header">
          <div><div class="chat-title">{{ currentTitle }}</div><div class="chat-status">{{ statusText }}</div></div>
          <button class="close-button" @click="expanded = false">×</button>
        </header>
        <main ref="messagesRef" class="messages">
          <div v-if="!messages.length" class="welcome">
            <div class="welcome-icon">✦</div><h3>今天想安排什么？</h3>
            <p>可以查询任务、修改状态，或让我制定一个完整计划。</p>
          </div>
          <div v-for="(msg, index) in messages" :key="index" class="message" :class="msg.role">
            <div v-if="msg.role === 'assistant'" class="avatar">AI</div>
            <div class="bubble markdown-body" v-html="renderMarkdown(msg.content)"></div>
          </div>
        </main>
        <footer class="composer">
          <el-input v-model="inputText" type="textarea" :autosize="{ minRows: 2, maxRows: 5 }"
            placeholder="询问计划，或直接让我操作任务…" resize="none" :disabled="sending"
            @keydown.enter.exact.prevent="sendMessage" />
          <div class="composer-footer"><span>Enter 发送 · Shift + Enter 换行</span>
            <el-button type="primary" round :loading="sending" :disabled="!inputText.trim()" @click="sendMessage">发送</el-button>
          </div>
        </footer>
      </div>
    </section>
  </transition>
  </Teleport>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

marked.setOptions({ gfm: true, breaks: true })
const expanded = ref(sessionStorage.getItem('plan-agent-expanded') === 'true')
const conversations = ref([]), currentConversationId = ref('')
const messages = ref([]), messagesRef = ref(null), inputText = ref(''), sending = ref(false)
const user = (() => { try { return JSON.parse(localStorage.getItem('user') || 'null') } catch { return null } })()
const statusText = computed(() => user?.email ? '会话记忆已连接' : '请先登录')
const currentTitle = computed(() => conversations.value.find(item => item.id === currentConversationId.value)?.title || '新对话')
const normalizeMarkdown = content => (content || '').split('\n').map(line => {
  // 模型偶尔会把整行 Markdown 表头包进 **...**，导致管道符被当成粗体文本。
  if (/^\s*\|\s*\*\*.*\*\*\s*\|\s*$/.test(line) && (line.match(/\|/g) || []).length >= 3) {
    return line.replaceAll('**', '')
  }
  return line
}).join('\n')
const renderMarkdown = content => DOMPurify.sanitize(marked.parse(normalizeMarkdown(content)))
const scrollToBottom = async () => { await nextTick(); if (messagesRef.value) messagesRef.value.scrollTop = messagesRef.value.scrollHeight }

const loadConversations = async () => {
  if (!user?.id) return
  const response = await fetch(`/api/ai/conversations?user_id=${user.id}`)
  if (!response.ok) throw new Error('加载会话失败')
  conversations.value = await response.json()
}
const newConversation = async () => {
  const response = await fetch('/api/ai/conversations', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({user_id:user.id,title:'新对话'}) })
  if (!response.ok) throw new Error('创建会话失败')
  const value = await response.json(); await loadConversations(); currentConversationId.value = value.id; messages.value = []
}
const openConversation = async id => {
  const response = await fetch(`/api/ai/conversations/${id}?user_id=${user.id}`)
  if (!response.ok) throw new Error('读取会话失败')
  const value = await response.json(); currentConversationId.value = id
  messages.value = (value.messages || []).map(({role,content}) => ({role,content})); await scrollToBottom()
}
const removeConversation = async id => {
  try { await ElMessageBox.confirm('确定删除这条会话及其记忆吗？','删除会话',{type:'warning'}) } catch { return }
  const response = await fetch(`/api/ai/conversations/${id}?user_id=${user.id}`,{method:'DELETE'})
  if (!response.ok) throw new Error('删除会话失败')
  await loadConversations()
  if (currentConversationId.value === id) conversations.value.length ? await openConversation(conversations.value[0].id) : await newConversation()
}
const parseSseBlock = block => {
  const line = block.split('\n').find(item => item.startsWith('data: ')); if (!line) return null
  try { return JSON.parse(line.slice(6)) } catch { return null }
}
const sendMessage = async () => {
  const text=inputText.value.trim(); if(!text||sending.value||!user?.id)return
  if(!currentConversationId.value)await newConversation()
  messages.value.push({role:'user',content:text}); inputText.value=''; const assistantIndex=messages.value.length
  messages.value.push({role:'assistant',content:''}); sending.value=true; await scrollToBottom()
  try {
    const response=await fetch('/api/ai/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text,email:user.email,user_id:user.id,conversation_id:currentConversationId.value,history:[]})})
    if(!response.ok)throw new Error(`请求失败 (${response.status})`)
    const reader=response.body?.getReader(); if(!reader)throw new Error('浏览器不支持流式响应')
    const decoder=new TextDecoder(); let buffer=''
    while(true){const{done,value}=await reader.read();if(done)break;buffer+=decoder.decode(value,{stream:true});const parts=buffer.split('\n\n');buffer=parts.pop()||''
      for(const part of parts){const payload=parseSseBlock(part);if(!payload)continue
        if(payload.type==='conversation')currentConversationId.value=payload.conversation_id
        else if(payload.type==='token'&&payload.content){messages.value[assistantIndex].content+=payload.content;await scrollToBottom()}
        else if(payload.type==='data_changed')window.dispatchEvent(new CustomEvent('plan-data-changed',{detail:payload}))
        else if(payload.type==='error')throw new Error(payload.content||'Agent 服务错误')}}
    if(!messages.value[assistantIndex].content)messages.value[assistantIndex].content='助手未返回内容。';await loadConversations()
  }catch(error){messages.value[assistantIndex].content=`连接 Agent 失败：${error.message||'未知错误'}`;ElMessage.error(error.message||'发送失败')}
  finally{sending.value=false;await scrollToBottom()}
}
watch(expanded, value => sessionStorage.setItem('plan-agent-expanded', String(value)))
onMounted(async()=>{if(!user?.id)return;try{await loadConversations();conversations.value.length?await openConversation(conversations.value[0].id):await newConversation()}catch(error){ElMessage.error(error.message)}})
</script>

<style scoped>
.agent-trigger{position:fixed;right:28px;bottom:28px;z-index:2100;display:flex;align-items:center;gap:9px;border:0;border-radius:28px;padding:13px 20px;color:#fff;background:linear-gradient(135deg,#5f56d8,#7b70ee);box-shadow:0 12px 30px rgba(70,59,180,.32);cursor:pointer;font-weight:600}.agent-trigger.open{background:#4c4967}.trigger-icon{font-size:19px}
.agent-workspace{position:fixed;z-index:2099;right:28px;bottom:86px;width:min(1040px,calc(100vw - 56px));height:min(760px,calc(100vh - 110px));display:grid;grid-template-columns:240px 1fr;overflow:hidden;border:1px solid rgba(100,90,180,.15);border-radius:18px;background:#fff;box-shadow:0 24px 70px rgba(35,30,80,.28)}
.conversation-sidebar{display:flex;flex-direction:column;min-width:0;padding:18px 12px;color:#eae8ff;background:linear-gradient(180deg,#24213d,#312d52)}.brand{display:flex;gap:9px;align-items:center;padding:2px 8px 18px;font-size:15px}.new-chat{width:100%;margin-bottom:20px;border:0;background:#7167e8}.conversation-label{padding:0 8px 8px;color:#9d98bd;font-size:11px;letter-spacing:.08em}.conversation-list{flex:1;overflow-y:auto}
.conversation-item{width:100%;display:flex;align-items:center;gap:4px;padding:10px;margin-bottom:4px;color:#c9c5e1;border:0;border-radius:9px;background:transparent;cursor:pointer;text-align:left}.conversation-item:hover,.conversation-item.active{color:#fff;background:rgba(255,255,255,.11)}.conversation-title{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.delete-chat{opacity:0;padding:0 3px;font-size:18px}.conversation-item:hover .delete-chat{opacity:.7}.empty-conversations{padding:20px 8px;color:#85809f;font-size:12px}
.chat-area{min-width:0;min-height:0;height:100%;overflow:hidden;display:flex;flex-direction:column;background:#fafaff}.chat-header{flex:0 0 auto;display:flex;justify-content:space-between;align-items:center;padding:16px 20px;border-bottom:1px solid #ececf4;background:#fff}.chat-title{max-width:460px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#29263a;font-weight:700}.chat-status{margin-top:3px;color:#8b879b;font-size:11px}.close-button{border:0;background:transparent;color:#777286;font-size:25px;cursor:pointer}.messages{flex:1 1 0;min-height:0;overflow-y:auto;padding:24px}.welcome{margin:80px auto;max-width:360px;text-align:center;color:#565168}.welcome-icon{color:#7167e8;font-size:38px}.welcome h3{margin:10px 0 5px}.welcome p{margin:0;color:#9691a4;font-size:13px}
.message{display:flex;gap:9px;margin-bottom:18px}.message.user{justify-content:flex-end}.avatar{width:30px;height:30px;flex:0 0 30px;display:grid;place-items:center;border-radius:9px;background:#7167e8;color:#fff;font-size:10px;font-weight:700}.bubble{max-width:82%;padding:11px 14px;border-radius:13px;color:#363246;background:#fff;box-shadow:0 2px 10px rgba(50,45,90,.07);line-height:1.65;word-break:break-word}.message.user .bubble{color:#fff;background:#7167e8;box-shadow:none}.composer{flex:0 0 auto;padding:14px 18px;border-top:1px solid #ececf4;background:#fff}.composer :deep(.el-textarea__inner){box-shadow:none;background:#f5f5fa;border-radius:10px}.composer-footer{display:flex;justify-content:space-between;align-items:center;margin-top:8px;color:#aaa6b5;font-size:11px}
.markdown-body :deep(p){margin:0 0 8px}.markdown-body :deep(p:last-child){margin-bottom:0}.markdown-body :deep(ul),.markdown-body :deep(ol){padding-left:20px}.markdown-body :deep(pre){overflow:auto;padding:10px;border-radius:8px;background:#29263a;color:#f4f2ff}.markdown-body :deep(code){font-family:Consolas,monospace}.markdown-body :deep(table){display:block;max-width:100%;overflow-x:auto;border-collapse:collapse;margin:10px 0;font-size:12px}.markdown-body :deep(th),.markdown-body :deep(td){padding:7px 10px;border:1px solid #dddde8;white-space:nowrap}.markdown-body :deep(th){background:#f0effa;font-weight:600}.markdown-body :deep(h1),.markdown-body :deep(h2),.markdown-body :deep(h3){margin:12px 0 8px;line-height:1.35}
.agent-pop-enter-active,.agent-pop-leave-active{transition:opacity .18s ease,transform .18s ease}.agent-pop-enter-from,.agent-pop-leave-to{opacity:0;transform:translateY(12px) scale(.98)}
@media(max-width:760px){.agent-workspace{right:10px;bottom:76px;width:calc(100vw - 20px);height:calc(100vh - 96px);grid-template-columns:150px 1fr}.agent-trigger{right:14px;bottom:14px}.conversation-sidebar{padding:14px 8px}.composer-footer span{display:none}.messages{padding:14px}}
</style>
