<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'
import instance_api from '@/services/api.js'
import { useAuth } from '@/services/useAuth.js'

const { t, locale } = useI18n()
const { role, isAuthenticated, isLoaded, loadUser } = useAuth()

const tournaments = ref([])
const loading = ref(false)
const error = ref('')

const canManageTournaments = computed(() => {
  return isAuthenticated.value && role.value === 'sports_admin'
})

function normalizeTournaments(data) {
  return Array.isArray(data) ? data : data.results || []
}

function extractError(err) {
  if (err.response?.data) {
    return JSON.stringify(err.response.data, null, 2)
  }

  return err.message || t('tournaments.errors.generic')
}

function formatDate(value) {
  if (!value) {
    return t('tournaments.notSet')
  }

  const browserLocale = locale.value === 'el' ? 'el-GR' : 'en-US'

  return new Date(value).toLocaleDateString(browserLocale)
}

// Simple mapping for translation using localization.
function translatedStatus(status) {
  const statusMap = {
    Scheduled: 'tournaments.status.scheduled',
    Completed: 'tournaments.status.completed',
    Cancelled: 'tournaments.status.cancelled',
  }

  return statusMap[status] ? t(statusMap[status]) : status
}

async function fetchTournaments() {
  loading.value = true
  error.value = ''
  // No need for authentication here.
  try {
    const response = await instance_api.get('/tournaments/')
    tournaments.value = normalizeTournaments(response.data)
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

  await fetchTournaments()
})
</script>

<template>
  <main class="min-h-screen bg-gray-100 p-6">
    <div class="mx-auto max-w-6xl space-y-6">
      <header class="flex flex-col gap-4 rounded-2xl bg-white p-6 shadow md:flex-row md:items-center md:justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">
            {{ t('tournaments.title') }}
          </h1>

          <p class="mt-2 text-gray-600">
            {{ t('tournaments.subtitle') }}
          </p>
        </div>

        <RouterLink
          v-if="canManageTournaments"
          :to="{ name: 'tournament-create' }"
          class="rounded-lg bg-green-600 px-4 py-2 text-center font-semibold text-white hover:bg-green-700"
        >
          {{ t('tournaments.createButton') }}
        </RouterLink>
      </header>

      <section v-if="error" class="rounded-lg bg-red-100 p-4">
        <h2 class="font-semibold text-red-900">
          {{ t('tournaments.errorTitle') }}
        </h2>

        <pre class="mt-2 whitespace-pre-wrap text-sm text-red-800">{{ error }}</pre>
      </section>

      <section class="rounded-2xl bg-white p-6 shadow">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-semibold text-gray-900">
            {{ t('tournaments.allTitle') }}
          </h2>
        </div>

        <div v-if="loading" class="mt-6 text-gray-600">
          {{ t('tournaments.loading') }}
        </div>

        <div
          v-else-if="tournaments.length === 0"
          class="mt-6 rounded-xl border border-dashed border-gray-300 p-8 text-center"
        >
          <p class="text-gray-600">
            {{ t('tournaments.empty') }}
          </p>

          <RouterLink
            v-if="canManageTournaments"
            :to="{ name: 'tournament-create' }"
            class="mt-4 inline-block rounded-lg bg-green-600 px-4 py-2 font-semibold text-white hover:bg-green-700"
          >
            {{ t('tournaments.createFirst') }}
          </RouterLink>

          <p
            v-else
            class="mt-3 text-sm text-gray-500"
          >
            {{ t('tournaments.emptyVisitorMessage') }}
          </p>
        </div>

        <div v-else class="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <article
            v-for="tournament in tournaments"
            :key="tournament.id"
            class="rounded-xl border border-gray-200 bg-white p-5 shadow-sm transition hover:-translate-y-1 hover:shadow-md"
          >
            <div class="flex items-start justify-between gap-4">
              <div>
                <h3 class="text-lg font-bold text-gray-900">
                  {{ tournament.name }}
                </h3>

                <p class="mt-1 text-sm text-gray-600">
                  {{ tournament.sport }}
                </p>
              </div>

              <span class="rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-800">
                {{ translatedStatus(tournament.status) }}
              </span>
            </div>

            <div class="mt-4 space-y-2 text-sm text-gray-700">
              <p>
                <span class="font-semibold">
                  {{ t('tournaments.labels.location') }}:
                </span>
                {{ tournament.location }}
              </p>

              <p>
                <span class="font-semibold">
                  {{ t('tournaments.labels.starts') }}:
                </span>
                {{ formatDate(tournament.start_date) }}
              </p>

              <p>
                <span class="font-semibold">
                  {{ t('tournaments.labels.ends') }}:
                </span>
                {{ formatDate(tournament.end_date) }}
              </p>

              <p v-if="tournament.teams">
                <span class="font-semibold">
                  {{ t('tournaments.labels.teams') }}:
                </span>
                {{ tournament.teams.length }}
              </p>
            </div>

            <div class="mt-5 flex gap-2">
              <RouterLink
                :to="{ name: 'tournament', params: { id: tournament.id } }"
                class="flex-1 rounded-lg bg-gray-900 px-3 py-2 text-center text-sm font-semibold text-white hover:bg-black"
              >
                {{ t('tournaments.viewDetails') }}
              </RouterLink>
            </div>
          </article>
        </div>
      </section>
    </div>
  </main>
</template>