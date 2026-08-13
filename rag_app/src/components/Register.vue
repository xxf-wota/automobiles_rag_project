<template>
    <div>
        <form>
            <div>用户名：<input type="text" placeholder="请输入用户名" v-model="username"></div>
            <div>邮箱号：<input type="text" placeholder="请输入邮箱号" v-model="email"></div>
            <div >密码：<input type="password" placeholder="请输入密码" v-model="password"></div>
            <div>验证码：<input type="text" placeholder="请输入验证码" v-model="code"><button type="button" @click="sendEmail">获取验证码</button></div>
            <button type="button" @click="register">注册</button>
            <br>
            <button type="button" @click="pushLogin">已有帐号？登录</button>
            <br>
        </form>

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

</style>