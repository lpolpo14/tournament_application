<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'
import instance_api from '@/services/api.js'
import { useAuth } from '@/services/useAuth.js'

const route = useRoute()
const { t, locale } = useI18n()

const matchId = route.params.id

const { user, role, isAuthenticated, isLoaded, loadUser } = useAuth()

const isRefereeRole = computed(() => {
  return isAuthenticated.value && role.value === 'referee'
})

const isSportsAdminRole = computed(() => {
  return isAuthenticated.value && role.value === 'sports_admin'
})

const canAdminEditMatch = computed(() => {
  return (
    isSportsAdminRole.value &&
    match.value &&
    match.value.match_status !== 'Completed'
  )
})

const stadiums = ref([])
const referees = ref([])

const adminMatchForm = ref({
  stadium: '',
  referee: '',
  scheduled_date: '',
})

const canEditMatch = computed(() => {
  if (!isRefereeRole.value) {
    return false
  }

  if (!match.value?.referee || !user.value?.id) {
    return false
  }

  return Number(match.value.referee) === Number(user.value.id)
})

const match = ref(null)
const loading = ref(false)
const error = ref('')
const success = ref('')

const scoreForm = ref({
  team1_score: '',
  team2_score: '',
})

const matchPlayers = ref({
  team1: {
    id: null,
    team_name: '',
    players: [],
  },
  team2: {
    id: null,
    team_name: '',
    players: [],
  },
})

const playerStatistics = ref([])

function emptyStatisticForm() {
  return {
    player: '',
    goals: 0,
    fouls: 0,
    yellow_cards: 0,
    red_cards: 0,
  }
}

// Need two forms for each team.
const team1StatisticForm = ref(emptyStatisticForm())
const team2StatisticForm = ref(emptyStatisticForm())

const team1Statistics = computed(() => {
  if (!match.value) {
    return []
  }

  return playerStatistics.value.filter((entry) => {
    return Number(entry.team) === Number(match.value.team1)
  })
})

const team2Statistics = computed(() => {
  if (!match.value) {
    return []
  }

  return playerStatistics.value.filter((entry) => {
    return Number(entry.team) === Number(match.value.team2)
  })
})

function normalizeList(data) {
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

  return err.message || t('matchDetail.errors.generic')
}

function toDatetimeLocal(value) {
  if (!value) {
    return ''
  }

  const date = new Date(value)
  date.setMinutes(date.getMinutes() - date.getTimezoneOffset())

  return date.toISOString().slice(0, 16)
}

function toApiDateTime(datetimeLocalValue) {
  if (!datetimeLocalValue) {
    return null
  }

  return new Date(datetimeLocalValue).toISOString() // Used when sending/saving dates to backend models.
}

function formatDateTime(value) {
  if (!value) {
    return t('matchDetail.common.notSet')
  }

  const browserLocale = locale.value === 'el' ? 'el-GR' : 'en-US'

  return new Date(value).toLocaleString(browserLocale) // Language Sensitive
}

function teamLabel(side) {
  if (!match.value) {
    return t('matchDetail.common.team')
  }

  if (side === 'team1') {
    return match.value.team1_name || t('matchDetail.common.teamFallback', { id: match.value.team1 })
  }

  return match.value.team2_name || t('matchDetail.common.teamFallback', { id: match.value.team2 })
}

function stadiumLabel() {
  if (!match.value) {
    return t('matchDetail.common.noStadiumAssigned')
  }

  if (match.value.stadium_name && match.value.stadium_city) {
    return `${match.value.stadium_name} - ${match.value.stadium_city}`
  }

  if (match.value.stadium_name) {
    return match.value.stadium_name
  }

  if (match.value.location) {
    return match.value.location
  }

  return t('matchDetail.common.noStadiumAssigned')
}

function translatedStatus(status) {
  const statusMap = {
    Scheduled: 'matchDetail.status.scheduled',
    Completed: 'matchDetail.status.completed',
    Cancelled: 'matchDetail.status.cancelled',
  }

  return statusMap[status] ? t(statusMap[status]) : status
}

