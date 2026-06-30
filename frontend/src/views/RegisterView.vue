<script setup>
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuth } from '@/services/useAuth.js'

const router = useRouter()
const { t } = useI18n()
const { register } = useAuth()

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const role = ref('team_manager')

const errorMessage = ref('')
const isLoading = ref(false)

const roles = [
  { labelKey: 'auth.roles.teamManager', value: 'team_manager' },
  { labelKey: 'auth.roles.referee', value: 'referee' },
  { labelKey: 'auth.roles.sportsAdmin', value: 'sports_admin' },
]

function translatedFieldName(field) {
  const fieldMap = {
    username: 'auth.fields.username',
    email: 'auth.fields.email',
    password: 'auth.fields.password',
    confirm_password: 'auth.fields.confirmPassword',
    role: 'auth.fields.role',
  }

  return fieldMap[field] ? t(fieldMap[field]) : field
}

function formatError(data) {
  if (!data) {
    return t('auth.register.errors.failed')
  }

  if (typeof data === 'string') {
    return data
  }

  if (data.detail) {
    return data.detail
  }

  const firstKey = Object.keys(data)[0]
  const firstValue = data[firstKey]

  if (Array.isArray(firstValue)) {
    return `${translatedFieldName(firstKey)}: ${firstValue[0]}`
  }

  return JSON.stringify(data)
}

async function submitRegister() {
  errorMessage.value = ''

  if (password.value !== confirmPassword.value) {
    errorMessage.value = t('auth.register.errors.passwordsDoNotMatch')
    return
  }

  isLoading.value = true

  try {
    await register({
      username: username.value,
      email: email.value,
      password: password.value,
      confirm_password: confirmPassword.value,
      role: role.value,
    })

    router.push('/')
  } catch (error) {
    errorMessage.value = formatError(error.response?.data)
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <main class="mx-auto max-w-md px-6 py-12">
    <section class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
      <h1 class="text-3xl font-bold text-gray-900">
        {{ t('auth.register.title') }}
      </h1>

      <p class="mt-2 text-sm text-gray-600">
        {{ t('auth.register.subtitle') }}
      </p>

      <form class="mt-6 space-y-4" @submit.prevent="submitRegister">
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
            {{ t('auth.fields.email') }}
          </label>

          <input
            v-model="email"
            type="email"
            required
            autocomplete="email"
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
            autocomplete="new-password"
            class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-green-700 focus:outline-none"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">
            {{ t('auth.fields.confirmPassword') }}
          </label>

          <input
            v-model="confirmPassword"
            type="password"
            required
            autocomplete="new-password"
            class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-green-700 focus:outline-none"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">
            {{ t('auth.fields.role') }}
          </label>

          <select
            v-model="role"
            class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-green-700 focus:outline-none"
          >
            <option
              v-for="item in roles"
              :key="item.value"
              :value="item.value"
            >
              {{ t(item.labelKey) }}
            </option>
          </select>

          <p class="mt-1 text-xs text-gray-500">
            {{ t('auth.register.roleHelp') }}
          </p>
        </div>

        <p v-if="errorMessage" class="text-sm text-red-600">
          {{ errorMessage }}
        </p>

        <button
          type="submit"
          :disabled="isLoading"
          class="w-full rounded-lg bg-green-700 px-4 py-2 text-sm font-semibold text-white hover:bg-green-800 disabled:opacity-60"
        >
          {{ isLoading ? t('auth.register.loading') : t('auth.register.submit') }}
        </button>
      </form>

      <p class="mt-4 text-center text-sm text-gray-600">
        {{ t('auth.register.alreadyHaveAccount') }}
        <RouterLink
          to="/login"
          class="font-semibold text-green-700 hover:text-green-800"
        >
          {{ t('auth.register.loginLink') }}
        </RouterLink>
      </p>
    </section>
  </main>
</template>