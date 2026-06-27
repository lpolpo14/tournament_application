<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { playerApi } from '@/services/api.js'

const route = useRoute()

const playerData = ref(null)
const loading = ref(false)
const error = ref('')

const player = computed(() => {
  return playerData.value?.player ?? null
})

const summary = computed(() => {
  return playerData.value?.summary ?? {
    played_matches: 0,
    goals: 0,
    fouls: 0,
    yellow_cards: 0,
    red_cards: 0,
  }
})

const matchHistory = computed(() => {
  return playerData.value?.match_history ?? []
})

async function loadPlayerStatistics() {
  loading.value = true
  error.value = ''

  try {
    const response = await playerApi.getStatistics(route.params.id)
    playerData.value = response.data
  } catch (err) {
    error.value = 'Could not load player statistics.'
  } finally {
    loading.value = false
  }
}

function formatDateTime(value) {
  if (!value) {
    return 'Not set'
  }

  return new Date(value).toLocaleString()
}

function stadiumLabel(match) {
  const parts = [match.stadium_name, match.stadium_city].filter(Boolean)

  if (parts.length === 0) {
    return 'No stadium assigned'
  }

  return parts.join(', ')
}

function scoreLabel(match) {
  if (match.team_score === null || match.opponent_score === null) {
    return '-'
  }

  return `${match.team_score} - ${match.opponent_score}`
}

function resultClass(result) {
  return {
    'text-green-700': result === 'Win',
    'text-red-700': result === 'Loss',
    'text-gray-700': result === 'Draw',
    'text-blue-700': result === 'Not completed',
  }
}

onMounted(loadPlayerStatistics)
</script>

<template>
  <main class="min-h-screen bg-gray-50 px-6 py-10">
    <div class="mx-auto max-w-7xl space-y-8">
      <RouterLink
        :to="{ name: 'teams' }"
        class="text-sm font-semibold text-green-700 hover:text-green-800"
      >
        ← Back to teams
      </RouterLink>

      <p
        v-if="loading"
        class="text-gray-600"
      >
        Loading player statistics...
      </p>

      <p
        v-else-if="error"
        class="rounded-xl bg-red-50 p-4 text-sm text-red-700"
      >
        {{ error }}
      </p>

      <template v-else-if="player">
        <header class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <h1 class="text-4xl font-bold text-gray-900">
                {{ player.full_name }}
              </h1>

              <p class="mt-2 text-lg text-gray-600">
                {{ player.position_display ?? player.position }}
              </p>
            </div>

            <div class="rounded-2xl bg-gray-50 px-6 py-4 text-center">
              <p class="text-sm font-semibold text-gray-500">
                Main Shirt Number
              </p>

              <p class="mt-1 text-3xl font-bold text-gray-900">
                #{{ player.main_shirt_number }}
              </p>
            </div>
          </div>
        </header>

        <section class="grid gap-4 md:grid-cols-5">
          <article class="rounded-2xl border border-gray-200 bg-white p-5 text-center shadow-sm">
            <p class="text-sm font-semibold text-gray-500">
              Matches
            </p>

            <p class="mt-2 text-3xl font-bold text-gray-900">
              {{ summary.played_matches }}
            </p>
          </article>

          <article class="rounded-2xl border border-gray-200 bg-white p-5 text-center shadow-sm">
            <p class="text-sm font-semibold text-gray-500">
              Goals
            </p>

            <p class="mt-2 text-3xl font-bold text-gray-900">
              {{ summary.goals }}
            </p>
          </article>

          <article class="rounded-2xl border border-gray-200 bg-white p-5 text-center shadow-sm">
            <p class="text-sm font-semibold text-gray-500">
              Fouls
            </p>

            <p class="mt-2 text-3xl font-bold text-gray-900">
              {{ summary.fouls }}
            </p>
          </article>

          <article class="rounded-2xl border border-gray-200 bg-white p-5 text-center shadow-sm">
            <p class="text-sm font-semibold text-gray-500">
              Yellow Cards
            </p>

            <p class="mt-2 text-3xl font-bold text-yellow-600">
              {{ summary.yellow_cards }}
            </p>
          </article>

          <article class="rounded-2xl border border-gray-200 bg-white p-5 text-center shadow-sm">
            <p class="text-sm font-semibold text-gray-500">
              Red Cards
            </p>

            <p class="mt-2 text-3xl font-bold text-red-700">
              {{ summary.red_cards }}
            </p>
          </article>
        </section>

        <section class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 class="text-2xl font-bold text-gray-900">
            Match History
          </h2>

          <p class="mt-1 text-sm text-gray-600">
            Match-by-match statistics recorded for this player.
          </p>

          <p
            v-if="matchHistory.length === 0"
            class="mt-6 rounded-xl border border-dashed border-gray-300 p-6 text-gray-600"
          >
            No match statistics have been recorded for this player yet.
          </p>

          <div
            v-else
            class="mt-6 overflow-x-auto rounded-xl border border-gray-200"
          >
            <table class="w-full text-left text-sm">
              <thead class="bg-gray-50 text-gray-700">
                <tr>
                  <th class="px-4 py-3">Match</th>
                  <th class="px-4 py-3">Tournament</th>
                  <th class="px-4 py-3">Date</th>
                  <th class="px-4 py-3">Stadium</th>
                  <th class="px-4 py-3 text-center">Score</th>
                  <th class="px-4 py-3 text-center">Result</th>
                  <th class="px-4 py-3 text-center">G</th>
                  <th class="px-4 py-3 text-center">F</th>
                  <th class="px-4 py-3 text-center">YC</th>
                  <th class="px-4 py-3 text-center">RC</th>
                </tr>
              </thead>

              <tbody class="divide-y divide-gray-200">
                <tr
                  v-for="match in matchHistory"
                  :key="match.match_id"
                  class="hover:bg-gray-50"
                >
                  <td class="px-4 py-3 font-semibold text-gray-900">
                    {{ match.team_name }}
                    vs
                    {{ match.opponent_name }}
                  </td>

                  <td class="px-4 py-3 text-gray-700">
                    <RouterLink
                      :to="`/tournament/${match.tournament_id}`"
                      class="font-semibold text-green-700 hover:text-green-800"
                    >
                      {{ match.tournament_name }}
                    </RouterLink>
                  </td>

                  <td class="px-4 py-3 text-gray-700">
                    {{ formatDateTime(match.scheduled_date) }}
                  </td>

                  <td class="px-4 py-3 text-gray-700">
                    {{ stadiumLabel(match) }}
                  </td>

                  <td class="px-4 py-3 text-center font-semibold text-gray-900">
                    {{ scoreLabel(match) }}
                  </td>

                  <td
                    class="px-4 py-3 text-center font-semibold"
                    :class="resultClass(match.result)"
                  >
                    {{ match.result }}
                  </td>

                  <td class="px-4 py-3 text-center">
                    {{ match.goals }}
                  </td>

                  <td class="px-4 py-3 text-center">
                    {{ match.fouls }}
                  </td>

                  <td class="px-4 py-3 text-center">
                    {{ match.yellow_cards }}
                  </td>

                  <td class="px-4 py-3 text-center">
                    {{ match.red_cards }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </template>
    </div>
  </main>
</template>