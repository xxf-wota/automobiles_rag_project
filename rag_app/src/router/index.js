// 引入路由配置
import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from '../utils/auth'

// 定义路由配置对象 --- 数组
const routes = [
  {
    path: '', // 登录页，默认路径 http://localhost:8080/
    component: () => import('../components/Login.vue')
  },
  {
    path: '/register', // 注册页
    component: () => import('../components/Register.vue')
  },
  {
    path: '/loginPassword', // 登录密码页
    component: () => import('../components/LoginPassword.vue')
  },
  {
    path: '/chat', // 聊天页
    component: () => import('../components/Chat.vue')
  }

]


// 设置路由模式为history模式 --- 默认为hash模式，会有一个#号
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局前置守卫：未登录不能访问聊天页，自动跳回登录页
router.beforeEach((to, from, next) => {
  if (to.path === '/chat' && !getToken()) {
    next('/')
  } else {
    next()
  }
})

// 导出路由实例
export default router
