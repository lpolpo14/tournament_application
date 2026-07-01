<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'
import instance_api from '@/services/api.js'
import { useAuth } from '@/services/useAuth.js'

const router = useRouter()
const { t } = useI18n()

const { role, isAuthenticated, isLoaded, loadUser } = useAuth()

const loading = ref(false)
const error = ref('')

const canManageTournaments = computed(() => {
  return isAuthenticated.value && role.value === 'sports_admin'
})

const form = ref({
  name: '',
  sport: '',
  location: '',
  start_date: '',
  end_date: '',
  status: 'Scheduled',
})

function extractError(err) {
  if (err.response?.data) {
    return JSON.stringify(err.response.data, null, 2)
  }

  return err.message || t('tournamentCreate.errors.generic')
}

function toApiDateTime(datetimeLocalValue) {
  // Used when saving dates to the backend models.
  if (!datetimeLocalValue) {
    return null
  }

  return new Date(datetimeLocalValue).toISOString()
}

async function createTournament() {
  if (!canManageTournaments.value) {
    error.value = t('tournamentCreate.errors.createForbidden')
    return
  }

  loading.value = true
  error.value = ''

  try {
    const payload = {
      name: form.value.name,
      sport: form.value.sport,
      location: form.value.location,
      start_date: toApiDateTime(form.value.start_date),
      end_date: toApiDateTime(form.value.end_date),
      status: 'Scheduled',
    }

    const response = await instance_api.post('/tournaments/', payload)

    const createdTournamentId = response.data.id

    if (createdTournamentId) {
      router.push({
        name: 'tournament',
        params: { id: createdTournamentId },
      })
    } else {
      router.push({ name: 'tournaments' })
    }
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
})
</script>

<template>
  <main class="min-h-screen bg-gray-100 p-6">
    <div class="mx-auto max-w-3xl space-y-6">
      <header class="rounded-2xl bg-white p-6 shadow">
        <RouterLink
          :to="{ name: 'tournaments' }"
          class="text-sm font-semibold text-blue-700 hover:text-blue-900"
        >
          {{ t('tournamentCreate.back') }}
        </RouterLink>

        <h1 class="mt-4 text-3xl font-bold text-gray-900">
          {{ t('tournamentCreate.title') }}
        </h1>

        <p class="mt-2 text-gray-600">
          {{ t('tournamentCreate.subtitle') }}
        </p>
      </header>

      <section v-if="error" class="rounded-lg bg-red-100 p-4">
        <h2 class="font-semibold text-red-900">
          {{ t('tournamentCreate.errorTitle') }}
        </h2>

        <pre class="mt-2 whitespace-pre-wrap text-sm text-red-800">{{ error }}</pre>
      </section>

      <section
        v-if="!isLoaded"
        class="rounded-2xl bg-white p-6 shadow"
      >
        <p class="text-gray-600">
          {{ t('tournamentCreate.checkingPermissions') }}
        </p>
      </section>

      <section
        v-else-if="!canManageTournaments"
        class="rounded-2xl bg-white p-6 shadow"
      >
        <h2 class="text-xl font-bold text-gray-900">
          {{ t('tournamentCreate.accessDeniedTitle') }}
        </h2>

        <p class="mt-2 text-gray-600">
          {{ t('tournamentCreate.accessDeniedMessage') }}
        </p>

        <RouterLink
          :to="{ name: 'tournaments' }"
          class="mt-5 inline-block rounded-lg bg-gray-900 px-4 py-2 font-semibold text-white hover:bg-black"
        >
          {{ t('tournamentCreate.backToTournaments') }}
        </RouterLink>
      </section>

      <section
        v-else
        class="rounded-2xl bg-white p-6 shadow"
      >
        <form class="space-y-5" @submit.prevent="createTournament">
          <div>
            <label class="block text-sm font-medium text-gray-700">
              {{ t('tournamentCreate.fields.name') }}
            </label>

            <input
              v-model="form.name"
              type="text"
              class="mt-1 w-full rounded-lg border border-gray-300 p-3 focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
              :placeholder="t('tournamentCreate.placeholders.name')"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">
              {{ t('tournamentCreate.fields.sport') }}
            </label>

            <input
              v-model="form.sport"
              type="text"
              class="mt-1 w-full rounded-lg border border-gray-300 p-3 focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
              :placeholder="t('tournamentCreate.placeholders.sport')"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">
              {{ t('tournamentCreate.fields.location') }}
            </label>

            <input
              v-model="form.location"
              type="text"
              class="mt-1 w-full rounded-lg border border-gray-300 p-3 focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
              :placeholder="t('tournamentCreate.placeholders.location')"
              required
            />
          </div>

          <div class="grid gap-5 md:grid-cols-2">
            <div>
              <label class="block text-sm font-medium text-gray-700">
                {{ t('tournamentCreate.fields.startDate') }}
              </label>

              <input
                v-model="form.start_date"
                type="datetime-local"
                class="mt-1 w-full rounded-lg border border-gray-300 p-3 focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
                required
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">
                {{ t('tournamentCreate.fields.endDate') }}
              </label>

              <input
                v-model="form.end_date"
                type="datetime-local"
                class="mt-1 w-full rounded-lg border border-gray-300 p-3 focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
                required
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">
              {{ t('tournamentCreate.fields.status') }}
            </label>

            <div class="rounded-xl bg-gray-50 p-4 text-sm text-gray-600">
              {{ t('tournamentCreate.statusHelp') }}
              <span class="font-semibold text-gray-900">
                {{ t('tournaments.status.scheduled') }}
              </span>.
            </div>
          </div>

          <div class="flex flex-col gap-3 pt-4 sm:flex-row">
            <button
              type="submit"
              class="rounded-lg bg-green-600 px-5 py-3 font-semibold text-white hover:bg-green-700 disabled:opacity-50"
              :disabled="loading"
            >
              {{ loading ? t('tournamentCreate.loading') : t('tournamentCreate.submit') }}
            </button>

            <RouterLink
              :to="{ name: 'tournaments' }"
              class="rounded-lg bg-gray-200 px-5 py-3 text-center font-semibold text-gray-800 hover:bg-gray-300"
            >
              {{ t('tournamentCreate.cancel') }}
            </RouterLink>
          </div>
        </form>
      </section>
    </div>
  </main>
</template>