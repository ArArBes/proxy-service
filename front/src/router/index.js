import { createRouter, createWebHistory } from 'vue-router'
import UserLogin from '../views/UserLogin.vue'
import UserRegister from '../views/UserRegister.vue'
import UserProfile from '../views/UserProfile.vue'

const routes = [
  { path: '/login', component: UserLogin, meta: { guest: true } },
  { path: '/register', component: UserRegister, meta: { guest: true } },
  { path: '/profile', component: UserProfile, meta: { requiresAuth: true } },
  { path: '/', redirect: '/login' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !isAuthenticated) next('/login')
  else if (to.meta.guest && isAuthenticated) next('/profile')
  else next()
})

export default router