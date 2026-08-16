<template>
    <div class="admin-shell">
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

            <!-- 导航菜单 -->
            <nav class="sidebar-nav">
                <button type="button" class="nav-btn" @click="pushChat">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                    </svg>
                    返回聊天
                </button>
                <button type="button" class="nav-btn" @click="pushAdmin">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                        <circle cx="9" cy="7" r="4" />
                        <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                        <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                    </svg>
                    用户权限管理
                </button>
                <button type="button" class="nav-btn active">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10" />
                        <path d="M4.93 4.93l14.14 14.14" />
                    </svg>
                    用户封禁管理
                </button>
            </nav>

            <!-- 底部用户信息 -->
            <div class="sidebar-user">
                <div class="user-avatar">{{ username.charAt(0) }}</div>
                <div class="user-meta">
                    <p class="user-name">{{ username }}</p>
                    <p class="user-role">管理员</p>
                </div>
                <button type="button" class="logout-btn" title="退出登录" @click="quitLogin">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                        <path d="M16 17l5-5-5-5" />
                        <path d="M21 12H9" />
                    </svg>
                </button>
            </div>
        </aside>

        <!-- ==================== 右侧主区域 ==================== -->
        <main class="admin-area">
            <!-- 顶部标题栏 -->
            <header class="admin-header">
                <div class="header-left">
                    <h2 class="header-title">用户封禁管理</h2>
                    <p class="header-sub">管理所有用户的封禁状态与解禁时间</p>
                </div>
                <div class="header-right">
                    <span class="user-count">共 {{ userBanList.length }} 个用户</span>
                </div>
            </header>

            <!-- 表格区域 -->
            <div class="table-wrapper">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th class="col-id">用户 ID</th>
                            <th class="col-username">用户名</th>
                            <th class="col-status">封禁状态</th>
                            <th class="col-time">封禁时间</th>
                            <th class="col-time">解禁时间</th>
                            <th class="col-action">操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="user in userBanList" :key="user.user_id">
                            <td class="col-id">
                                <span class="id-badge">{{ user.user_id }}</span>
                            </td>
                            <td class="col-username">
                                <div class="user-cell">
                                    <span class="table-avatar">{{ user.username.charAt(0) }}</span>
                                    <span>{{ user.username }}</span>
                                </div>
                            </td>
                            <td class="col-status">
                                <span class="status-tag" :class="user.status === 1 ? 'banned' : 'normal'">
                                    {{ user.status === 1 ? '已封禁' : '正常' }}
                                </span>
                            </td>
                            <td class="col-time">
                                <span v-if="user.banned_time" class="time-text">{{ user.banned_time }}</span>
                                <span v-else class="time-empty">--</span>
                            </td>
                            <td class="col-time">
                                <span v-if="user.normal_time" class="time-text">{{ user.normal_time }}</span>
                                <span v-else class="time-empty">--</span>
                            </td>
                            <td class="col-action">
                                <button
                                    v-if="user.status === 1"
                                    type="button"
                                    class="action-btn unban"
                                    @click="banUser(user.user_id, 0, 0)"
                                >
                                    解禁
                                </button>
                                <button
                                    v-else
                                    type="button"
                                    class="action-btn ban"
                                    @click="openBanDialog(user.user_id)"
                                >
                                    封禁
                                </button>
                            </td>
                        </tr>
                        <tr v-if="userBanList.length === 0">
                            <td colspan="6" class="empty-row">
                                <div class="empty-state">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                                        <circle cx="12" cy="12" r="10" />
                                        <path d="M4.93 4.93l14.14 14.14" />
                                    </svg>
                                    <p>暂无用户数据</p>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </main>

        <!-- ==================== 封禁时长弹窗 ==================== -->
        <div v-if="showBanDialog" class="modal-overlay" @click.self="cancelBan">
            <div class="modal-card">
                <h3 class="modal-title">封禁用户</h3>
                <p class="modal-desc">设置封禁时长</p>

                <div class="modal-field">
                    <label class="modal-label">封禁时长（分钟）</label>
                    <input
                        type="number"
                        class="modal-input"
                        v-model="banDuration"
                        placeholder="请输入封禁分钟数"
                        min="1"
                        @keyup.enter="confirmBan"
                    />
                </div>

                <div class="modal-actions">
                    <button type="button" class="modal-btn cancel" @click="cancelBan">取消</button>
                    <button type="button" class="modal-btn confirm" @click="confirmBan">确认封禁</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import {ref, getCurrentInstance, onMounted} from "vue";
import {useRouter} from "vue-router";
import {getToken, getUserId, getUsername, removeToken, getRole, getStatus} from "../utils/auth.js";

import {ElMessage} from "element-plus";


const router = useRouter();

let proxy = getCurrentInstance().proxy
let username = ref(getUsername() || "")

// 用户状态列表
let userBanList = ref([])

// 封禁弹窗状态
let showBanDialog = ref(false)
let banTargetUserId = ref(null)
let banDuration = ref("")

