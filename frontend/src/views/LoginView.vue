<script setup>
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuth } from '@/services/useAuth.js'

const router = useRouter()
const { t } = useI18n()
const { login } = useAuth()

const username = ref('')
const password = ref('')
const errorMessage = ref('')
const isLoading = ref(false)

// Simple way to login with the useAuth code.
async function submitLogin() {
  errorMessage.value = ''
  isLoading.value = true

  try {
    await login(username.value, password.value)
    router.push('/')
  } catch (error) {
    errorMessage.value = t('auth.login.errors.invalidCredentials')
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <main class="mx-auto max-w-md px-6 py-12">
    <section class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
      <h1 class="text-3xl font-bold text-gray-900">
        {{ t('auth.login.title') }}
      </h1>

      <p class="mt-2 text-sm text-gray-600">
        {{ t('auth.login.subtitle') }}
      </p>

      <form class="mt-6 space-y-4" @submit.prevent="submitLogin">
        <div>
          <label class="block text-sm font-medium text-gray-700">
            {{ t('auth.fields.username') }}
          </label>

          <input
            v-model="username"
            type="text"
            required
            autocomplete="username"
            class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-green-700 focus:outline-none"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">
            {{ t('auth.fields.password') }}
          </label>

          <input
            v-model="password"
            type="password"
            required
            autocomplete="current-password"
            class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-green-700 focus:outline-none"
          />
        </div>

        <p v-if="errorMessage" class="text-sm text-red-600">
          {{ errorMessage }}
        </p>

        <button
          type="submit"
          :disabled="isLoading"
          class="w-full rounded-lg bg-green-700 px-4 py-2 text-sm font-semibold text-white hover:bg-green-800 disabled:opacity-60"
        >
          {{ isLoading ? t('auth.login.loading') : t('auth.login.submit') }}
        </button>
      </form>

      <p class="mt-4 text-center text-sm text-gray-600">
        {{ t('auth.login.noAccount') }}
        <RouterLink
          to="/register"
          class="font-semibold text-green-700 hover:text-green-800"
        >
          {{ t('auth.login.registerLink') }}
        </RouterLink>
      </p>
    </section>
  </main>
</template>