function editPlayerStatistic(entry) {
  const targetForm =
    Number(entry.team) === Number(match.value.team1)
      ? team1StatisticForm
      : team2StatisticForm

  targetForm.value = {
    player: entry.player,
    goals: entry.goals,
    fouls: entry.fouls,
    yellow_cards: entry.yellow_cards,
    red_cards: entry.red_cards,
  }
}

async function fetchStadiums() {
  const response = await instance_api.get('/stadiums/')
  stadiums.value = normalizeList(response.data)
}

async function fetchReferees() {
  const response = await instance_api.get('/auth/referees/')
  referees.value = normalizeList(response.data)
}

async function fetchMatchPlayers() {
  const response = await instance_api.get(`/matches/${matchId}/players/`)
  matchPlayers.value = response.data
}

async function fetchPlayerStatistics() {
  const response = await instance_api.get('/player-match-statistics/', {
    params: {
      match: matchId,
    },
  })

  playerStatistics.value = normalizeList(response.data)
}

async function updateMatchSettings() {
  if (!canAdminEditMatch.value) {
    error.value = t('matchDetail.errors.adminEditForbidden')
    return
  }

  loading.value = true
  clearMessages()

  try {
    const response = await instance_api.patch(
      `/matches/${matchId}/admin-update/`,
      {
        stadium: adminMatchForm.value.stadium,
        referee: adminMatchForm.value.referee,
        scheduled_date: toApiDateTime(adminMatchForm.value.scheduled_date),
      }
    )

    match.value = response.data

    adminMatchForm.value = {
      stadium: response.data.stadium ?? '',
      referee: response.data.referee ?? '',
      scheduled_date: toDatetimeLocal(response.data.scheduled_date),
    }

    success.value = t('matchDetail.success.settingsUpdated')
  } catch (err) {
    error.value = extractError(err)
  } finally {
    loading.value = false
  }
}

async function cancelMatch() {
  /*
   *  The sports administrator can only cancel a match that was not marked as complete.
   *  There is no remarking - it is definite.
   */
  if (!canAdminEditMatch.value) {
    error.value = t('matchDetail.errors.adminCancelForbidden')
    return
  }

  // Since this action is absolute, add a window to confirm.
  const confirmed = window.confirm(t('matchDetail.confirm.cancelMatch'))

  if (!confirmed) {
    return
  }

  loading.value = true
  clearMessages()

  try {
    const response = await instance_api.post(`/matches/${matchId}/cancel/`)

    match.value = response.data
    success.value = t('matchDetail.success.cancelled')
  } catch (err) {
    error.value = extractError(err)
  } finally {
    loading.value = false
  }
}

async function fetchMatch() {
  loading.value = true
  clearMessages()

  try {
    const response = await instance_api.get(`/matches/${matchId}/`)
    match.value = response.data

    adminMatchForm.value = {
      stadium: response.data.stadium ?? '',
      referee: response.data.referee ?? '',
      scheduled_date: toDatetimeLocal(response.data.scheduled_date),
    }

    scoreForm.value = {
      team1_score: response.data.team1_score ?? '',
      team2_score: response.data.team2_score ?? '',
    }
  } catch (err) {
    error.value = extractError(err)
  } finally {
    loading.value = false
  }
}

async function submitScore() {
  if (!canEditMatch.value) {
    error.value = t('matchDetail.errors.scoreForbidden')
    return
  }

  loading.value = true
  clearMessages()

  try {
    await instance_api.patch(`/matches/${matchId}/submit-score/`, {
      team1_score: Number(scoreForm.value.team1_score),
      team2_score: Number(scoreForm.value.team2_score),
    })

    success.value = t('matchDetail.success.scoreSaved')

    await fetchMatch()
  } catch (err) {
    error.value = extractError(err)
  } finally {
    loading.value = false
  }
}

