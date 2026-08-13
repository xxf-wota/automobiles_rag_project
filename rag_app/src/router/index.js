// 引入路由配置
import { createRouter, createWebHistory } from 'vue-router'

// 定义路由配置对象 --- 数组
const routes = [
  {
    path: '', // 登录页，默认路径 http://localhost:8080/
    meta: {
      isLogin: false // 登录页不需要拦截
    },
    component: () => import('../components/Login.vue')
  },
  {
    path: '/register', // 注册页
    meta: {
      isLogin: false // 注册页不需要拦截
    },
    component: () => import('../components/Register.vue')
  },
  {
    path: '/loginPassword', // 登录密码页
    meta: {
      isLogin: false // 登录密码页不需要拦截
    },
    component: () => import('../components/LoginPassword.vue')
  },
  {
    path: '/chat', // 聊天页
    meta: {
      isLogin: true // 聊天页需要拦截
    },
    component: () => import('../components/Chat.vue')
  }

]


// 设置路由模式为history模式 --- 默认为hash模式，会有一个#号
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 导出路由实例
export default router
