import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/features/auth/views/LoginView.vue'
import RegisterView from '@/features/auth/views/RegisterView.vue'
import HomeView from '@/features/gyms/views/HomeView.vue'
import GymCreateView from '@/features/gyms/views/GymCreateView.vue'
import AdminRequestsView from '@/features/admin/views/AdminRequestsView.vue'
import { useUserStore } from '@/features/auth/store/userStore'

const routes = [
  {
    path: '/',
    redirect: '/login',
  },
  {
    path: '/home',
    name: 'home',
    component: HomeView,
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
  },
  {
    path: '/gyms/create',
    name: 'gym-create',
    component: GymCreateView,
  },
  {
    path: '/gyms/seguidos',
    name: 'followed-gyms',
    component: () => import('@/features/gyms/views/FollowedGymsView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/gyms/:slug',
    name: 'gym-detail',
    component: () => import('@/features/gyms/views/GymDetailView.vue'),
  },
  {
    path: '/admin/solicitudes',
    name: 'admin-requests',
    component: AdminRequestsView,
    meta: { requiresSuperuser: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const userStore = useUserStore()
  if (to.meta.requiresSuperuser && !userStore.user?.is_superuser) {
    return '/home'
  }
  if (to.meta.requiresAuth && !userStore.user) {
    return '/login'
  }
})

export default router