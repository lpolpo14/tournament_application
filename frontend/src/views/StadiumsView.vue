<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'
import instance_api from '@/services/api.js'
import { useAuth } from '@/services/useAuth.js'

const { t } = useI18n()
const { role, isAuthenticated, isLoaded, loadUser } = useAuth()

const stadiums = ref([])
const loading = ref(false)
const error = ref('')
const success = ref('')

const form = ref({
  name: '',
  city: '',
  address: '',
}) // ref is simply amazing.

const canManageStadiums = computed(() => {
  return isAuthenticated.value && role.value === 'sports_admin'
})

function normalizeStadiums(data) {
  return Array.isArray(data) ? data : data.results || []
}

function clearMessages() {
  error.value = ''
  success.value = ''
}

function extractError(err) {
  if (err.response?.data) {
    return JSON.stringify(err.response.data, null, 2)
  }

  return err.message || t('stadiums.errors.generic')
}

async function fetchStadiums() {
  loading.value = true
  clearMessages()

  try {
    const response = await instance_api.get('/stadiums/')
    stadiums.value = normalizeStadiums(response.data)
  } catch (err) {
    error.value = extractError(err)
  } finally {
    loading.value = false
  }
}

async function createStadium() {
  /*
  Used for sending a create request to the stadiums api endpoint.
   */
  if (!canManageStadiums.value) {
    error.value = t('stadiums.errors.createForbidden')
    return
  }

  loading.value = true
  clearMessages()

  try {
    const payload = {
      name: form.value.name,
      city: form.value.city,
      address: form.value.address,
    }

    await instance_api.post('/stadiums/', payload)

    success.value = t('stadiums.success.created')

    form.value = {
      name: '',
      city: '',
      address: '',
    }

    await fetchStadiums()
  } catch (err) {
    error.value = extractError(err)
  } finally {
    loading.value = false
  }
}

async function deleteStadium(stadium) {
  /*
  The backend allows for stadium deletion - but we decided not to include it for simplicity.
   */
  if (!canManageStadiums.value) {
    error.value = t('stadiums.errors.deleteForbidden')
    return
  }

  const confirmed = window.confirm(
    t('stadiums.confirmDelete', { name: stadium.name })
  )

  if (!confirmed) {
    return
  }

  loading.value = true
  clearMessages()

  try {
    await instance_api.delete(`/stadiums/${stadium.id}/`)

    success.value = t('stadiums.success.deleted')

    await fetchStadiums()
  } catch (err) {
    error.value = extractError(err)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  if (!isLoaded.value) {
    await loadUser()
  }

  await fetchStadiums()
})
</script>

<template>
  <main class="min-h-screen bg-gray-100 p-6">
    <div class="mx-auto max-w-6xl space-y-6">
      <header class="flex flex-col gap-4 rounded-2xl bg-white p-6 shadow md:flex-row md:items-center md:justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">
            {{ t('stadiums.title') }}
          </h1>

          <p class="mt-2 text-gray-600">
            {{ t('stadiums.subtitle') }}
          </p>
        </div>

        <RouterLink
          :to="{ name: 'tournaments' }"
          class="rounded-lg bg-gray-900 px-4 py-2 text-center font-semibold text-white hover:bg-black"
        >
          {{ t('stadiums.backToTournaments') }}
        </RouterLink>
      </header>

      <section v-if="error" class="rounded-lg bg-red-100 p-4">
        <h2 class="font-semibold text-red-900">
          {{ t('stadiums.errorTitle') }}
        </h2>

        <pre class="mt-2 whitespace-pre-wrap text-sm text-red-800">{{ error }}</pre>
      </section>

      <section v-if="success" class="rounded-lg bg-green-100 p-4 text-green-800">
        {{ success }}
      </section>

      <section
        v-if="canManageStadiums"
        class="rounded-2xl bg-white p-6 shadow"
      >
        <h2 class="text-xl font-semibold text-gray-900">
          {{ t('stadiums.createTitle') }}
        </h2>

        <p class="mt-1 text-sm text-gray-600">
          {{ t('stadiums.createSubtitle') }}
        </p>

        <form class="mt-5 grid gap-5 md:grid-cols-2" @submit.prevent="createStadium">
          <div>
            <label class="block text-sm font-medium text-gray-700">
              {{ t('stadiums.fields.name') }}
            </label>

            <input
              v-model="form.name"
              type="text"
              class="mt-1 w-full rounded-lg border border-gray-300 p-3 focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
              :placeholder="t('stadiums.placeholders.name')"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">
              {{ t('stadiums.fields.city') }}
            </label>

            <input
              v-model="form.city"
              type="text"
              class="mt-1 w-full rounded-lg border border-gray-300 p-3 focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
              :placeholder="t('stadiums.placeholders.city')"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">
              {{ t('stadiums.fields.address') }}
            </label>

            <input
              v-model="form.address"
              type="text"
              class="mt-1 w-full rounded-lg border border-gray-300 p-3 focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
              :placeholder="t('stadiums.placeholders.address')"
            />
          </div>

          <div class="md:col-span-2">
            <button
              type="submit"
              class="rounded-lg bg-green-600 px-5 py-3 font-semibold text-white hover:bg-green-700 disabled:opacity-50"
              :disabled="loading"
            >
              {{ loading ? t('stadiums.saving') : t('stadiums.createButton') }}
            </button>
          </div>
        </form>
      </section>

      <section class="rounded-2xl bg-white p-6 shadow">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-semibold text-gray-900">
            {{ t('stadiums.allTitle') }}
          </h2>

          <button
            class="rounded-lg bg-gray-900 px-4 py-2 text-sm font-semibold text-white hover:bg-black disabled:opacity-50"
            :disabled="loading"
            @click="fetchStadiums"
          >
            {{ t('stadiums.refresh') }}
          </button>
        </div>

        <div v-if="loading" class="mt-6 text-gray-600">
          {{ t('stadiums.loading') }}
        </div>

        <div
          v-else-if="stadiums.length === 0"
          class="mt-6 rounded-xl border border-dashed border-gray-300 p-8 text-center"
        >
          <p class="text-gray-600">
            {{ t('stadiums.empty') }}
          </p>
        </div>

        <div v-else class="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <article
            v-for="stadium in stadiums"
            :key="stadium.id"
            class="rounded-xl border border-gray-200 bg-white p-5 shadow-sm transition hover:-translate-y-1 hover:shadow-md"
          >
            <div>
              <h3 class="text-lg font-bold text-gray-900">
                {{ stadium.name }}
              </h3>

              <p class="mt-1 text-sm text-gray-600">
                {{ stadium.city }}
              </p>
            </div>

            <div class="mt-4 space-y-2 text-sm text-gray-700">
              <p>
                <span class="font-semibold">
                  {{ t('stadiums.labels.address') }}:
                </span>
                {{ stadium.address || t('stadiums.notSet') }}
              </p>
            </div>
            <!--
            <div
              v-if="canManageStadiums"
              class="mt-5"
            >
              <button
                type="button"
                class="rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700 disabled:opacity-50"
                :disabled="loading"
                @click="deleteStadium(stadium)"
              >
                {{ t('stadiums.deleteButton') }}
              </button>
            </div>
            -->
          </article>
        </div>
      </section>
    </div>
  </main>
</template>