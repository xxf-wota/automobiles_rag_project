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
                <p class="brand-sub">注册账号</p>
            </div>

            <!-- 表单 -->
            <form class="auth-form">
                <div class="field">
                    <label class="field-label">用户名</label>
                    <input type="text" placeholder="请输入用户名" v-model="username" />
                </div>

                <div class="field">
                    <label class="field-label">邮箱号</label>
                    <input type="text" placeholder="请输入邮箱号" v-model="email" />
                </div>

                <div class="field">
                    <label class="field-label">密码</label>
                    <input type="password" placeholder="请输入密码" v-model="password" />
                </div>

                <div class="field-row">
                    <div class="field field-code">
                        <label class="field-label">验证码</label>
                        <input type="text" placeholder="请输入验证码" v-model="code" />
                    </div>
                    <button type="button" class="btn-send" @click="sendEmail">获取验证码</button>
                </div>

                <button type="button" class="btn-primary" @click="register">注册</button>
            </form>

            <!-- 底部链接 -->
            <div class="auth-footer">
                <button type="button" class="link-btn" @click="pushLogin">已有帐号？登录</button>
            </div>
        </div>
    </div>
</template>

<script setup>
import {ref, getCurrentInstance, onMounted} from "vue";
import {useRouter} from "vue-router";
import {ElMessage} from "element-plus";
import {setToken} from "../utils/auth.js";

let email = ref("")
let password = ref("")
let code = ref("")
let username = ref("")

let router = useRouter()
let proxy = getCurrentInstance().proxy


function sendEmail() {
    ElMessage.info("发送验证码")
    let sendEmail = email.value
    proxy.$axios({
        url: "/users/sendEmail",
        method: "get",
        params: {
            email: sendEmail
        }
    }).then(res => {
        if (res.data.code === 200) {
            ElMessage.info("验证码发送成功")
        } else {
            ElMessage.error(res.data.msg)
        }
    })
}


function register() {
    proxy.$axios({
        url: "/users/register",
        method: "post",
        // post请求后端需要json格式
        data: JSON.stringify({
            username: username.value,
            email: email.value,
            password: password.value,
            code: code.value
        })
    }).then(res => {
        if (res.data.code === 200) {
            ElMessage.info(res.data.msg)
            // 注册成功后，将token存储到localStorage
            setToken(res.data.data.access_token)
            setTimeout(() => {
                router.push("/chat")
            }, 1000)
        } else {
            ElMessage.error(res.data.msg)
        }
    })
}

// 跳转登录登录页
function pushLogin() {
    router.push("/")
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

/* 验证码行 */
.field-row {
    display: flex;
    gap: 10px;
    align-items: flex-end;
}

.field-code {
    flex: 1;
}

.btn-send {
    padding: 12px 16px;
    border: 1.5px solid var(--border);
    border-radius: 10px;
    background: #fff;
    color: var(--accent);
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    white-space: nowrap;
    transition: all 0.15s ease;
    font-family: inherit;
    height: 44px;
    box-sizing: border-box;
}

.btn-send:hover {
    background: var(--accent-soft);
    border-color: var(--accent);
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