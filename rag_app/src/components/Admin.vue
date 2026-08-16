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
                <button type="button" class="nav-btn active">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                        <circle cx="9" cy="7" r="4" />
                        <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                        <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                    </svg>
                    用户权限管理
                </button>
                <button type="button" class="nav-btn" @click="pushBan">
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
                    <h2 class="header-title">用户权限管理</h2>
                    <p class="header-sub">管理所有用户的角色与权限</p>
                </div>
                <div class="header-right">
                    <span class="user-count">共 {{ userList.length }} 个用户</span>
                </div>
            </header>

            <!-- 表格区域 -->
            <div class="table-wrapper">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th class="col-id">用户 ID</th>
                            <th class="col-username">用户名</th>
                            <th class="col-role">角色</th>
                            <th class="col-time">创建时间</th>
                            <th class="col-action">操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="user in userList" :key="user.user_id">
                            <td class="col-id">
                                <span class="id-badge">{{ user.user_id }}</span>
                            </td>
                            <td class="col-username">
                                <div class="user-cell">
                                    <span class="table-avatar">{{ user.username.charAt(0) }}</span>
                                    <span>{{ user.username }}</span>
                                </div>
                            </td>
                            <td class="col-role">
                                <span class="role-tag" :class="user.role">
                                    {{ user.role === 'admin' ? '管理员' : user.role === 'user' ? '普通用户' : user.role }}
                                </span>
                            </td>
                            <td class="col-time">{{ user.create_time }}</td>
                            <td class="col-action">
                                <button
                                    type="button"
                                    class="action-btn"
                                    :class="user.role === 'admin' ? 'demote' : 'promote'"
                                    @click="changeRole(user.user_id, user.role)"
                                >
                                    {{ user.role === 'admin' ? '降为普通用户' : '升为管理员' }}
                                </button>
                            </td>
                        </tr>
                        <tr v-if="userList.length === 0">
                            <td colspan="5" class="empty-row">
                                <div class="empty-state">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                                        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                                        <circle cx="9" cy="7" r="4" />
                                    </svg>
                                    <p>暂无用户数据</p>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </main>
    </div>
</template>

<script setup>
import {ref, getCurrentInstance, onMounted} from "vue";
import {useRouter} from "vue-router";
import {getToken, getUserId, getUsername, removeToken, getRole} from "../utils/auth.js";

import {ElMessage} from "element-plus";

let router = useRouter()
let proxy = getCurrentInstance().proxy
let username = ref(getUsername() || "")

// 模板数据，后续替换为后端接口
let userList = ref([])

// 获取用户权限表
function getUserRoleList() {
    let token = getToken()
    if (!token) {
        ElMessage.error("请重新登录")
        return
    }
    if (!isAdmin()) {
        ElMessage.error("您没有管理员权限")
        return
    }
    proxy.$axios({
        url: "/users/getUserRoleList",
        method: "get",
        headers: {
            "Authorization": "Bearer " + token
        }
    }).then(res => {
        if (res.data.code === 200) {
            userList.value = res.data.data
        } else {
            ElMessage.error(res.data.msg)
        }
    })
}



// 检查用户是否为管理员
function isAdmin() {
    if (getRole() === "admin") {
        return true
    }
    ElMessage.error("您不是管理员，无法跳转到管理员页面")
    return false
}



// 修改用户的role字段
function changeRole(userId, currentRole) {
    let token = getToken()
    if (!token) {
        ElMessage.error("请重新登录")
        return
    }
    if (getStatus() === "banned") {
        ElMessage.error("您已被封禁，无法修改用户权限")
        return
    }
    if (userId === getUserId()) {
        ElMessage.error("您不能修改自己的权限")
        return
    }
    if (!isAdmin()) {
        ElMessage.error("您没有管理员权限")
        return
    }

    let newRole = currentRole === "admin" ? "user" : "admin"

    proxy.$axios({
        url: "/users/changeRole",
        method: "post",
        data: JSON.stringify({
            userId: userId,
            role: newRole
        }),
        headers: {
            "Authorization": "Bearer " + token
        }
    }).then(res => {
        if (res.data.code === 200) {
            ElMessage.success("修改成功")
            // 更新本地数据
            getUserRoleList()
        } else {
            ElMessage.error(res.data.msg)
        }
    })
}

// 回到聊天页面
function pushChat() {
    router.push("/chat")
}

// 跳转用户封禁管理页面
function pushBan() {
    router.push("/adminBan")
}

// 退出登录
function quitLogin() {
    removeToken()
    router.push("/")
}

onMounted(() => {
    getUserRoleList()
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

.col-role {
    width: 130px;
}

.col-time {
    width: 200px;
}

.col-action {
    width: 160px;
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

/* 角色标签 */
.role-tag {
    display: inline-block;
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.3px;
}

.role-tag.admin {
    background: #fdf1e3;
    color: #e8862e;
    border: 1px solid rgba(232, 134, 46, 0.25);
}

.role-tag.user {
    background: #eef2ff;
    color: #4f6df5;
    border: 1px solid rgba(79, 109, 245, 0.2);
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

.action-btn.promote {
    background: var(--accent-soft);
    color: var(--accent);
    border: 1px solid rgba(232, 134, 46, 0.25);
}

.action-btn.promote:hover {
    background: var(--accent);
    color: #fff;
}

.action-btn.demote {
    background: #fef0f0;
    color: #e06060;
    border: 1px solid rgba(224, 96, 96, 0.2);
}

.action-btn.demote:hover {
    background: #e06060;
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
</style>