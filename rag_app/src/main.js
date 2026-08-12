import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

// 创建对象
const app = createApp(App)

// 注册路由对象
import router from './router'
app.use(router)

//注册element-plus组件库
import 'element-plus/dist/index.css'
import ElementPlus from 'element-plus'
app.use(ElementPlus)




// token 工具
import { getToken, removeToken } from "./utils/auth"

// axios 全局配置
import axios from 'axios' // 导入axios包
axios.defaults.baseURL = 'http://localhost:8000/' // 服务器请求路径公共部分
axios.defaults.headers.post['Content-Type'] = 'application/json' // post请求发送json数据给服务器
axios.defaults.headers.put['Content-Type'] = 'application/json' // put请求发送json数据给服务器
app.config.globalProperties.$axios = axios // 挂载axios，使用 对象.$axios 代替原生的axios

// 请求拦截器：每次请求自动携带 JWT 令牌
axios.interceptors.request.use(
    config => {
        const token = getToken()
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    error => {
        return Promise.reject(error)
    }
)

// 响应拦截器：token 过期或无效时，清除 token 并跳转登录页
axios.interceptors.response.use(
    response => response,
    error => {
        if (error.response && error.response.status === 401) {
            removeToken()
            router.push('/')
        }
        return Promise.reject(error)
    }
)




app.mount('#app')




