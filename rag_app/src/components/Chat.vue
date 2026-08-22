<template>
    <!-- 聊天整体容器：左侧历史记录侧边栏 + 右侧聊天区 -->
    <div class="chat-shell">
        <!-- ==================== 左侧侧边栏 ==================== -->
        <aside class="sidebar">
            <!-- 品牌标题 -->
            <div class="sidebar-brand">
                <div class="brand-mark">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M5 13l1.5-4.5A2 2 0 0 1 8.4 7h7.2a2 2 0 0 1 1.9 1.5L19 13" />
                        <path d="M3 13h18a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1z" />
                        <circle cx="7" cy="18" r="1.6" />
                        <circle cx="17" cy="18" r="1.6" />
                    </svg>
                </div>
                <h1>汽车问答智能助手</h1>
            </div>

            <!-- 新对话按钮 -->
            <button type="button" class="new-chat-btn" @click="newChat">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">
                    <path d="M12 5v14M5 12h14" />
                </svg>
                新对话
            </button>

            <!-- 搜索框 -->
            <div class="search-box">
                <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                    <circle cx="11" cy="11" r="7" />
                    <path d="M20 20l-3.5-3.5" />
                </svg>
                <input
                    type="text"
                    v-model="searchKeyword"
                    placeholder="搜索历史记录"
                    @keyup.enter="searchParentHistory"
                >
                <span v-if="searchKeyword" class="search-clear" @click="clearHistoryList">×</span>
            </div>

            <!-- 历史记录列表 -->
            <div class="history-list">
                <p class="history-label">历史记录</p>

                <div
                    v-for="item in filteredHistory"
                    :key="item.id"
                    class="history-item"
                >
                    <div class="history-main" @click="conversationLog(item.id)">
                        <p class="history-title" >{{ item.title }}</p>
                        <p class="history-time" >{{ item.time }}</p>
                    </div>
                    <button
                        type="button"
                        class="history-delete"
                        title="删除记录"
                        @click="deleteConversation(item.id)"
                    >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M4 7h16M10 11v6M14 11v6M6 7l1 12a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-12M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2" />
                        </svg>
                    </button>
                </div>

                <!-- 搜索无结果 -->
                <div v-if="filteredHistory.length === 0" class="history-empty">
                    <p>没有找到相关记录</p>
                </div>
            </div>

            <!-- 底部用户信息 -->
            <div class="sidebar-user">
                <div class="user-avatar" @click="toggleUserMenu">{{ username.charAt(0) }}</div>
                <div class="user-meta">
                    <p class="user-name">{{ username }}</p>
                    <p class="user-role">{{ isOnline ? '在线' : '离线' }}</p>
                </div>
                <!-- 退出登录按钮 -->
                <button type="button" class="logout-btn" title="退出登录" @click="quitLogin">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                        <path d="M16 17l5-5-5-5" />
                        <path d="M21 12H9" />
                    </svg>
                </button>

                <!-- 用户弹出菜单 -->
                <div v-if="showUserMenu" class="user-popup">
                    <button type="button" class="popup-item" @click="goAdmin">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <rect x="2" y="3" width="20" height="14" rx="2" ry="2" />
                            <path d="M8 21h8M12 17v4" />
                        </svg>
                        开发者平台
                    </button>
                </div>
            </div>
        </aside>

        <!-- ==================== 右侧聊天区 ==================== -->
        <main class="chat-area">
            <!-- 消息列表区域 -->
            <div class="message-list" ref="messageListRef">
                <!-- 默认问候语 -->
                <div v-if="messages.length === 0" class="welcome">
                    <div class="welcome-mark">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M5 13l1.5-4.5A2 2 0 0 1 8.4 7h7.2a2 2 0 0 1 1.9 1.5L19 13" />
                            <path d="M3 13h18a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1z" />
                            <circle cx="7" cy="18" r="1.6" />
                            <circle cx="17" cy="18" r="1.6" />
                        </svg>
                    </div>
                    <p class="welcome-text">你好，{{ username }}</p>
                    <p class="welcome-sub">有什么汽车方面的问题可以问我</p>
                </div>

                <!-- 遍历显示所有消息 -->
                <div
                    v-for="(msg, index) in messages"
                    :key="index"
                    class="message"
                    :class="msg.role"
                >
                    <div class="avatar">{{ msg.role === 'user' ? '我' : 'AI' }}</div>
                    <div class="bubble" v-html="msg.content"></div>
                </div>
            </div>

            <!-- 底部输入框和发送按钮 -->
            <div class="input-bar">
                <div class="input-wrap">
                    <input
                        type="text"
                        placeholder="请输入你的汽车问题"
                        :disabled="isChat"
                        v-model="question"
                        @keyup.enter="chat"
                    >
                </div>
                <button
                    type="button"
                    class="send-btn"
                    @click="chat"
                    :disabled="isChat"
                >
                    <template v-if="!isChat">发送</template>
                    <template v-else><span class="dot"></span>生成中</template>
                </button>
            </div>
        </main>
    </div>
