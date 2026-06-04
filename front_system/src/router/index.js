import { createRouter, createWebHistory } from 'vue-router'
import { DataAnalysis, Document, Histogram, Monitor, Search, UploadFilled } from '@element-plus/icons-vue'
import MainLayout from '@/layouts/MainLayout.vue'
import { pinia } from '@/stores'
import { useUserStore } from '@/stores/user'
import { ROLES } from '@/constants'
import { hasRole } from '@/utils/permission'

export const mainRoutes = [
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { title: '工作台', icon: Monitor, roles: [ROLES.USER, ROLES.ADMIN] }
  },
  {
    path: '/detect',
    name: 'detect',
    component: () => import('@/views/DetectView.vue'),
    meta: { title: '智能检测', icon: UploadFilled, roles: [ROLES.USER, ROLES.ADMIN] }
  },
  {
    path: '/records',
    name: 'records',
    component: () => import('@/views/RecordsView.vue'),
    meta: { title: '检测记录', icon: Document, roles: [ROLES.USER, ROLES.ADMIN] }
  },
  {
    path: '/statistics',
    name: 'statistics',
    component: () => import('@/views/StatisticsView.vue'),
    meta: { title: '统计分析', icon: Histogram, roles: [ROLES.ADMIN] }
  }
]

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue'), meta: { public: true } },
  {
    path: '/',
    component: MainLayout,
    children: mainRoutes
  },
  { path: '/403', name: 'forbidden', component: () => import('@/views/ForbiddenView.vue'), meta: { public: true } },
  { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('@/views/NotFoundView.vue'), meta: { public: true, hidden: true, icon: Search } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  const userStore = useUserStore(pinia)
  if (!userStore.token) userStore.hydrateFromStorage()

  if (to.meta.public) return true

  if (!userStore.isAuthenticated) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  if (!hasRole(userStore.role, to.meta.roles || [])) return '/403'

  return true
})

export default router
