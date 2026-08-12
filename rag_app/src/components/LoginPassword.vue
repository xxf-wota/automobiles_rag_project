<template>
    <div>
        <form>
            邮箱号：<input type="text" placeholder="请输入邮箱号" v-model="email">
            <br>
            <div >密码：<input type="password" placeholder="请输入密码" v-model="password"></div>
            <button type="button" @click="email_password">登录</button><button type="button" @click="pushLogin">使用验证码登录</button>
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
            // 保存后端返回的 JWT token，用于后续请求身份认证
            setToken(res.data.data.access_token)
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

</script>

<style scoped>

</style>