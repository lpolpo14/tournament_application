<script setup>
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import {useAuth} from "@/services/useAuth.js";

const router = useRouter()
const { register } = useAuth()

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const role = ref('team_manager')

const errorMessage = ref('')
const isLoading = ref(false)

const roles = [
  { label: 'Team Manager', value: 'team_manager' },
  { label: 'Referee', value: 'referee' },
  { label: 'Sports Administrator', value: 'sports_admin' },
]

function formatError(data) {
  if (!data) return 'Registration failed.'

  if (typeof data === 'string') return data

  if (data.detail) return data.detail

  const firstKey = Object.keys(data)[0]
  const firstValue = data[firstKey]

  if (Array.isArray(firstValue)) {
    return `${firstKey}: ${firstValue[0]}`
  }

  return JSON.stringify(data)
}

async function submitRegister() {
  errorMessage.value = ''

  if (password.value !== confirmPassword.value) {
    errorMessage.value = 'Passwords do not match.'
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
        Register
      </h1>

      <p class="mt-2 text-sm text-gray-600">
        Create your Unipi Sports account.
      </p>

      <form class="mt-6 space-y-4" @submit.prevent="submitRegister">
        <div>
          <label class="block text-sm font-medium text-gray-700">
            Username
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
            Email
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
            Password
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
            Confirm Password
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
            Role
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
              {{ item.label }}
            </option>
          </select>

          <p class="mt-1 text-xs text-gray-500">
            Role selection is included for assignment demonstration purposes.
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
          {{ isLoading ? 'Creating account...' : 'Register' }}
        </button>
      </form>

      <p class="mt-4 text-center text-sm text-gray-600">
        Already have an account?
        <RouterLink
          to="/login"
          class="font-semibold text-green-700 hover:text-green-800"
        >
          Login
        </RouterLink>
      </p>
    </section>
  </main>
</template>