</template>

<script setup>
import {ref, computed, getCurrentInstance, onMounted, onUnmounted, nextTick} from "vue";
import {useRouter} from "vue-router";
import {ElMessage} from "element-plus";
import {getUsername, getSession, removeSession, getUserId, getRole, getStatus} from "../utils/auth.js"
// ==================== 聊天业务 ====================
// 定义聊天状态，false表示没有聊天，可以输入问题
let isChat = ref(false)
// 定义用户问题
let question = ref("")
// 用于接收服务器返回的回答
let messages = ref([])
// 消息列表容器引用，用于滚动到底部
let messageListRef = ref(null)

// 将消息列表滚动到最底部
function scrollToBottom() {
    nextTick(() => {
        if (messageListRef.value) {
            messageListRef.value.scrollTop = messageListRef.value.scrollHeight
        }
    })
}
// 定义用户是否在线
let isOnline = ref(false)
if (getSession()) {
    isOnline.value = true
}

// 代理对象，用于发送axios请求
let proxy = getCurrentInstance().proxy
// 路由对象，登录过期时跳转登录页
let router = useRouter()
// 保存当前请求的 AbortController，用于中止流式请求
let abortController = null


// 用来保存当前聊天记录的id
const currentChatId = ref(0)

// chat函数，发送问题，并更新聊天状态
// 使用 fetch + ReadableStream 实现 SSE，可以在请求头中携带 JWT
// EventSource 无法添加自定义请求头，所以改用 fetch
async function chat() {
    isChat.value = true
    let myQuestion = question.value.trim() // 去掉首尾空格
    question.value = "" // 将问题内容赋值给myQuestion后，清空输入框

    // 判断是否输入了数据
    if (myQuestion.length === 0) {
        ElMessage.error("请输入问题！")
        isChat.value = false
        return
    }

    // 访问服务器 --- 需要把问题myQuestion发送给服务器
    messages.value.push({role: "user", content: myQuestion})
    messages.value.push({role: "assistant", content: "正在生成回复"})
    // 发送消息后滚动到底部
    scrollToBottom()

    // 中止上一次未完成的请求
    if (abortController) {
        abortController.abort()
    }
    abortController = new AbortController() // 创建新的 AbortController

    // 拼接请求地址，注意后端端口是 8000
    let urlSearchParams = new URLSearchParams({
        question: myQuestion,
        historyId: currentChatId.value // 需要多轮对话，所以需要传递历史记录id
    })
    let url = "http://localhost:8000/chat/chat?" + urlSearchParams.toString()

    // 定义拼接结果的变量
    let s = ""

    try {
        // 1. 使用 fetch 发起请求，请求头携带 JWT 令牌
        let response = await fetch(url, {
            headers: {
                "Authorization": "Bearer " + getSession()
            },
            signal: abortController.signal // 用于中止流式请求
        })

        // 2. token 无效或过期，后端返回 401
        // response.status 是固定的，不是后端返回的 code 字段
        if (response.status === 401) {
            removeSession() // 删除过期的 session_id
            ElMessage.error("登录已过期，请重新登录")
            setTimeout(() => {
                router.push("/")
            }, 1000)
            isChat.value = false
            return
        }


        // 3. 其它错误状态码
        if (!response.ok) {
            ElMessage.error("连接服务器失败")
            isChat.value = false
            return
        }

        // 4. 获取响应体流，并流式解码（避免中文等多字节字符被截断导致乱码）
        let reader = response.body.getReader()
        let decoder = new TextDecoder("utf-8")
        // SSE 数据缓冲区
        let buffer = ""

        // 5. 循环读取流数据
        while (true) {
            let {done, value} = await reader.read()
            if (done) break // 连接正常关闭

            // 将本次读取的数据解码并追加到缓冲区
            buffer += decoder.decode(value, {stream: true})

            // 6. 按 SSE 分隔符 \n\n 拆分成完整事件
            let index
            while ((index = buffer.indexOf("\n\n")) !== -1) {
                // 提取当前事件文本，从开始0下标到搜索到的 \n\n 下标
                let eventText = buffer.slice(0, index)
                // 从搜索到的 \n\n 下标开始，截取剩余数据
                buffer = buffer.slice(index + 2)

                // 只处理以 data: 开头的行
                let dataLine = eventText
                    .replace(/\r\n/g, "\n") // 兼容 CRLF 换行（回车换行）
                    .split("\n") // 按行拆分事件文本
                    .find(line => line.startsWith("data:")) // 查找以 data: 开头的行
                if (!dataLine) continue // 如果没有 data: 开头的行，跳过

                // slice(5) 从第6个字符开始截取，去掉 "data:" 前缀
                // trim() 去掉首尾空格
                let payload = dataLine.slice(5).trim()
                if (!payload) continue // 如果 payload 为空，跳过

                // 解析 JSON 字符串
                let parsed
                try {
                    parsed = JSON.parse(payload)
                } catch (e) {
                    console.error("解析SSE数据失败", e)
                    continue
                }
                // 从解析后的 JSON 中提取 content 字段
                let content = parsed.content

                // 7. 处理结束标识 [DONE]
                if (content === "[DONE]") {
                    isChat.value = false // 聊天结束可以输入问题了
                    // 保存本次对话记录
                    saveConversation(myQuestion, s)
                    return
                }

                // 拼接并更新最后一条 assistant 消息的内容
                s += content
                // 渲染 markdown 内容，这样可以支持换行、列表、代码块等 markdown 格式
                messages.value[messages.value.length - 1].content = proxy.$renderMarkdown(s)
                // 流式输出时跟随滚动到底部
                scrollToBottom()
            }
        }

        isChat.value = false // 流正常结束
    } catch (error) {
        // 8. 处理错误：网络断开、连接中断等（主动 abort 触发的错误不需要提示）
        if (error.name !== "AbortError") {
            ElMessage.error("连接服务器失败")
            console.log("发生错误", error)
        }
        isChat.value = false // 聊天结束可以输入问题了
    }
}



