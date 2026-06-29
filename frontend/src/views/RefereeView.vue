<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { matchApi } from '@/services/api.js'
import { useAuth } from '@/services/useAuth.js'

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

function isOverdue(match) {
  if (!match.scheduled_date) {
    return false
  }

  return new Date(match.scheduled_date) < new Date()
}

function extractError(err) {
  if (err.response?.data) {
    return JSON.stringify(err.response.data, null, 2)
  }

  return err.message || 'Something went wrong.'
}

function formatDateTime(value) {
  if (!value) {
    return 'Not scheduled'
  }

  return new Date(value).toLocaleString()
}

function stadiumLabel(match) {
  if (match.stadium_name && match.stadium_city) {
    return `${match.stadium_name} - ${match.stadium_city}`
  }

  if (match.stadium_name) {
    return match.stadium_name
  }

  return 'No stadium assigned'
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
          Referee Dashboard
        </h1>

        <p class="mt-3 max-w-2xl text-gray-600">
          View your upcoming assigned matches and open each match sheet.
        </p>
      </header>

      <section
        v-if="!isLoaded"
        class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm"
      >
        <p class="text-gray-600">
          Checking permissions...
        </p>
      </section>

      <section
        v-else-if="!canViewRefereePage"
        class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm"
      >
        <h2 class="text-2xl font-bold text-gray-900">
          Access denied
        </h2>

        <p class="mt-2 text-gray-600">
          This page is available only to referees.
        </p>

        <RouterLink
          :to="{ name: 'tournaments' }"
          class="mt-5 inline-block rounded-xl bg-gray-900 px-5 py-2 font-semibold text-white hover:bg-black"
        >
          Back to tournaments
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
              <h2>
                   Pending Assigned Matches
              </h2>

              <p>
                    Matches assigned to you that still need a final result.
              </p>
            </div>

            <button
              class="rounded-xl border border-gray-300 px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-50 disabled:opacity-50"
              :disabled="loading"
              @click="loadAssignedMatches"
            >
              Refresh
            </button>
          </div>

          <p
            v-if="loading"
            class="mt-6 text-gray-600"
          >
            Loading assigned matches...
          </p>

          <p
            v-else-if="matches.length === 0"
            class="mt-6 rounded-xl border border-dashed border-gray-300 p-6 text-gray-600"
          >
            You do not have any upcoming assigned matches.
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
                    {{ match.team1_name }} vs {{ match.team2_name }}
                  </h3>

                  <p class="mt-1 text-sm text-gray-600">
                    Tournament: {{ match.tournament_name }}
                  </p>

                  <p class="mt-1 text-sm text-gray-600">
                    Date: {{ formatDateTime(match.scheduled_date) }}
                  </p>

                  <p class="mt-1 text-sm text-gray-600">
                    Stadium: {{ stadiumLabel(match) }}
                  </p>
                </div>

                <span
                  v-if="isOverdue(match)"
                  class="w-fit rounded-full bg-red-50 px-3 py-1 text-sm font-semibold text-red-700"
                >
                Awaiting result
                </span>

                <span class="w-fit rounded-full bg-blue-50 px-3 py-1 text-sm font-semibold text-blue-700">
                  {{ match.match_status }}
                </span>
              </div>

              <div class="mt-5 flex justify-end">
                <RouterLink
                  :to="{ name: 'match', params: { id: match.id } }"
                  class="rounded-xl bg-purple-600 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-700"
                >
                  Open Match Sheet
                </RouterLink>
              </div>
            </article>
          </div>
        </section>
      </template>
    </div>
  </main>
</template>