async function savePlayerStatisticsForTeam(side) {
  /*
   * This function is tricky. There are two forms, so we must input the side
   * for which we want to submit the statistics. Apart from that, simple payload settings.
   */
  if (!canEditMatch.value) {
    error.value = t('matchDetail.errors.statisticsForbidden')
    return
  }

  loading.value = true
  clearMessages()

  try {
    const form =
      side === 'team1'
        ? team1StatisticForm.value
        : team2StatisticForm.value

    const teamId =
      side === 'team1'
        ? match.value.team1
        : match.value.team2

    const payload = {
      match: matchId,
      player: form.player,
      team: teamId,
      goals: Number(form.goals),
      fouls: Number(form.fouls),
      yellow_cards: Number(form.yellow_cards),
      red_cards: Number(form.red_cards),
      extra_statistics: {},
    }

    // Check if statistics for the user were already saved.
    const existingStatistic = playerStatistics.value.find((entry) => {
      return Number(entry.player) === Number(payload.player)
    })

    // If statistics were already saved, then we update the statistics, not create new.
    if (existingStatistic) {
      await instance_api.patch(
        `/player-match-statistics/${existingStatistic.id}/`,
        payload
      )

      success.value = t('matchDetail.success.statisticsUpdated')
    } else { // Since no existing statistics were found, we use another endpoint to create the object.
      await instance_api.post('/player-match-statistics/', payload)

      success.value = t('matchDetail.success.statisticsSaved')
    }

    if (side === 'team1') {
      team1StatisticForm.value = emptyStatisticForm()
    } else {
      team2StatisticForm.value = emptyStatisticForm()
    }

    await fetchPlayerStatistics()
  } catch (err) {
    error.value = extractError(err)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  loading.value = true
  clearMessages()

  try {
    if (!isLoaded.value) {
      await loadUser()
    }

    await Promise.all([
      fetchMatch(),
      fetchMatchPlayers(),
      fetchPlayerStatistics(),
    ])

    if (isSportsAdminRole.value) {
      await Promise.all([
        fetchStadiums(),
        fetchReferees(),
      ])
    }
  } catch (err) {
    error.value = extractError(err)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <main class="min-h-screen bg-gray-100 p-6">
    <div class="mx-auto max-w-5xl space-y-6">
      <header class="rounded-2xl bg-white p-6 shadow">
        <RouterLink
          :to="{ name: 'tournaments' }"
          class="text-sm font-semibold text-blue-700 hover:text-blue-900"
        >
          {{ t('matchDetail.back') }}
        </RouterLink>

        <div
          v-if="match"
          class="mt-4 flex flex-col gap-4 md:flex-row md:items-start md:justify-between"
        >
          <div>
            <h1 class="text-3xl font-bold text-gray-900">
              {{ teamLabel('team1') }}
              {{ t('matchDetail.common.versus') }}
              {{ teamLabel('team2') }}
            </h1>

            <p class="mt-2 text-gray-600">
              {{ t('matchDetail.subtitle') }}
            </p>
          </div>

          <span class="w-fit rounded-full bg-blue-100 px-4 py-2 text-sm font-semibold text-blue-800">
            {{ translatedStatus(match.match_status) }}
          </span>
        </div>

        <div v-else class="mt-4">
          <h1 class="text-3xl font-bold text-gray-900">
            {{ t('matchDetail.fallbackTitle') }}
          </h1>
        </div>
      </header>

      <section v-if="error" class="rounded-lg bg-red-100 p-4">
        <h2 class="font-semibold text-red-900">
          {{ t('matchDetail.errorTitle') }}
        </h2>

        <pre class="mt-2 whitespace-pre-wrap text-sm text-red-800">{{ error }}</pre>
      </section>

      <section v-if="success" class="rounded-lg bg-green-100 p-4 text-green-800">
        {{ success }}
      </section>

      <section v-if="loading" class="rounded-2xl bg-white p-6 shadow">
        <p class="text-gray-600">
          {{ t('matchDetail.loadingData') }}
        </p>
      </section>

      <template v-if="!loading && match">
        <section class="grid gap-4 md:grid-cols-5">
          <article class="rounded-2xl bg-white p-5 shadow">
            <p class="text-sm font-semibold text-gray-500">
              {{ t('matchDetail.summary.referee') }}
            </p>

            <p class="mt-1 text-lg font-bold text-gray-900">
              {{ match.referee_username || t('matchDetail.common.notAssigned') }}
            </p>
          </article>

          <article class="rounded-2xl bg-white p-5 shadow">
            <p class="text-sm font-semibold text-gray-500">
              {{ t('matchDetail.summary.team1') }}
            </p>

            <p class="mt-1 text-lg font-bold text-gray-900">
              {{ teamLabel('team1') }}
            </p>
          </article>

          <article class="rounded-2xl bg-white p-5 shadow">
            <p class="text-sm font-semibold text-gray-500">
              {{ t('matchDetail.summary.team2') }}
            </p>

            <p class="mt-1 text-lg font-bold text-gray-900">
              {{ teamLabel('team2') }}
            </p>
          </article>

          <article class="rounded-2xl bg-white p-5 shadow">
            <p class="text-sm font-semibold text-gray-500">
              {{ t('matchDetail.summary.date') }}
            </p>

            <p class="mt-1 text-lg font-bold text-gray-900">
              {{ formatDateTime(match.scheduled_date) }}
            </p>
          </article>

          <article class="rounded-2xl bg-white p-5 shadow">
            <p class="text-sm font-semibold text-gray-500">
              {{ t('matchDetail.summary.stadium') }}
            </p>

            <p class="mt-1 text-lg font-bold text-gray-900">
              {{ stadiumLabel() }}
            </p>
          </article>
        </section>

        <section class="rounded-2xl bg-white p-6 shadow">
          <h2 class="text-xl font-bold text-gray-900">
            {{ t('matchDetail.score.title') }}
          </h2>

          <div class="mt-4 rounded-xl bg-gray-100 px-6 py-8 text-center">
            <p class="text-sm font-semibold text-gray-500">
              {{ t('matchDetail.score.currentResult') }}
            </p>

            <p class="mt-2 text-5xl font-bold text-gray-900">
              {{ match.team1_score ?? '-' }}
              :
              {{ match.team2_score ?? '-' }}
            </p>

            <p class="mt-3 text-gray-600">
              {{ teamLabel('team1') }}
              {{ t('matchDetail.common.versus') }}
              {{ teamLabel('team2') }}
            </p>
          </div>
        </section>

        <section
          v-if="canAdminEditMatch"
          class="rounded-2xl bg-white p-6 shadow"
        >
          <div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
            <div>
              <h2 class="text-xl font-bold text-gray-900">
                {{ t('matchDetail.adminSettings.title') }}
              </h2>

              <p class="mt-1 text-sm text-gray-600">
                {{ t('matchDetail.adminSettings.subtitle') }}
              </p>
            </div>

            <button
              type="button"
              class="rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700 disabled:opacity-50"
              :disabled="loading"
              @click="cancelMatch"
            >
              {{ t('matchDetail.adminSettings.cancelMatch') }}
            </button>
          </div>

          <form
            class="mt-5 grid gap-4 md:grid-cols-3"
            @submit.prevent="updateMatchSettings"
          >
            <div>
              <label class="block text-sm font-medium text-gray-700">
                {{ t('matchDetail.adminSettings.stadium') }}
              </label>

              <select
                v-model="adminMatchForm.stadium"
                class="mt-1 w-full rounded-lg border border-gray-300 p-3"
                required
              >
                <option value="" disabled>
                  {{ t('matchDetail.adminSettings.selectStadium') }}
                </option>

                <option
                  v-for="stadium in stadiums"
                  :key="stadium.id"
                  :value="stadium.id"
                >
                  {{ stadium.name }} - {{ stadium.city }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">
                {{ t('matchDetail.adminSettings.referee') }}
              </label>

              <select
                v-model="adminMatchForm.referee"
                class="mt-1 w-full rounded-lg border border-gray-300 p-3"
                required
              >
                <option value="" disabled>
                  {{ t('matchDetail.adminSettings.selectReferee') }}
                </option>

                <option
                  v-for="referee in referees"
                  :key="referee.id"
                  :value="referee.id"
                >
                  {{ referee.username }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">
                {{ t('matchDetail.adminSettings.scheduledDate') }}
              </label>

              <input
                v-model="adminMatchForm.scheduled_date"
                type="datetime-local"
                class="mt-1 w-full rounded-lg border border-gray-300 p-3"
                required
              />
            </div>

            <div class="md:col-span-3">
              <button
                type="submit"
                class="rounded-lg bg-green-600 px-5 py-3 font-semibold text-white hover:bg-green-700 disabled:opacity-50"
                :disabled="loading"
              >
                {{ t('matchDetail.adminSettings.save') }}
              </button>
            </div>
          </form>
        </section>

        <section
          v-if="canEditMatch"
          class="rounded-2xl bg-white p-6 shadow"
        >
          <h2 class="text-xl font-bold text-gray-900">
            {{ t('matchDetail.refereeScore.title') }}
          </h2>

          <p class="mt-1 text-sm text-gray-600">
            {{ t('matchDetail.refereeScore.subtitle') }}
          </p>

          <form
            class="mt-5 grid gap-4 md:grid-cols-3"
            @submit.prevent="submitScore"
          >
            <div>
              <label class="block text-sm font-medium text-gray-700">
                {{ t('matchDetail.score.teamScore', { team: teamLabel('team1') }) }}
              </label>

              <input
                v-model="scoreForm.team1_score"
                type="number"
                min="0"
                class="mt-1 w-full rounded-lg border border-gray-300 p-3 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
                required
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">
                {{ t('matchDetail.score.teamScore', { team: teamLabel('team2') }) }}
              </label>

              <input
                v-model="scoreForm.team2_score"
                type="number"
                min="0"
                class="mt-1 w-full rounded-lg border border-gray-300 p-3 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
                required
              />
            </div>

            <div class="flex items-end">
              <button
                type="submit"
                class="w-full rounded-lg bg-purple-600 px-4 py-3 font-semibold text-white hover:bg-purple-700 disabled:opacity-50"
                :disabled="loading"
              >
                {{ t('matchDetail.score.saveScore') }}
              </button>
            </div>
          </form>
        </section>

        <section
          v-if="canEditMatch"
          class="rounded-2xl bg-white p-6 shadow"
        >
          <h2 class="text-xl font-bold text-gray-900">
            {{ t('matchDetail.statistics.teamTitle', { team: teamLabel('team1') }) }}
          </h2>

          <p class="mt-1 text-sm text-gray-600">
            {{ t('matchDetail.statistics.teamSubtitle', { team: teamLabel('team1') }) }}
          </p>

          <form
            class="mt-5 grid gap-4 md:grid-cols-2"
            @submit.prevent="savePlayerStatisticsForTeam('team1')"
          >
            <div>
              <label class="block text-sm font-medium text-gray-700">
                {{ t('matchDetail.statistics.player') }}
              </label>

              <select
                v-model="team1StatisticForm.player"
                class="mt-1 w-full rounded-lg border border-gray-300 p-3"
                required
              >
                <option value="" disabled>
                  {{ t('matchDetail.statistics.selectPlayer') }}
                </option>

                <option
                  v-for="player in matchPlayers.team1.players"
                  :key="player.player_id"
                  :value="player.player_id"
                >
                  #{{ player.shirt_number }} - {{ player.player_full_name }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">
                {{ t('matchDetail.statistics.goals') }}
              </label>

              <input
                v-model="team1StatisticForm.goals"
                type="number"
                min="0"
                class="mt-1 w-full rounded-lg border border-gray-300 p-3"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">
                {{ t('matchDetail.statistics.fouls') }}
              </label>

              <input
                v-model="team1StatisticForm.fouls"
                type="number"
                min="0"
                class="mt-1 w-full rounded-lg border border-gray-300 p-3"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">
                {{ t('matchDetail.statistics.yellowCards') }}
              </label>

              <input
                v-model="team1StatisticForm.yellow_cards"
                type="number"
                min="0"
                max="2"
                class="mt-1 w-full rounded-lg border border-gray-300 p-3"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">
                {{ t('matchDetail.statistics.redCards') }}
              </label>

              <input
                v-model="team1StatisticForm.red_cards"
                type="number"
                min="0"
                max="1"
                class="mt-1 w-full rounded-lg border border-gray-300 p-3"
              />
            </div>

            <div class="flex items-end">
              <button
                type="submit"
                class="w-full rounded-lg bg-purple-600 px-5 py-3 font-semibold text-white hover:bg-purple-700 disabled:opacity-50"
                :disabled="loading"
              >
                {{ t('matchDetail.statistics.saveTeamStatistics', { team: teamLabel('team1') }) }}
              </button>
            </div>
          </form>

          <div
            v-if="team1Statistics.length === 0"
            class="mt-6 rounded-xl border border-dashed border-gray-300 p-6 text-center text-gray-600"
          >
            {{ t('matchDetail.statistics.noTeamStatistics', { team: teamLabel('team1') }) }}
          </div>

          <div v-else class="mt-6 overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200 text-sm">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left font-semibold text-gray-700">
                    {{ t('matchDetail.statistics.player') }}
                  </th>
                  <th class="px-4 py-3 text-left font-semibold text-gray-700">
                    {{ t('matchDetail.statistics.shirt') }}
                  </th>
                  <th class="px-4 py-3 text-left font-semibold text-gray-700">
                    {{ t('matchDetail.statistics.goals') }}
                  </th>
                  <th class="px-4 py-3 text-left font-semibold text-gray-700">
                    {{ t('matchDetail.statistics.fouls') }}
                  </th>
                  <th class="px-4 py-3 text-left font-semibold text-gray-700">
                    {{ t('matchDetail.statistics.yellow') }}
                  </th>
                  <th class="px-4 py-3 text-left font-semibold text-gray-700">
                    {{ t('matchDetail.statistics.red') }}
                  </th>
                  <th class="px-4 py-3 text-right font-semibold text-gray-700">
                    {{ t('matchDetail.statistics.actions') }}
                  </th>
                </tr>
              </thead>

              <tbody class="divide-y divide-gray-200 bg-white">
                <tr
                  v-for="entry in team1Statistics"
                  :key="entry.id"
                >
                  <td class="px-4 py-3 font-medium text-gray-900">
                    {{ entry.player_full_name }}
                  </td>

                  <td class="px-4 py-3 text-gray-700">
                    {{ entry.shirt_number ?? '-' }}
                  </td>

                  <td class="px-4 py-3 text-gray-700">
                    {{ entry.goals }}
                  </td>

                  <td class="px-4 py-3 text-gray-700">
                    {{ entry.fouls }}
                  </td>

                  <td class="px-4 py-3 text-gray-700">
                    {{ entry.yellow_cards }}
                  </td>

                  <td class="px-4 py-3 text-gray-700">
                    {{ entry.red_cards }}
                  </td>

                  <td class="px-4 py-3 text-right">
                    <button
                      class="rounded-lg bg-gray-900 px-3 py-2 text-xs font-semibold text-white hover:bg-black"
                      @click="editPlayerStatistic(entry)"
                    >
                      {{ t('matchDetail.statistics.edit') }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section
          v-if="canEditMatch"
          class="rounded-2xl bg-white p-6 shadow"
        >
          <h2 class="text-xl font-bold text-gray-900">
            {{ t('matchDetail.statistics.teamTitle', { team: teamLabel('team2') }) }}
          </h2>

          <p class="mt-1 text-sm text-gray-600">
            {{ t('matchDetail.statistics.teamSubtitle', { team: teamLabel('team2') }) }}
          </p>

          <form
            class="mt-5 grid gap-4 md:grid-cols-2"
            @submit.prevent="savePlayerStatisticsForTeam('team2')"
          >
            <div>
              <label class="block text-sm font-medium text-gray-700">
                {{ t('matchDetail.statistics.player') }}
              </label>

              <select
                v-model="team2StatisticForm.player"
                class="mt-1 w-full rounded-lg border border-gray-300 p-3"
                required
              >
                <option value="" disabled>
                  {{ t('matchDetail.statistics.selectPlayer') }}
                </option>

                <option
                  v-for="player in matchPlayers.team2.players"
                  :key="player.player_id"
                  :value="player.player_id"
                >
                  #{{ player.shirt_number }} - {{ player.player_full_name }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">
                {{ t('matchDetail.statistics.goals') }}
              </label>

              <input
                v-model="team2StatisticForm.goals"
                type="number"
                min="0"
                class="mt-1 w-full rounded-lg border border-gray-300 p-3"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">
                {{ t('matchDetail.statistics.fouls') }}
              </label>

              <input
                v-model="team2StatisticForm.fouls"
                type="number"
                min="0"
                class="mt-1 w-full rounded-lg border border-gray-300 p-3"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">
                {{ t('matchDetail.statistics.yellowCards') }}
              </label>

              <input
                v-model="team2StatisticForm.yellow_cards"
                type="number"
                min="0"
                max="2"
                class="mt-1 w-full rounded-lg border border-gray-300 p-3"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">
                {{ t('matchDetail.statistics.redCards') }}
              </label>

              <input
                v-model="team2StatisticForm.red_cards"
                type="number"
                min="0"
                max="1"
                class="mt-1 w-full rounded-lg border border-gray-300 p-3"
              />
            </div>

            <div class="flex items-end">
              <button
                type="submit"
                class="w-full rounded-lg bg-purple-600 px-5 py-3 font-semibold text-white hover:bg-purple-700 disabled:opacity-50"
                :disabled="loading"
              >
                {{ t('matchDetail.statistics.saveTeamStatistics', { team: teamLabel('team2') }) }}
              </button>
            </div>
          </form>

          <div
            v-if="team2Statistics.length === 0"
            class="mt-6 rounded-xl border border-dashed border-gray-300 p-6 text-center text-gray-600"
          >
            {{ t('matchDetail.statistics.noTeamStatistics', { team: teamLabel('team2') }) }}
          </div>

          <div v-else class="mt-6 overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200 text-sm">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left font-semibold text-gray-700">
                    {{ t('matchDetail.statistics.player') }}
                  </th>
                  <th class="px-4 py-3 text-left font-semibold text-gray-700">
                    {{ t('matchDetail.statistics.shirt') }}
                  </th>
                  <th class="px-4 py-3 text-left font-semibold text-gray-700">
                    {{ t('matchDetail.statistics.goals') }}
                  </th>
                  <th class="px-4 py-3 text-left font-semibold text-gray-700">
                    {{ t('matchDetail.statistics.fouls') }}
                  </th>
                  <th class="px-4 py-3 text-left font-semibold text-gray-700">
                    {{ t('matchDetail.statistics.yellow') }}
                  </th>
                  <th class="px-4 py-3 text-left font-semibold text-gray-700">
                    {{ t('matchDetail.statistics.red') }}
                  </th>
                  <th class="px-4 py-3 text-right font-semibold text-gray-700">
                    {{ t('matchDetail.statistics.actions') }}
                  </th>
                </tr>
              </thead>

              <tbody class="divide-y divide-gray-200 bg-white">
                <tr
                  v-for="entry in team2Statistics"
                  :key="entry.id"
                >
                  <td class="px-4 py-3 font-medium text-gray-900">
                    {{ entry.player_full_name }}
                  </td>

                  <td class="px-4 py-3 text-gray-700">
                    {{ entry.shirt_number ?? '-' }}
                  </td>

                  <td class="px-4 py-3 text-gray-700">
                    {{ entry.goals }}
                  </td>

                  <td class="px-4 py-3 text-gray-700">
                    {{ entry.fouls }}
                  </td>

                  <td class="px-4 py-3 text-gray-700">
                    {{ entry.yellow_cards }}
                  </td>

                  <td class="px-4 py-3 text-gray-700">
                    {{ entry.red_cards }}
                  </td>

                  <td class="px-4 py-3 text-right">
                    <button
                      class="rounded-lg bg-gray-900 px-3 py-2 text-xs font-semibold text-white hover:bg-black"
                      @click="editPlayerStatistic(entry)"
                    >
                      {{ t('matchDetail.statistics.edit') }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>


        <!--
        <section
          v-else
          class="rounded-2xl bg-white p-6 shadow"
        >
          <h2 class="text-xl font-bold text-gray-900">
            {{ t('matchDetail.viewer.title') }}
          </h2>

          <p class="mt-1 text-sm text-gray-600">
            {{ t('matchDetail.viewer.subtitle') }}
          </p>

          <div class="mt-5 grid gap-4 md:grid-cols-3">
            <article class="rounded-xl border border-gray-200 p-4">
              <p class="text-sm font-semibold text-gray-500">
                {{ t('matchDetail.viewer.status') }}
              </p>

              <p class="mt-1 text-lg font-bold text-gray-900">
                {{ translatedStatus(match.match_status) }}
              </p>
            </article>

            <article class="rounded-xl border border-gray-200 p-4">
              <p class="text-sm font-semibold text-gray-500">
                {{ t('matchDetail.statistics.yellowCards') }}
              </p>

              <p class="mt-1 text-lg font-bold text-gray-900">
                {{ t('matchDetail.viewer.notRecordedYet') }}
              </p>
            </article>

            <article class="rounded-xl border border-gray-200 p-4">
              <p class="text-sm font-semibold text-gray-500">
                {{ t('matchDetail.statistics.redCards') }}
              </p>

              <p class="mt-1 text-lg font-bold text-gray-900">
                {{ t('matchDetail.viewer.notRecordedYet') }}
              </p>
            </article>
          </div>
        </section>

        -->
        <section class="rounded-2xl bg-white p-6 shadow">
          <h2 class="text-xl font-bold text-gray-900">
            {{ t('matchDetail.statistics.publicTitle') }}
          </h2>

          <p class="mt-1 text-sm text-gray-600">
            {{ t('matchDetail.statistics.publicSubtitle') }}
          </p>

          <div
            v-if="playerStatistics.length === 0"
            class="mt-4 rounded-xl border border-dashed border-gray-300 p-6 text-center text-gray-600"
          >
            {{ t('matchDetail.statistics.publicEmpty') }}
          </div>

          <div v-else class="mt-5 overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200 text-sm">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left font-semibold text-gray-700">
                    {{ t('matchDetail.statistics.player') }}
                  </th>
                  <th class="px-4 py-3 text-left font-semibold text-gray-700">
                    {{ t('matchDetail.statistics.team') }}
                  </th>
                  <th class="px-4 py-3 text-left font-semibold text-gray-700">
                    {{ t('matchDetail.statistics.shirt') }}
                  </th>
                  <th class="px-4 py-3 text-left font-semibold text-gray-700">
                    {{ t('matchDetail.statistics.goals') }}
                  </th>
                  <th class="px-4 py-3 text-left font-semibold text-gray-700">
                    {{ t('matchDetail.statistics.fouls') }}
                  </th>
                  <th class="px-4 py-3 text-left font-semibold text-gray-700">
                    {{ t('matchDetail.statistics.yellow') }}
                  </th>
                  <th class="px-4 py-3 text-left font-semibold text-gray-700">
                    {{ t('matchDetail.statistics.red') }}
                  </th>
                </tr>
              </thead>

              <tbody class="divide-y divide-gray-200 bg-white">
                <tr
                  v-for="entry in playerStatistics"
                  :key="entry.id"
                >
                  <td class="px-4 py-3 font-medium text-gray-900">
                    {{ entry.player_full_name }}
                  </td>

                  <td class="px-4 py-3 text-gray-700">
                    {{ entry.team_name }}
                  </td>

                  <td class="px-4 py-3 text-gray-700">
                    {{ entry.shirt_number ?? '-' }}
                  </td>

                  <td class="px-4 py-3 text-gray-700">
                    {{ entry.goals }}
                  </td>

                  <td class="px-4 py-3 text-gray-700">
                    {{ entry.fouls }}
                  </td>

                  <td class="px-4 py-3 text-gray-700">
                    {{ entry.yellow_cards }}
                  </td>

                  <td class="px-4 py-3 text-gray-700">
                    {{ entry.red_cards }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section
          v-if="isRefereeRole && !canEditMatch"
          class="rounded-2xl bg-white p-6 shadow"
        >
          <h2 class="text-xl font-bold text-gray-900">
            {{ t('matchDetail.refereeAccess.title') }}
          </h2>

          <p class="mt-1 text-sm text-gray-600">
            {{ t('matchDetail.refereeAccess.message') }}
          </p>

          <p class="mt-3 text-sm text-gray-600">
            {{ t('matchDetail.refereeAccess.assignedReferee') }}:
            <span class="font-semibold text-gray-900">
              {{ match.referee_username || t('matchDetail.common.notAssigned') }}
            </span>
          </p>
        </section>
      </template>
    </div>
  </main>
</template>