// ==================== 历史记录侧边栏数据 ====================
// 当前登录用户名（后续可从 JWT 中解析后替换）
// 若不这样写，username.value会为空，导致历史记录侧边栏数据为空字符串
let username = ref(getUsername() || "")
// 搜索关键字
let searchKeyword = ref("")
// 历史记录假数据（后续接入后端从数据库获取）
let historyList = ref([])

// 搜索父级对话记录
let filteredHistory = computed(() => {
    let keyword = searchKeyword.value.trim()
    if (!keyword) return historyList.value
    return historyList.value.filter(item => item.title.includes(keyword))
})

// 添加新对话
function newChat() {
    currentChatId.value = 0 // 将historyId 置0，表示新对话开始
    messages.value = [] // 清空消息列表
}

// 搜索父级对话记录
function searchParentHistory() {
    let session_id = getSession()
    // 从 sessionStorage 中获取userId
    let userId = getUserId()
    // 检查userId是否为空
    if(!userId) {
        ElMessage.error("请重新登录")
        return
    }
    proxy.$axios({
        url: "/history/searchParentHistory",
        method: "get",
        params: {
            userId: userId,
            question: searchKeyword.value
        },
        // 传递token参数
        headers: {
            "Authorization": "Bearer " + session_id
        }
    }).then(res => {
        if (res.data.code === 200) {
            // console.log(res.data.data)
            // 当搜索到的内容只有一个时，直接跳转到该对话记录
            if (res.data.data.length === 1) {
                messages.value = [] // 清空消息列表，因为用户可能点击了其他历史记录再搜索
                historyList.value = res.data.data
                // queryHistoryMenu()
                conversationLog(res.data.data[0].id) // 需要取后端传过来的historyId，而不是currentChatId.value
            }
            if (searchKeyword.value === "") {
                queryHistoryMenu()
            }

            historyList.value = res.data.data // 后端传过来的就是data_list
        }
    })
    // 重新加载历史记录菜单栏
    queryHistoryMenu()
}

