<template>
    <div>
        <form>
            邮箱号：<input type="text" placeholder="请输入邮箱号" v-model="email">

            <br>
            <div >验证码：<input type="text" placeholder="请输入验证码" v-model="code"><button type="button" @click="sendEmail">发送验证码</button></div>
            <button type="button" @click="checkCode">登录</button><button type="button" @click="pushLoginPassword">使用密码登录</button>
            <br>
            <button type="button" @click="pushRegister">还没有账号？注册账号</button>
            <br>
        </form>

    </div>
</template>

<script setup>
import {ref, getCurrentInstance, onMounted} from "vue";
import {useRouter} from "vue-router";
import {ElMessage} from "element-plus";
import {setToken} from "../utils/auth";



let email = ref("")

let code = ref("")
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

function checkCode() {
    let checkCode = code.value
    let sendEmail = email.value
    proxy.$axios({
        url: "/users/checkCode",
        method: "get",
        params: {
            email: sendEmail,
            code: checkCode
        }
    }).then(res => {
        if (res.data.code === 200) {
            // 保存后端返回的 JWT token，用于后续请求身份认证
            setToken(res.data.data.access_token)
            ElMessage.info(res.data.msg)
            setTimeout(() => {
                router.push("/chat")
            }, 1000)
        } else {
            ElMessage.error(res.data.msg)
        }
    })
}

function pushLoginPassword() {
    router.push("/loginPassword")
}

function pushRegister() {
    router.push("/register")
}

</script>

<style scoped>

</style>