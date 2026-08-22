import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
// Markdown 配置
import { marked } from 'marked'
import DOMPurify from 'dompurify'

// 创建对象
const app = createApp(App)

// 注册路由对象
import router from './router'
app.use(router)

//注册element-plus组件库
import 'element-plus/dist/index.css'
import ElementPlus from 'element-plus'
app.use(ElementPlus)




// axios 全局配置
import axios from 'axios'
import {getSession, removeSession} from "./utils/auth.js"; // 导入axios包
import {ElMessage} from "element-plus";
axios.defaults.baseURL = 'http://localhost:8000/' // 服务器请求路径公共部分
axios.defaults.headers.post['Content-Type'] = 'application/json' // post请求发送json数据给服务器
axios.defaults.headers.put['Content-Type'] = 'application/json' // put请求发送json数据给服务器
app.config.globalProperties.$axios = axios // 挂载axios，使用 对象.$axios 代替原生的axios

// axios 响应拦截器：全局统一处理 token 失效
// 但内部主动处理token失效也不影响
axios.interceptors.response.use(
    response => response,
    error => {
        if (error.response && error.response.status === 401) {
            removeSession()
            ElMessage.error("登录已过期，请重新登录")
            setTimeout(() => {
                router.push("/")
            }, 1000)
        }
        return Promise.reject(error)
    }
)

// 导航守卫
router.beforeEach((to, from, next) => {
    if(to.meta.isLogin){
        if(!getSession()){
            next('/')
        }else{
            next()
        }
    }else{
        next()
    }
})

// markdown 配置全局
marked.setOptions({
  breaks: true,    // 支持换行
  gfm: true,       // GitHub 风格
  smartLists: true,
  smartypants: false
})

// markdown 正则处理
function normalizeMarkdown(text) {
    return text
        .replace(/\r\n/g, '\n')     // 统一换行符
        .replace(/\n{3,}/g, '\n\n') // 3+ 连续换行 → 1 个空行（保留段落分隔）
        .replace(/(#{1,6} )/g, '\n$1')
        .replace(/- /g, '\n- ')
}

// 全局 markdown 渲染方法
function renderMarkdown(text) {
    if (!text) return ''
    const rawHtml = marked.parse(normalizeMarkdown(text))
    return DOMPurify.sanitize(rawHtml)
}
app.config.globalProperties.$renderMarkdown = renderMarkdown





app.mount('#app')