// 清空搜索结果
function clearHistoryList() {
    searchKeyword.value = ""
    // 清空搜索结果后，重新加载历史记录菜单栏
    queryHistoryMenu()
}





// 删除指定历史记录
function deleteConversation(historyId) {
    // 从 sessionStorage 中获取 session_id
    let session_id = getSession()
    // 检查session_id是否为空
    if(!session_id) {
        ElMessage.error("请重新登录")
        return
    }
    proxy.$axios({
        url: "/history/deleteConversation",
        method: "delete",
        params: {
            historyId: historyId
        },
        // 传递token参数
        headers: {
            "Authorization": "Bearer " + session_id
        }
    }).then(res => {
        if (res.data.code === 200) {
            ElMessage.success("删除成功")
            // 删除成功后，清空消息列表
            messages.value = []
            currentChatId.value = 0 // 将historyId 置0，表示新对话开始
            // 删除成功后，刷新历史记录菜单栏
            queryHistoryMenu()
        } else {
            ElMessage.error(res.data.msg)
        }
    })
}

// 获取历史记录菜单栏
function queryHistoryMenu() {
    // 判断用户是否在线，若未在线，则不查询历史记录菜单栏
    if (!isOnline.value) {
        ElMessage.error("请先登录")
        return
    }
    // 从 sessionStorage 中获取 session_id
    let session_id = getSession()
    proxy.$axios({
        url: "/history/queryHistoryMenu",
        method: "get",
        params: {
            userId: getUserId()
        },
        // 传递token参数
        headers: {
            "Authorization": "Bearer " + session_id
        }
    }).then(res => {
        if (res.data.code === 200) {
            historyList.value = res.data.data // 后端传过来的就是data_list
        }

    })

}




// 保存历史对话记录
// 后端使用了JWT权限需要传递token参数
function saveConversation(question, answer) {
    // 从 sessionStorage 中获取 session_id
    let session_id = getSession()
    if (!session_id) {
        ElMessage.error("请重新登录")
        return
    }
    proxy.$axios({
        url: "/chat/saveConversation",
        method: "post",
        //使用post请求时使用data字段
        // 需要存入数据库则需要question、user_id、answer、parent_id
        // 注意：使用post请求时，这里需要将JSON对象转换为字符串
        data: JSON.stringify({
            question: question,
            answer: answer,
            userId: getUserId(),
            parentId: currentChatId.value // parentId是当前对话的historyId，于是就做到了历史记录的关联
        }),
        // 传递token参数
        headers: {
            "Authorization": "Bearer " + session_id
        }
    }).then(res => {
        // 只有当currentChatId.value为0时，才需要更新currentChatId.value，表示这是第一次对话
        // 否则，后续的对话记录会基于当前的currentChatId.value进行关联
        if (currentChatId.value === 0) {
            currentChatId.value = res.data.data.history_id // history_id是在用户发送问题时生成的，用于后续的对话记录
        }
        // 加载历史记录菜单栏
        queryHistoryMenu()
    })
}

// 获取详细历史记录
// 后端使用了JWT权限需要传递token参数
function conversationLog(historyId) {
    // 从 sessionStorage 中获取 session_id
    let session_id = getSession()
    if (!session_id) {
        ElMessage.error("请重新登录")
        return
    }
    currentChatId.value = historyId // 将当前对话的historyId设置为点击的历史记录的historyId
    proxy.$axios({
        url: "/history/conversationLog",
        method: "get",
        params: {
            historyId: historyId
        },
        // 传递token参数
        headers: {
            "Authorization": "Bearer " + session_id
        }
    }).then(res => {
        if (res.data.code === 200) {
            console.log(res.data.msg)
            const rawData = res.data.data
            // 处理markdown格式，由于后端返回的是markdown格式，需要渲染为html格式
            messages.value = rawData.map(msg => ({
                role: msg.role,
                content: msg.role === 'assistant' ? proxy.$renderMarkdown(msg.content) : msg.content
            }))
            // 加载历史记录后滚动到底部
            scrollToBottom()
        if (searchKeyword.value === "") {
            queryHistoryMenu()
        }
        } else {
            ElMessage.error("查询失败")
        }
    })
}

