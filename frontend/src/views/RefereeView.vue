<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { matchApi } from '@/services/api.js'
import { useAuth } from '@/services/useAuth.js'

const { t, locale } = useI18n()
const { role, isAuthenticated, isLoaded, loadUser } = useAuth()

const matches = ref([])
const loading = ref(false)
const error = ref('')

const canViewRefereePage = computed(() => {
  return isAuthenticated.value && role.value === 'referee'
})

function normalizeList(data) {
  return Array.isArray(data) ? data : data.results || []
}

function isOverdue(match) { // Adds is overdue message on the match
  if (!match.scheduled_date) {
    return false
  }

  return new Date(match.scheduled_date) < new Date()
}

function extractError(err) {
  if (err.response?.data?.detail) {
    return err.response.data.detail
  }

  if (err.response?.data) {
    return JSON.stringify(err.response.data, null, 2)
  }

  return err.message || t('referee.errors.generic')
}

function formatDateTime(value) {
  if (!value) {
    return t('referee.match.notScheduled')
  }

  const browserLocale = locale.value === 'el' ? 'el-GR' : 'en-US'

  return new Date(value).toLocaleString(browserLocale)
}

function stadiumLabel(match) {
  if (match.stadium_name && match.stadium_city) {
    return `${match.stadium_name} - ${match.stadium_city}`
  }

  if (match.stadium_name) {
    return match.stadium_name
  }

  return t('referee.match.noStadiumAssigned')
}

function translatedMatchStatus(status) {
  const statusMap = {
    Scheduled: 'referee.status.scheduled',
    Completed: 'referee.status.completed',
    Cancelled: 'referee.status.cancelled',
  }

  return statusMap[status] ? t(statusMap[status]) : status
}

async function loadAssignedMatches() {
  if (!canViewRefereePage.value) {
    matches.value = []
    return
  }

  loading.value = true
  error.value = ''

  try {
    const response = await matchApi.getAssignedToMe()

    // Sorts by date after converting scheduled dates to Javascript Date objects.
    matches.value = normalizeList(response.data).sort((a, b) => {
      return new Date(a.scheduled_date) - new Date(b.scheduled_date)
    })
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

  await loadAssignedMatches()
})
</script>

<template>
  <main class="min-h-screen bg-gray-50 px-6 py-10">
    <div class="mx-auto max-w-6xl space-y-8">
      <header class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
        <h1 class="text-4xl font-bold text-gray-900">
          {{ t('referee.title') }}
        </h1>

        <p class="mt-3 max-w-2xl text-gray-600">
          {{ t('referee.subtitle') }}
        </p>
      </header>

      <section
        v-if="!isLoaded"
        class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm"
      >
        <p class="text-gray-600">
          {{ t('referee.checkingPermissions') }}
        </p>
      </section>

      <section
        v-else-if="!canViewRefereePage"
        class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm"
      >
        <h2 class="text-2xl font-bold text-gray-900">
          {{ t('referee.accessDeniedTitle') }}
        </h2>

        <p class="mt-2 text-gray-600">
          {{ t('referee.accessDeniedMessage') }}
        </p>

        <RouterLink
          :to="{ name: 'tournaments' }"
          class="mt-5 inline-block rounded-xl bg-gray-900 px-5 py-2 font-semibold text-white hover:bg-black"
        >
          {{ t('referee.backToTournaments') }}
        </RouterLink>
      </section>

      <template v-else>
        <section
          v-if="error"
          class="rounded-xl bg-red-50 p-4 text-sm text-red-700"
        >
          <pre class="whitespace-pre-wrap">{{ error }}</pre>
        </section>

        <section class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 class="text-2xl font-bold text-gray-900">
                {{ t('referee.pendingTitle') }}
              </h2>

              <p class="mt-1 text-sm text-gray-600">
                {{ t('referee.pendingSubtitle') }}
              </p>
            </div>

            <button
              class="rounded-xl border border-gray-300 px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-50 disabled:opacity-50"
              :disabled="loading"
              @click="loadAssignedMatches"
            >
              {{ t('referee.refresh') }}
            </button>
          </div>

          <p
            v-if="loading"
            class="mt-6 text-gray-600"
          >
            {{ t('referee.loadingMatches') }}
          </p>

          <p
            v-else-if="matches.length === 0"
            class="mt-6 rounded-xl border border-dashed border-gray-300 p-6 text-gray-600"
          >
            {{ t('referee.emptyMatches') }}
          </p>

          <div
            v-else
            class="mt-6 space-y-4"
          >
            <article
              v-for="match in matches"
              :key="match.id"
              class="rounded-xl border border-gray-200 p-5"
            >
              <div class="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                <div>
                  <h3 class="text-xl font-bold text-gray-900">
                    {{ match.team1_name }}
                    {{ t('referee.match.versus') }}
                    {{ match.team2_name }}
                  </h3>

                  <p class="mt-1 text-sm text-gray-600">
                    {{ t('referee.labels.tournament') }}:
                    {{ match.tournament_name }}
                  </p>

                  <p class="mt-1 text-sm text-gray-600">
                    {{ t('referee.labels.date') }}:
                    {{ formatDateTime(match.scheduled_date) }}
                  </p>

                  <p class="mt-1 text-sm text-gray-600">
                    {{ t('referee.labels.stadium') }}:
                    {{ stadiumLabel(match) }}
                  </p>
                </div>

                <div class="flex flex-col gap-2 md:items-end">
                  <span
                    v-if="isOverdue(match)"
                    class="w-fit rounded-full bg-red-50 px-3 py-1 text-sm font-semibold text-red-700"
                  >
                    {{ t('referee.awaitingResult') }}
                  </span>

                  <span class="w-fit rounded-full bg-blue-50 px-3 py-1 text-sm font-semibold text-blue-700">
                    {{ translatedMatchStatus(match.match_status) }}
                  </span>
                </div>
              </div>

              <div class="mt-5 flex justify-end">
                <RouterLink
                  :to="{ name: 'match', params: { id: match.id } }"
                  class="rounded-xl bg-purple-600 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-700"
                >
                  {{ t('referee.openMatchSheet') }}
                </RouterLink>
              </div>
            </article>
          </div>
        </section>
      </template>
    </div>
  </main>
</template>