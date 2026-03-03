import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: '仪表板', requiresAuth: true }
  },
  {
    path: '/cases',
    name: 'CaseList',
    component: () => import('@/views/CaseList.vue'),
    meta: { title: '案件列表', requiresAuth: true }
  },
  {
    path: '/cases/:id',
    name: 'CaseDetail',
    component: () => import('@/views/CaseDetail.vue'),
    meta: { title: '案件详情', requiresAuth: true }
  },
  {
    path: '/cases/:caseId/audit-trail',
    name: 'AuditTrail',
    component: () => import('@/views/AuditTrail.vue'),
    meta: { title: '审计追踪', requiresAuth: true }
  },
  {
    path: '/prompts',
    name: 'PromptManagement',
    component: () => import('@/views/PromptManagement.vue'),
    meta: { title: 'Prompt 管理', requiresAuth: true }
  },
  {
    path: '/analytics',
    name: 'Analytics',
    component: () => import('@/views/Analytics.vue'),
    meta: { title: '数据分析', requiresAuth: true }
  },
  {
    path: '/users',
    name: 'UserManagement',
    component: () => import('@/views/UserManagement.vue'),
    meta: { title: '用户管理', requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach((to, _from, next) => {
  document.title = `${to.meta.title || '页面'} - 风控决策增强平台`

  const requiresAuth = to.meta.requiresAuth as boolean
  const token = localStorage.getItem('token')

  if (requiresAuth && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/')
  } else {
    next()
  }
})

export default router