// 退出登录
function quitLogin() {
    // 调用后端删除session，使session_id在服务端立即失效
    let session_id = getSession()
    if (session_id) {
        proxy.$axios({
            url: "/users/logout",
            method: "get",
            headers: {
                "Authorization": "Bearer " + session_id
            }
        })
    }
    // 清除本地session_id
    removeSession()
    // 跳转到登录页
    router.push("/")
}
// ==================== 用户弹出菜单 ====================
let showUserMenu = ref(false)

function toggleUserMenu() {
    showUserMenu.value = !showUserMenu.value
}

function goAdmin() {
    if (!isAdmin()) {
        return
    }
    ElMessage.info("正在跳转到管理员页面")
    setTimeout(() => {
        router.push("/admin")
    }, 1000)
    showUserMenu.value = false

}

// 点击外部关闭弹出菜单
function handleClickOutside(e) {
    let sidebar = document.querySelector(".sidebar-user")
    if (sidebar && !sidebar.contains(e.target)) {
        showUserMenu.value = false
    }
}

// ==================== 管理员权限 ====================
// 检查用户是否为管理员
function isAdmin() {
    if (getRole() === "admin") {
        return true
    }
    ElMessage.error("您不是管理员，无法跳转到管理员页面")
    return false
}



// 组件挂载时加载历史记录菜单栏
onMounted(() => {
    // 取出session_id中的username字段
    if (getSession()) {
        // 将username的session_id解码为原始字符串
        username.value = getUsername()
        // 加载历史记录菜单栏
        queryHistoryMenu()
    }
    document.addEventListener("click", handleClickOutside)
})


// 组件卸载时中止未完成的请求，防止内存泄漏
onUnmounted(() => {
    if (abortController) {
        abortController.abort()
    }
    document.removeEventListener("click", handleClickOutside)
})





</script>

<style scoped>
/* ==================== 主题变量 ==================== */
/* 注意：scoped 样式下不能用 :root（会被重写成 :root[data-v-xxx] 永不匹配导致变量失效），
   改为定义在组件根元素 .chat-shell 上 */
.chat-shell {
    --ink: #1b1e24;           /* 侧边栏深色背景 */
    --ink-soft: #242830;      /* 侧边栏 hover */
    --paper: #f6f4ef;         /* 聊天区暖纸色 */
    --card: #ffffff;          /* 卡片白 */
    --border: #e8e3d9;        /* 边框 */
    --accent: #e8862e;        /* 琥珀强调色 */
    --accent-soft: #fdf1e3;   /* 强调色浅底 */
    --text: #26221b;          /* 主文字 */
    --muted: #8a8275;         /* 次要文字 */

    display: flex;
    width: 100%;
    height: 100vh;
    background: var(--paper);
    font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Segoe UI", sans-serif;
    color: var(--text);
    overflow: hidden;
}

/* ==================== 侧边栏 ==================== */
.sidebar {
    display: flex;
    flex-direction: column;
    width: 280px;
    flex-shrink: 0;
    background: var(--ink);
    color: #e8e4dc;
    padding: 20px 14px 16px;
    gap: 16px;
}

/* 品牌标题 */
.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 4px 6px;
}

.brand-mark {
    width: 40px;
    height: 40px;
    border-radius: 12px;
    background: linear-gradient(135deg, var(--accent), #f4b063);
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 4px 12px rgba(232, 134, 46, 0.35);
}

.brand-mark svg {
    width: 24px;
    height: 24px;
}

.sidebar-brand h1 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    letter-spacing: 0.5px;
    color: #fff;
    line-height: 1.3;
}

/* 新对话按钮 */
.new-chat-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    width: 100%;
    padding: 11px 0;
    border: 1px solid rgba(232, 134, 46, 0.5);
    border-radius: 12px;
    background: var(--accent);
    color: #fff;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
}

