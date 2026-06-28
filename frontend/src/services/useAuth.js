import { computed, ref } from 'vue'
import {
  getMe,
  login as loginService,
  logout as logoutService,
  register as registerService,
} from '@/services/authService'

const user = ref(null)
const isLoaded = ref(false)

const isAuthenticated = computed(() => !!user.value)

const role = computed(() => {
  return user.value?.role || 'visitor'
})

async function loadUser() {
  const response = await getMe()
  user.value = response.user
  isLoaded.value = true
}

async function login(username, password) {
  const response = await loginService(username, password)
  user.value = response.user
  return response
}

async function register(payload) {
  const response = await registerService(payload)
  user.value = response.user
  return response
}

async function logout() {
  await logoutService()
  user.value = null
}

export function useAuth() {
  return {
    user,
    role,
    isLoaded,
    isAuthenticated,
    loadUser,
    login,
    register,
    logout,
  }
}