// 打开封禁弹窗
function openBanDialog(userId) {
    banTargetUserId.value = userId
    banDuration.value = ""
    showBanDialog.value = true
}

// 确认封禁
function confirmBan() {
    let duration = parseInt(banDuration.value)
    if (!duration || duration < 1) {
        ElMessage.error("请输入有效的封禁时长（分钟）")
        return
    }
    banUser(banTargetUserId.value, 1, duration)
    showBanDialog.value = false
}

// 取消封禁
function cancelBan() {
    showBanDialog.value = false
    banTargetUserId.value = null
    banDuration.value = ""
}

// 检查用户是否为管理员
function isAdmin() {
    if (getRole() === "admin") {
        return true
    }
    ElMessage.error("您不是管理员，无法跳转到管理员页面")
    return false
}

// 获取用户状态列表
function getUserBanStatus() {
    let token = getToken()
    if (!token) {
        ElMessage.error("请重新登录")
        router.push("/Login")
        return
    }
    if (!isAdmin()) {
        ElMessage.error("您没有管理员权限")
        return
    }
    proxy.$axios({
        url: "/users/getUserBanStatus",
        method: "get",
        headers: {
            "Authorization": "Bearer " + token
        }
    }).then(res => {
        if (res.data.code === 200) {
            userBanList.value = res.data.data
        } else {
            ElMessage.error(res.data.msg)
        }
    })
}

// 用户封禁服务

function banUser(userId, status, ban_time) {

    let token = getToken()
    if (!token) {
        ElMessage.error("请重新登录")
        router.push("/Login")
        return
    }
    if (!isAdmin()) {
        ElMessage.error("您没有管理员权限")
        return
    }
    if (userId === getUserId()) {
        ElMessage.error("您不能封禁或解禁自己")
        return
    }
    // 封禁用户
    proxy.$axios({
        url: "/users/banUser",
        method: "post",
        headers: {
            "Authorization": "Bearer " + token
        },
        data: JSON.stringify({
            userId: userId,
            status: status,
            ban_time: ban_time
        })
    }).then(res => {
        if (res.data.code === 200) {
            ElMessage.success("用户封禁状态更新成功")
            getUserBanStatus()
        } else {
            ElMessage.error(res.data.msg)
        }
    })

}

// 回到聊天页面
function pushChat() {
    router.push("/chat")
}

// 跳转用户权限管理页面
function pushAdmin() {
    router.push("/admin")
}

// 退出登录
function quitLogin() {
    removeToken()
    router.push("/")
}

onMounted(() => {
    getUserBanStatus()
})

</script>

<style scoped>
/* ==================== 主题变量 ==================== */
.admin-shell {
    --ink: #1b1e24;
    --ink-soft: #242830;
    --paper: #f6f4ef;
    --card: #ffffff;
    --border: #e8e3d9;
    --accent: #e8862e;
    --accent-soft: #fdf1e3;
    --text: #26221b;
    --muted: #8a8275;

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

/* 导航菜单 */
.sidebar-nav {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.nav-btn {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    padding: 11px 14px;
    border: none;
    border-radius: 10px;
    background: transparent;
    color: #b3ad9f;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.15s ease;
    text-align: left;
}

.nav-btn svg {
    width: 18px;
    height: 18px;
    flex-shrink: 0;
}

.nav-btn:hover {
    background: var(--ink-soft);
    color: #e8e4dc;
}

.nav-btn.active {
    background: var(--ink-soft);
    color: var(--accent);
    font-weight: 500;
}

/* 底部用户信息 */
.sidebar-user {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 10px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
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
    color: #e8862e;
}

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

/* ==================== 右侧主区域 ==================== */
.admin-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
    background:
        radial-gradient(circle at 15% 0%, rgba(232, 134, 46, 0.05), transparent 40%),
        var(--paper);
}

/* 顶部标题栏 */
.admin-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 28px 36px 20px;
    border-bottom: 1px solid var(--border);
}

