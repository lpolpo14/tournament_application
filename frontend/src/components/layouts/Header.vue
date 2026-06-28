<script setup>
import { computed, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuth } from '@/services/useAuth.js'

const router = useRouter()
const { user, role, isAuthenticated, logout } = useAuth()

const isMobileMenuOpen = ref(false)

const menus = {
  visitor: [
    { label: 'Tournaments', path: '/tournaments' },
    { label: 'Teams', path: '/teams' },
    { label: 'Players', path: '/players' },
  ],

  team_manager: [
    { label: 'Teams', path: '/teams' },
    { label: 'Tournaments', path: '/tournaments' },
    { label: 'Players', path: '/players' },
  ],

  referee: [
    { label: 'My Matches', path: '/referee' },
    { label: 'Tournaments', path: '/tournaments' },
    { label: 'Teams', path: '/teams' },
    { label: 'Players', path: '/players' },
  ],

  sports_admin: [
    { label: 'Tournaments', path: '/tournaments' },
    { label: 'Stadiums', path: '/stadiums' },
    { label: 'Teams', path: '/teams' },
    { label: 'Players', path: '/players' },
  ],
}

const currentMenu = computed(() => menus[role.value] || menus.visitor)

async function handleLogout() {
  await logout()
  isMobileMenuOpen.value = false
  router.push('/login')
}
</script>

<template>
  <header class="border-b border-gray-200 bg-white">
    <nav class="mx-auto max-w-7xl px-6 py-4">
      <div class="flex items-center justify-between">
        <RouterLink to="/" class="text-2xl font-bold text-green-700">
          Unipi Sports
        </RouterLink>

        <div class="hidden items-center gap-6 md:flex">
          <RouterLink
            v-for="item in currentMenu"
            :key="item.label"
            :to="item.path"
            class="text-sm font-medium text-gray-700 hover:text-green-700"
          >
            {{ item.label }}
          </RouterLink>
        </div>

        <div class="hidden items-center gap-4 md:flex">
          <p
            v-if="isAuthenticated"
            class="text-sm text-gray-600"
          >
            Signed in as:
            <span class="font-semibold text-gray-900">
              {{ user.username }}
            </span>
          </p>

          <RouterLink
            v-if="!isAuthenticated"
            to="/login"
            class="rounded-lg bg-green-700 px-4 py-2 text-sm font-semibold text-white hover:bg-green-800"
          >
            Login
          </RouterLink>

          <button
            v-else
            class="rounded-lg bg-gray-900 px-4 py-2 text-sm font-semibold text-white hover:bg-gray-800"
            @click="handleLogout"
          >
            Logout
          </button>
        </div>

        <button
          class="rounded-lg border border-gray-300 px-3 py-2 text-sm font-semibold text-gray-700 md:hidden"
          @click="isMobileMenuOpen = !isMobileMenuOpen"
        >
          Menu
        </button>
      </div>

      <div
        v-if="isMobileMenuOpen"
        class="mt-4 flex flex-col gap-3 border-t border-gray-100 pt-4 md:hidden"
      >
        <p
          v-if="isAuthenticated"
          class="text-sm text-gray-600"
        >
          Signed in as:
          <span class="font-semibold text-gray-900">
            {{ user.username }}
          </span>
        </p>

        <RouterLink
          v-for="item in currentMenu"
          :key="item.label"
          :to="item.path"
          class="text-sm font-medium text-gray-700 hover:text-green-700"
          @click="isMobileMenuOpen = false"
        >
          {{ item.label }}
        </RouterLink>

        <RouterLink
          v-if="!isAuthenticated"
          to="/login"
          class="mt-2 rounded-lg bg-green-700 px-4 py-2 text-center text-sm font-semibold text-white hover:bg-green-800"
          @click="isMobileMenuOpen = false"
        >
          Login
        </RouterLink>

        <button
          v-else
          class="mt-2 rounded-lg bg-gray-900 px-4 py-2 text-sm font-semibold text-white hover:bg-gray-800"
          @click="handleLogout"
        >
          Logout
        </button>
      </div>
    </nav>
  </header>
</template>