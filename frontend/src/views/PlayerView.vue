<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { playerApi } from '@/services/api.js'

const route = useRoute()
const { t, locale } = useI18n()

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


const positions = [
  { value: 'UK', labelKey: 'players.positions.unknown' },
  { value: 'GK', labelKey: 'players.positions.goalkeeper' },
  { value: 'DF', labelKey: 'players.positions.defender' },
  { value: 'MF', labelKey: 'players.positions.midfielder' },
  { value: 'FR', labelKey: 'players.positions.forward' },
]

function getPositionLabel(positionValue) {
  const position = positions.find((item) => item.value === positionValue)
  return position ? t(position.labelKey) : positionValue
}

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
    error.value = t('player.errorLoad')
  } finally {
    loading.value = false
  }
}

function formatDateTime(value) {
  if (!value) {
    return t('player.notSet')
  }

  const browserLocale = locale.value === 'el' ? 'el-GR' : 'en-US'

  return new Date(value).toLocaleString(browserLocale)
}

function stadiumLabel(match) {
  const parts = [match.stadium_name, match.stadium_city].filter(Boolean)

  if (parts.length === 0) {
    return t('player.noStadiumAssigned')
  }

  return parts.join(', ')
}

function scoreLabel(match) {
  if (match.team_score === null || match.opponent_score === null) {
    return '-'
  }

  return `${match.team_score} - ${match.opponent_score}`
}

function translatedResult(result) {
  const resultMap = {
    Win: 'player.results.win',
    Loss: 'player.results.loss',
    Draw: 'player.results.draw',
    'Not completed': 'player.results.notCompleted',
  }

  return resultMap[result] ? t(resultMap[result]) : result
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
        {{ t('player.backToTeams') }}
      </RouterLink>

      <p
        v-if="loading"
        class="text-gray-600"
      >
        {{ t('player.loading') }}
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
                {{ getPositionLabel(player.position) }}
              </p>
            </div>

            <div class="rounded-2xl bg-gray-50 px-6 py-4 text-center">
              <p class="text-sm font-semibold text-gray-500">
                {{ t('player.mainShirtNumber') }}
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
              {{ t('player.stats.matches') }}
            </p>

            <p class="mt-2 text-3xl font-bold text-gray-900">
              {{ summary.played_matches }}
            </p>
          </article>

          <article class="rounded-2xl border border-gray-200 bg-white p-5 text-center shadow-sm">
            <p class="text-sm font-semibold text-gray-500">
              {{ t('player.stats.goals') }}
            </p>

            <p class="mt-2 text-3xl font-bold text-gray-900">
              {{ summary.goals }}
            </p>
          </article>

          <article class="rounded-2xl border border-gray-200 bg-white p-5 text-center shadow-sm">
            <p class="text-sm font-semibold text-gray-500">
              {{ t('player.stats.fouls') }}
            </p>

            <p class="mt-2 text-3xl font-bold text-gray-900">
              {{ summary.fouls }}
            </p>
          </article>

          <article class="rounded-2xl border border-gray-200 bg-white p-5 text-center shadow-sm">
            <p class="text-sm font-semibold text-gray-500">
              {{ t('player.stats.yellowCards') }}
            </p>

            <p class="mt-2 text-3xl font-bold text-yellow-600">
              {{ summary.yellow_cards }}
            </p>
          </article>

          <article class="rounded-2xl border border-gray-200 bg-white p-5 text-center shadow-sm">
            <p class="text-sm font-semibold text-gray-500">
              {{ t('player.stats.redCards') }}
            </p>

            <p class="mt-2 text-3xl font-bold text-red-700">
              {{ summary.red_cards }}
            </p>
          </article>
        </section>

        <section class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 class="text-2xl font-bold text-gray-900">
            {{ t('player.historyTitle') }}
          </h2>

          <p class="mt-1 text-sm text-gray-600">
            {{ t('player.historySubtitle') }}
          </p>

          <p
            v-if="matchHistory.length === 0"
            class="mt-6 rounded-xl border border-dashed border-gray-300 p-6 text-gray-600"
          >
            {{ t('player.emptyHistory') }}
          </p>

          <div
            v-else
            class="mt-6 overflow-x-auto rounded-xl border border-gray-200"
          >
            <table class="w-full text-left text-sm">
              <thead class="bg-gray-50 text-gray-700">
                <tr>
                  <th class="px-4 py-3">
                    {{ t('player.table.match') }}
                  </th>
                  <th class="px-4 py-3">
                    {{ t('player.table.tournament') }}
                  </th>
                  <th class="px-4 py-3">
                    {{ t('player.table.date') }}
                  </th>
                  <th class="px-4 py-3">
                    {{ t('player.table.stadium') }}
                  </th>
                  <th class="px-4 py-3 text-center">
                    {{ t('player.table.score') }}
                  </th>
                  <th class="px-4 py-3 text-center">
                    {{ t('player.table.result') }}
                  </th>
                  <th class="px-4 py-3 text-center">
                    {{ t('player.table.goalsShort') }}
                  </th>
                  <th class="px-4 py-3 text-center">
                    {{ t('player.table.foulsShort') }}
                  </th>
                  <th class="px-4 py-3 text-center">
                    {{ t('player.table.yellowCardsShort') }}
                  </th>
                  <th class="px-4 py-3 text-center">
                    {{ t('player.table.redCardsShort') }}
                  </th>
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
                    {{ t('player.versus') }}
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
                    {{ translatedResult(match.result) }}
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