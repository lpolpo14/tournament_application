<script setup>
import { computed, ref } from 'vue'

/*
Note: The script is for the future. We will be adding authentication.
 */
const role = ref('visitor')

const menus = {
  visitor: [
    { label: 'Home', path: '/' },
    { label: 'Tournaments', path: '/tournaments' },
    { label: 'Teams', path: '/teams' },
  ],

  manager: [
    { label: 'Dashboard', path: '/manager' },
    { label: 'My Team', path: '/manager/team' },
    { label: 'Players', path: '/manager/players' },
  ],

  referee: [
    { label: 'Dashboard', path: '/referee' },
    { label: 'Matches', path: '/referee/matches' },
    { label: 'Submit Result', path: '/referee/results' },
  ],
}

const currentMenu = computed(() => menus[role.value])
</script>

<template>
  <header class="border-b border-gray-200 bg-white">
    <nav class="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
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

      <RouterLink
        to="/login"
        class="rounded-lg bg-green-700 px-4 py-2 text-sm font-semibold text-white hover:bg-green-800"
      >
        Login
      </RouterLink>
    </nav>
  </header>
</template>