.header-left {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.header-title {
    margin: 0;
    font-size: 22px;
    font-weight: 700;
    color: var(--text);
    letter-spacing: 0.3px;
}

.header-sub {
    margin: 0;
    font-size: 13px;
    color: var(--muted);
}

.header-right {
    display: flex;
    align-items: center;
    gap: 16px;
}

.user-count {
    font-size: 13px;
    color: var(--muted);
    background: var(--card);
    border: 1px solid var(--border);
    padding: 7px 16px;
    border-radius: 20px;
}

/* ==================== 表格区域 ==================== */
.table-wrapper {
    flex: 1;
    overflow: auto;
    padding: 24px 36px 36px;
}

.data-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    background: var(--card);
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid var(--border);
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

/* 表头 */
.data-table thead {
    background: #faf8f5;
}

.data-table th {
    padding: 15px 20px;
    font-size: 12px;
    font-weight: 600;
    color: var(--muted);
    text-align: left;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    border-bottom: 1px solid var(--border);
    white-space: nowrap;
}

/* 表体 */
.data-table td {
    padding: 16px 20px;
    font-size: 14px;
    color: var(--text);
    border-bottom: 1px solid #f2efe8;
    vertical-align: middle;
}

.data-table tbody tr:last-child td {
    border-bottom: none;
}

.data-table tbody tr:hover {
    background: #fdfbf7;
}

/* 列宽 */
.col-id {
    width: 100px;
}

.col-username {
    width: 200px;
}

.col-status {
    width: 120px;
}

.col-time {
    width: 180px;
}

.col-action {
    width: 120px;
}

/* ID 标记 */
.id-badge {
    font-family: "SF Mono", "Fira Code", "Consolas", monospace;
    font-size: 13px;
    color: var(--muted);
    background: #f5f2eb;
    padding: 4px 10px;
    border-radius: 6px;
}

/* 用户单元格 */
.user-cell {
    display: flex;
    align-items: center;
    gap: 10px;
}

.table-avatar {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    background: linear-gradient(135deg, #6b8afd, #4f6df5);
    color: #fff;
    font-size: 13px;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

/* 封禁状态标签 */
.status-tag {
    display: inline-block;
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.3px;
}

.status-tag.normal {
    background: #eef7ee;
    color: #3d8b40;
    border: 1px solid rgba(61, 139, 64, 0.2);
}

.status-tag.banned {
    background: #fef0f0;
    color: #e06060;
    border: 1px solid rgba(224, 96, 96, 0.25);
}

/* 时间文本 */
.time-text {
    font-size: 13px;
    color: var(--text);
}

.time-empty {
    font-size: 13px;
    color: #c4bfb5;
}

/* 操作按钮 */
.action-btn {
    padding: 7px 16px;
    border: none;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s ease;
    white-space: nowrap;
}

.action-btn.ban {
    background: #fef0f0;
    color: #e06060;
    border: 1px solid rgba(224, 96, 96, 0.2);
}

.action-btn.ban:hover {
    background: #e06060;
    color: #fff;
}

.action-btn.unban {
    background: #eef7ee;
    color: #3d8b40;
    border: 1px solid rgba(61, 139, 64, 0.2);
}

.action-btn.unban:hover {
    background: #3d8b40;
    color: #fff;
}

/* 空状态 */
.empty-row {
    text-align: center;
}

.empty-state {
    padding: 60px 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    color: var(--muted);
}

.empty-state svg {
    width: 48px;
    height: 48px;
    opacity: 0.4;
}

.empty-state p {
    margin: 0;
    font-size: 14px;
}

/* 滚动条 */
.table-wrapper::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}

.table-wrapper::-webkit-scrollbar-thumb {
    background: #ccc6ba;
    border-radius: 3px;
}

.table-wrapper::-webkit-scrollbar-thumb:hover {
    background: #a8a194;
}

/* ==================== 封禁弹窗 ==================== */
.modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(4px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    animation: fadeIn 0.15s ease;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.modal-card {
    width: 380px;
    max-width: 92vw;
    background: var(--card);
    border-radius: 16px;
    padding: 28px 28px 22px;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    border: 1px solid var(--border);
    animation: slideUp 0.2s ease;
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}

.modal-title {
    margin: 0 0 6px;
    font-size: 18px;
    font-weight: 700;
    color: var(--text);
}

.modal-desc {
    margin: 0 0 20px;
    font-size: 13px;
    color: var(--muted);
}

.modal-field {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-bottom: 22px;
}

.modal-label {
    font-size: 13px;
    font-weight: 600;
    color: var(--text);
    letter-spacing: 0.3px;
}

.modal-input {
    width: 100%;
    padding: 12px 14px;
    border: 1.5px solid var(--border);
    border-radius: 10px;
    font-size: 14px;
    color: var(--text);
    background: #faf8f5;
    outline: none;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
    box-sizing: border-box;
    font-family: inherit;
}

.modal-input::placeholder {
    color: #c4bfb5;
}

.modal-input:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(232, 134, 46, 0.1);
    background: #fff;
}

.modal-actions {
    display: flex;
    gap: 10px;
    justify-content: flex-end;
}

.modal-btn {
    padding: 9px 22px;
    border: none;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s ease;
    font-family: inherit;
}

.modal-btn.cancel {
    background: #f5f2eb;
    color: var(--muted);
}

.modal-btn.cancel:hover {
    background: #e8e3d9;
    color: var(--text);
}

.modal-btn.confirm {
    background: linear-gradient(135deg, #e06060, #d44a4a);
    color: #fff;
    box-shadow: 0 2px 8px rgba(224, 96, 96, 0.25);
}

.modal-btn.confirm:hover {
    background: linear-gradient(135deg, #d44a4a, #c03a3a);
    box-shadow: 0 4px 14px rgba(224, 96, 96, 0.35);
    transform: translateY(-1px);
}

.modal-btn.confirm:active {
    transform: translateY(0);
}
</style>