.new-chat-btn svg {
    width: 18px;
    height: 18px;
}

.new-chat-btn:hover {
    background: #f0913e;
    box-shadow: 0 4px 14px rgba(232, 134, 46, 0.35);
    transform: translateY(-1px);
}

/* 搜索框 */
.search-box {
    position: relative;
    display: flex;
    align-items: center;
}

.search-icon {
    position: absolute;
    left: 12px;
    width: 16px;
    height: 16px;
    color: #8a8275;
    pointer-events: none;
}

.search-box input {
    width: 100%;
    padding: 10px 34px 10px 36px;
    border: 1px solid transparent;
    border-radius: 10px;
    background: var(--ink-soft);
    color: #e8e4dc;
    font-size: 13px;
    outline: none;
    transition: all 0.2s ease;
}

.search-box input::placeholder {
    color: #6f6a5f;
}

.search-box input:focus {
    border-color: var(--accent);
    background: #2a2e36;
}

.search-clear {
    position: absolute;
    right: 10px;
    width: 18px;
    height: 18px;
    line-height: 16px;
    text-align: center;
    border-radius: 50%;
    background: #4a4e55;
    color: #cfc9bd;
    font-size: 14px;
    cursor: pointer;
}

.search-clear:hover {
    background: #5c6169;
}

/* 历史记录列表 */
.history-list {
    flex: 1;
    overflow-y: auto;
    min-height: 0;
}

.history-label {
    margin: 4px 6px 8px;
    font-size: 11px;
    color: #6f6a5f;
    letter-spacing: 1px;
}

.history-item {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 10px 10px;
    border-radius: 10px;
    transition: background 0.15s ease;
}

.history-item:hover {
    background: var(--ink-soft);
}

.history-main {
    flex: 1;
    min-width: 0;
}

.history-title {
    margin: 0;
    font-size: 13px;
    color: #ded9cf;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.history-time {
    margin: 3px 0 0;
    font-size: 11px;
    color: #6f6a5f;
}

.history-delete {
    width: 28px;
    height: 28px;
    border: none;
    border-radius: 7px;
    background: transparent;
    color: #6f6a5f;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: all 0.15s ease;
    flex-shrink: 0;
}

.history-delete svg {
    width: 16px;
    height: 16px;
}

.history-item:hover .history-delete {
    opacity: 1;
}

.history-delete:hover {
    background: rgba(255, 99, 99, 0.2);
    color: #ff8a8a;
}

/* 空状态 */
.history-empty {
    padding: 32px 0;
    text-align: center;
}

.history-empty p {
    margin: 0;
    font-size: 12px;
    color: #6f6a5f;
}

/* 底部用户信息 */
.sidebar-user {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 10px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    position: relative;
}

