import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/modules/auth'

const routes = [
  {
    path: '/',
    redirect: '/auth/login'
  },
  {
    path: '/auth',
    component: () => import('../views/AuthLayout.vue'),
    children: [
      {
        path: 'login',
        name: 'Login',
        component: () => import('../views/auth/Login.vue'),
        meta: { requiresAuth: false }
      },
      {
        path: 'register',
        name: 'Register',
        component: () => import('../views/auth/Register.vue'),
        meta: { requiresAuth: false }
      }
    ]
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/checkin',
    name: 'Checkin',
    component: () => import('../views/Checkin.vue'),
    meta: { requiresAuth: true }
  },
  {
      path: '/groups',
      name: 'Groups',
      component: () => import('../views/Groups.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/groups/:id',
      name: 'GroupDetail',
      component: () => import('../views/GroupDetail.vue'),
      meta: { requiresAuth: true }
    },
  {
    path: '/ai-report',
    name: 'AIReport',
    component: () => import('../views/AIReport.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/chat-rooms',
    name: 'ChatRoomManage',
    component: () => import('../views/ChatRoomManage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/chat-rooms/search',
    name: 'ChatRoomSearch',
    component: () => import('../views/ChatRoomSearch.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/chat-rooms/:id',
    name: 'ChatRoomDetail',
    component: () => import('../views/ChatRoomDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/groups/:id/chat',
    name: 'Chat',
    component: () => import('../views/Chat.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const requiresAuth = to.meta.requiresAuth
  // 从localStorage直接获取认证状态，避免Pinia初始化问题
  const isAuthenticated = !!localStorage.getItem('token')

  if (requiresAuth && !isAuthenticated) {
    next('/auth/login')
  } else {
    next()
  }
})

export default router
