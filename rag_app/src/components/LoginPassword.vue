<template>
    <div class="auth-shell">
        <div class="auth-card">
            <!-- 品牌头部 -->
            <div class="brand-header">
                <div class="brand-mark">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M5 13l1.5-4.5A2 2 0 0 1 8.4 7h7.2a2 2 0 0 1 1.9 1.5L19 13" />
                        <path d="M3 13h18a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1z" />
                        <circle cx="7" cy="18" r="1.6" />
                        <circle cx="17" cy="18" r="1.6" />
                    </svg>
                </div>
                <h1>汽车问答智能助手</h1>
                <p class="brand-sub">密码登录</p>
            </div>

            <!-- 表单 -->
            <form class="auth-form">
                <div class="field">
                    <label class="field-label">邮箱号</label>
                    <input type="text" placeholder="请输入邮箱号" v-model="email" />
                </div>

                <div class="field">
                    <label class="field-label">密码</label>
                    <input type="password" placeholder="请输入密码" v-model="password" />
                </div>

                <button type="button" class="btn-primary" @click="email_password">登录</button>

                <div class="link-row">
                    <button type="button" class="link-btn" @click="pushLogin">使用验证码登录</button>
                </div>

                <div class="link-row">
                    <button type="button" class="link-btn" @click="pushForget">忘记密码</button>
                </div>
            </form>

            <!-- 底部链接 -->
            <div class="auth-footer">
                <button type="button" class="link-btn" @click="pushRegister">还没有账号？注册账号</button>
            </div>
        </div>
    </div>
</template>

<script setup>
import {ref, getCurrentInstance, onMounted} from "vue";
import {useRouter} from "vue-router";
import {ElMessage} from "element-plus";
import {getStatus, setToken} from "../utils/auth.js";

let email = ref("")
let password = ref("")

let router = useRouter()
let proxy = getCurrentInstance().proxy


function email_password() {
    let sendPassword = password.value
    let sendEmail = email.value
    proxy.$axios({
        url: "/users/emailPassword",
        method: "get",
        params: {
            email: sendEmail,
            password: sendPassword
        }
    }).then(res => {
        if (res.data.code === 200) {
            // 登录成功后，将token存储到localStorage
            setToken(res.data.data.access_token)
            // console.log(getStatus())
            // 处理被封禁的情况
            if (getStatus() === 1) {
                ElMessage.error("您已被封禁，无法登录")
                return
            }
            ElMessage.info("登录成功")
            setTimeout(() => {
                router.push("/chat")
            }, 1000)
        } else {
            ElMessage.error(res.data.msg)
        }
    })
}

function pushLogin() {
    router.push("/")
}

function pushRegister() {
    router.push("/register")
}

function pushForget() {
    router.push("/forget")
}

</script>

<style scoped>
/* ==================== 主题变量 ==================== */
.auth-shell {
    --ink: #1b1e24;
    --paper: #f6f4ef;
    --card: #ffffff;
    --border: #e8e3d9;
    --accent: #e8862e;
    --accent-soft: #fdf1e3;
    --text: #26221b;
    --muted: #8a8275;

    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100vh;
    background:
        radial-gradient(circle at 15% 0%, rgba(232, 134, 46, 0.05), transparent 40%),
        radial-gradient(circle at 85% 100%, rgba(79, 109, 245, 0.04), transparent 40%),
        var(--paper);
    font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Segoe UI", sans-serif;
    color: var(--text);
}

/* ==================== 卡片 ==================== */
.auth-card {
    width: 400px;
    max-width: 92vw;
    background: var(--card);
    border-radius: 18px;
    padding: 40px 36px 32px;
    box-shadow:
        0 1px 4px rgba(0, 0, 0, 0.04),
        0 8px 32px rgba(0, 0, 0, 0.06);
    border: 1px solid var(--border);
}

/* ==================== 品牌头部 ==================== */
.brand-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    margin-bottom: 32px;
}

.brand-mark {
    width: 52px;
    height: 52px;
    border-radius: 14px;
    background: linear-gradient(135deg, var(--accent), #f4b063);
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 16px rgba(232, 134, 46, 0.3);
}

.brand-mark svg {
    width: 28px;
    height: 28px;
}

.brand-header h1 {
    margin: 0;
    font-size: 18px;
    font-weight: 700;
    color: var(--text);
    letter-spacing: 0.5px;
}

.brand-sub {
    margin: 0;
    font-size: 13px;
    color: var(--muted);
}

/* ==================== 表单 ==================== */
.auth-form {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.field {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.field-label {
    font-size: 13px;
    font-weight: 600;
    color: var(--text);
    letter-spacing: 0.3px;
}

.field input {
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

.field input::placeholder {
    color: #c4bfb5;
}

.field input:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(232, 134, 46, 0.1);
    background: #fff;
}

/* 主按钮 */
.btn-primary {
    width: 100%;
    padding: 13px 0;
    border: none;
    border-radius: 10px;
    background: linear-gradient(135deg, var(--accent), #f4a04a);
    color: #fff;
    font-size: 15px;
    font-weight: 700;
    cursor: pointer;
    letter-spacing: 0.5px;
    transition: all 0.15s ease;
    font-family: inherit;
    margin-top: 4px;
    box-shadow: 0 2px 8px rgba(232, 134, 46, 0.25);
}

.btn-primary:hover {
    background: linear-gradient(135deg, #d87a24, var(--accent));
    box-shadow: 0 4px 14px rgba(232, 134, 46, 0.35);
    transform: translateY(-1px);
}

.btn-primary:active {
    transform: translateY(0);
}

/* 链接行 */
.link-row {
    text-align: center;
}

.link-btn {
    background: none;
    border: none;
    color: var(--accent);
    font-size: 13px;
    cursor: pointer;
    padding: 4px 8px;
    transition: color 0.15s ease;
    font-family: inherit;
}

.link-btn:hover {
    color: #d87a24;
    text-decoration: underline;
}

/* ==================== 底部 ==================== */
.auth-footer {
    margin-top: 28px;
    padding-top: 20px;
    border-top: 1px solid var(--border);
    text-align: center;
}
</style>