.user-avatar {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    background: linear-gradient(135deg, #6b8afd, #4f6df5);
    color: #fff;
    font-size: 16px;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    cursor: pointer;
    transition: all 0.15s ease;
}

.user-avatar:hover {
    box-shadow: 0 0 0 3px rgba(107, 138, 253, 0.35);
}

.user-meta {
    min-width: 0;
    flex: 1;
}

.user-name {
    margin: 0;
    font-size: 14px;
    color: #fff;
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.user-role {
    margin: 2px 0 0;
    font-size: 11px;
    color: #7fb77f;
}

/* 退出登录按钮 */
.logout-btn {
    width: 32px;
    height: 32px;
    border: none;
    border-radius: 8px;
    background: transparent;
    color: #8a8275;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    transition: all 0.15s ease;
}

.logout-btn svg {
    width: 17px;
    height: 17px;
}

.logout-btn:hover {
    background: rgba(255, 99, 99, 0.18);
    color: #ff8a8a;
}

/* 用户弹出菜单 */
.user-popup {
    position: absolute;
    bottom: calc(100% + 8px);
    left: 0;
    right: 0;
    background: #2a2e36;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 4px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
    z-index: 100;
    animation: popupIn 0.15s ease;
}

@keyframes popupIn {
    from {
        opacity: 0;
        transform: translateY(6px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.popup-item {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    padding: 10px 14px;
    border: none;
    border-radius: 8px;
    background: transparent;
    color: #e8e4dc;
    font-size: 13px;
    cursor: pointer;
    transition: all 0.12s ease;
    text-align: left;
}

.popup-item svg {
    width: 17px;
    height: 17px;
    color: var(--accent);
    flex-shrink: 0;
}

.popup-item:hover {
    background: var(--ink-soft);
    color: #fff;
}

/* ==================== 聊天区 ==================== */
.chat-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
    background:
        radial-gradient(circle at 15% 0%, rgba(232, 134, 46, 0.05), transparent 40%),
        var(--paper);
}

/* 消息列表 */
.message-list {
    flex: 1;
    overflow-y: auto;
    padding: 28px;
    display: flex;
    flex-direction: column;
    gap: 18px;
}

/* 默认问候语 */
.welcome {
    margin: auto;
    text-align: center;
    color: var(--muted);
}

.welcome-mark {
    width: 72px;
    height: 72px;
    margin: 0 auto 18px;
    border-radius: 22px;
    background: linear-gradient(135deg, var(--accent), #f4b063);
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 10px 30px rgba(232, 134, 46, 0.3);
}

.welcome-mark svg {
    width: 38px;
    height: 38px;
}

.welcome-text {
    margin: 0 0 8px;
    font-size: 22px;
    font-weight: 600;
    color: var(--text);
}

.welcome-sub {
    margin: 0;
    font-size: 14px;
}

/* 单条消息 */
.message {
    display: flex;
    gap: 12px;
    max-width: 78%;
}

.message.user {
    align-self: flex-end;
    flex-direction: row-reverse;
}

.message.assistant {
    align-self: flex-start;
}

.avatar {
    width: 34px;
    height: 34px;
    border-radius: 10px;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    font-weight: 600;
    color: #fff;
}

.message.user .avatar {
    background: linear-gradient(135deg, #6b8afd, #4f6df5);
}

.message.assistant .avatar {
    background: linear-gradient(135deg, var(--accent), #f4b063);
}

.bubble {
    padding: 12px 16px;
    border-radius: 14px;
    font-size: 14px;
    line-height: 1.7;
    word-wrap: break-word;
}

.message.user .bubble {
    background: linear-gradient(135deg, #6b8afd, #4f6df5);
    color: #fff;
    border-top-right-radius: 4px;
    white-space: pre-wrap;
}

.message.assistant .bubble {
    background: var(--card);
    border: 1px solid var(--border);
    border-top-left-radius: 4px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

/* 底部输入栏 */
.input-bar {
    display: flex;
    gap: 12px;
    padding: 16px 28px 20px;
    border-top: 1px solid var(--border);
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(6px);
}

.input-wrap {
    flex: 1;
}

.input-wrap input {
    width: 100%;
    padding: 13px 16px;
    border: 1px solid var(--border);
    border-radius: 12px;
    background: var(--card);
    font-size: 14px;
    color: var(--text);
    outline: none;
    transition: all 0.2s ease;
    box-sizing: border-box;
}

.input-wrap input::placeholder {
    color: #b3ac9f;
}

.input-wrap input:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(232, 134, 46, 0.12);
}

.input-wrap input:disabled {
    background: #f0ede6;
    cursor: not-allowed;
}

.send-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    min-width: 96px;
    padding: 0 22px;
    border: none;
    border-radius: 12px;
    background: var(--accent);
    color: #fff;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
}

.send-btn:hover:not(:disabled) {
    background: #f0913e;
    box-shadow: 0 4px 14px rgba(232, 134, 46, 0.35);
}

.send-btn:disabled {
    background: #d8d2c6;
    cursor: not-allowed;
}

/* 生成中的小圆点动画 */
.dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #fff;
    animation: blink 1s infinite;
}

@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* ==================== 滚动条美化 ==================== */
.message-list::-webkit-scrollbar,
.history-list::-webkit-scrollbar {
    width: 6px;
}

.message-list::-webkit-scrollbar-thumb,
.history-list::-webkit-scrollbar-thumb {
    background: #ccc6ba;
    border-radius: 3px;
}

.message-list::-webkit-scrollbar-thumb:hover,
.history-list::-webkit-scrollbar-thumb:hover {
    background: #a8a194;
}

.history-list::-webkit-scrollbar-track {
    background: transparent;
}
</style>