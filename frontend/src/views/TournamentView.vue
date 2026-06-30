<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'
import instance_api, { teamApi, userApi } from '@/services/api.js'
import { useAuth } from '@/services/useAuth.js'
import StandingsTable from '@/components/helpers/StandingsTable.vue'

const route = useRoute()
const { t, locale } = useI18n()

const tournamentId = route.params.id
const { user, role, isAuthenticated, isLoaded, loadUser } = useAuth()

const tournament = ref(null)
const matches = ref([])
const standings = ref([])
const teams = ref([])
const registrations = ref([])
const selectedTeamId = ref('')
const referees = ref([])
const stadiums = ref([])

const loading = ref(false)
const error = ref('')
const success = ref('')

const generateMatchesOnCommence = ref(true)

const manualMatchForm = ref({
  team1: '',
  team2: '',
  stadium: '',
  referee: '',
  scheduled_date: '',
})

const isSportsAdmin = computed(() => {
  return isAuthenticated.value && role.value === 'sports_admin'
})

const isTeamManager = computed(() => {
  return isAuthenticated.value && role.value === 'team_manager'
})

const isReferee = computed(() => {
  return isAuthenticated.value && role.value === 'referee'
})

const canManageTournament = computed(() => {
  return isSportsAdmin.value
})

const canRequestRegistration = computed(() => {
  return (
    isTeamManager.value &&
    tournament.value?.status === 'Scheduled'
  )
})

const canViewRegistrationRequests = computed(() => {
  return isSportsAdmin.value
})

const canCreateMatches = computed(() => {
  return (
    isSportsAdmin.value &&
    tournament.value?.status !== 'Completed' &&
    tournament.value?.status !== 'Cancelled'
  )
})

const canCancelTournament = computed(() => {
  return (
    canManageTournament.value &&
    tournament.value &&
    tournament.value.status !== 'Completed' &&
    tournament.value.status !== 'Cancelled'
  )
})

const canCompleteTournament = computed(() => {
  return (
    canManageTournament.value &&
    tournament.value?.status === 'Ongoing' &&
    matches.value.length > 0 &&
    matches.value.every((match) => {
      return (
        match.match_status === 'Completed' ||
        match.match_status === 'Cancelled'
      )
    }) &&
    matches.value.some((match) => match.match_status === 'Completed')
  )
})

const canMarkTournamentOngoing = computed(() => {
  return (
    canManageTournament.value &&
    tournament.value?.status === 'Cancelled'
  )
})

function clearMessages() {
  error.value = ''
  success.value = ''
}

function extractError(err) {
  if (err.response?.data) {
    return JSON.stringify(err.response.data, null, 2)
  }

  return err.message || t('tournamentDetail.errors.generic')
}

function normalizeList(data) {
  return Array.isArray(data) ? data : data.results || []
}

function formatDate(value) {
  if (!value) {
    return t('tournamentDetail.common.notSet')
  }

  const browserLocale = locale.value === 'el' ? 'el-GR' : 'en-US'

  return new Date(value).toLocaleDateString(browserLocale)
}

function formatDateTime(value) {
  if (!value) {
    return t('tournamentDetail.common.notSet')
  }

  const browserLocale = locale.value === 'el' ? 'el-GR' : 'en-US'

  return new Date(value).toLocaleString(browserLocale)
}

function toApiDateTime(datetimeLocalValue) {
  if (!datetimeLocalValue) {
    return null
  }

  return new Date(datetimeLocalValue).toISOString()
}

function teamLabel(match, side) {
  if (side === 'team1') {
    return match.team1_name || t('tournamentDetail.participatingTeams.teamFallback', { id: match.team1 })
  }

  return match.team2_name || t('tournamentDetail.participatingTeams.teamFallback', { id: match.team2 })
}

function stadiumLabel(match) {
  if (match.stadium_name && match.stadium_city) {
    return `${match.stadium_name} - ${match.stadium_city}`
  }

  if (match.stadium_name) {
    return match.stadium_name
  }

  return t('tournamentDetail.matches.noStadiumAssigned')
}

function canSubmitThisMatch(match) {
  return (
    isReferee.value &&
    user.value?.id &&
    Number(match.referee) === Number(user.value.id)
  )
}

function translatedStatus(status) {
  const statusMap = {
    Scheduled: 'tournamentDetail.status.scheduled',
    Ongoing: 'tournamentDetail.status.ongoing',
    Completed: 'tournamentDetail.status.completed',
    Cancelled: 'tournamentDetail.status.cancelled',
    Pending: 'tournamentDetail.status.pending',
    Accepted: 'tournamentDetail.status.accepted',
    Rejected: 'tournamentDetail.status.rejected',
  }

  return statusMap[status] ? t(statusMap[status]) : status
}

async function fetchTournament() {
  const response = await instance_api.get(`/tournaments/${tournamentId}/`)
  tournament.value = response.data
}

async function fetchMatches() {
  const response = await instance_api.get('/matches/', {
    params: {
      tournament: tournamentId,
    },
  })

  matches.value = normalizeList(response.data)
}

async function fetchStandings() {
  const response = await instance_api.get(`/tournaments/${tournamentId}/standings/`)
  standings.value = normalizeList(response.data)
}

async function fetchMyTeams() {
  const response = await teamApi.getMine()
  teams.value = normalizeList(response.data)
}

async function fetchRegistrations() {
  const response = await instance_api.get(`/tournaments/${tournamentId}/registrations/`)
  registrations.value = normalizeList(response.data)
}

async function fetchReferees() {
  const response = await userApi.getReferees()
  referees.value = normalizeList(response.data)
}

async function fetchStadiums() {
  const response = await instance_api.get('/stadiums/')
  stadiums.value = normalizeList(response.data)
}

async function requestRegistration() {
  if (!canRequestRegistration.value) {
    error.value = t('tournamentDetail.errors.registrationForbidden')
    return
  }

  loading.value = true
  clearMessages()

  try {
    await instance_api.post(`/tournaments/${tournamentId}/request-registration/`, {
      team_id: selectedTeamId.value,
    })

    success.value = t('tournamentDetail.success.registrationRequested')
    selectedTeamId.value = ''
  } catch (err) {
    error.value = extractError(err)
  } finally {
    loading.value = false
  }
}

async function acceptRegistration(registration) {
  if (!canManageTournament.value) {
    error.value = t('tournamentDetail.errors.acceptForbidden')
    return
  }

  loading.value = true
  clearMessages()

  try {
    await instance_api.post(`/tournament-registrations/${registration.id}/accept/`)

    success.value = t('tournamentDetail.success.registrationAccepted')

    await Promise.all([
      fetchTournament(),
      fetchRegistrations(),
      fetchStandings(),
    ])
  } catch (err) {
    error.value = extractError(err)
  } finally {
    loading.value = false
  }
}

async function rejectRegistration(registration) {
  if (!canManageTournament.value) {
    error.value = t('tournamentDetail.errors.rejectForbidden')
    return
  }

  loading.value = true
  clearMessages()

  try {
    await instance_api.post(`/tournament-registrations/${registration.id}/reject/`)

    success.value = t('tournamentDetail.success.registrationRejected')

    await fetchRegistrations()
  } catch (err) {
    error.value = extractError(err)
  } finally {
    loading.value = false
  }
}

async function commenceTournament() {
  if (!canManageTournament.value) {
    error.value = t('tournamentDetail.errors.commenceForbidden')
    return
  }

  loading.value = true
  clearMessages()

  try {
    const response = await instance_api.post(`/tournaments/${tournamentId}/commence/`, {
      generate_matches: generateMatchesOnCommence.value,
    })

    success.value = generateMatchesOnCommence.value
      ? t('tournamentDetail.success.commencedGenerated', {
          count: response.data.generated_matches,
        })
      : t('tournamentDetail.success.commencedManual')

    await Promise.all([
      fetchTournament(),
      fetchMatches(),
      fetchStandings(),
    ])
  } catch (err) {
    error.value = extractError(err)
  } finally {
    loading.value = false
  }
}

async function generateMatches() {
  if (!canManageTournament.value) {
    error.value = t('tournamentDetail.errors.generateForbidden')
    return
  }

  loading.value = true
  clearMessages()

  try {
    const response = await instance_api.post(`/tournaments/${tournamentId}/generate-matches/`)

    success.value = t('tournamentDetail.success.generatedMatches', {
      count: response.data.generated_matches,
    })

    await fetchMatches()
  } catch (err) {
    error.value = extractError(err)
  } finally {
    loading.value = false
  }
}

async function createManualMatch() {
  if (!canCreateMatches.value) {
    error.value = t('tournamentDetail.errors.createMatchForbidden')
    return
  }

  if (manualMatchForm.value.team1 === manualMatchForm.value.team2) {
    error.value = t('tournamentDetail.errors.teamCannotPlayItself')
    return
  }

  loading.value = true
  clearMessages()

  try {
    await instance_api.post('/matches/', {
      tournament: tournamentId,
      team1: manualMatchForm.value.team1,
      team2: manualMatchForm.value.team2,
      stadium: manualMatchForm.value.stadium,
      referee: manualMatchForm.value.referee,
      scheduled_date: toApiDateTime(manualMatchForm.value.scheduled_date),
    })

    success.value = t('tournamentDetail.success.matchCreated')

    manualMatchForm.value = {
      team1: '',
      team2: '',
      stadium: '',
      referee: '',
      scheduled_date: '',
    }

    await fetchMatches()
  } catch (err) {
    error.value = extractError(err)
  } finally {
    loading.value = false
  }
}

async function completeTournament() {
  if (!canCompleteTournament.value) {
    error.value = t('tournamentDetail.errors.completeRequiresAll')
    return
  }

  loading.value = true
  clearMessages()

  try {
    const response = await instance_api.post(`/tournaments/${tournamentId}/complete/`)

    tournament.value = response.data
    success.value = t('tournamentDetail.success.completed')
  } catch (err) {
    error.value = extractError(err)
  } finally {
    loading.value = false
  }
}

async function cancelTournament() {
  if (!canCancelTournament.value) {
    error.value = t('tournamentDetail.errors.cannotCancel')
    return
  }

  const confirmed = window.confirm(
    t('tournamentDetail.confirm.cancelTournament')
  )

  if (!confirmed) {
    return
  }

  loading.value = true
  clearMessages()

  try {
    const response = await instance_api.post(`/tournaments/${tournamentId}/cancel/`)

    tournament.value = response.data
    success.value = t('tournamentDetail.success.cancelled')
  } catch (err) {
    error.value = extractError(err)
  } finally {
    loading.value = false
  }
}

async function markTournamentOngoing() {
  if (!canMarkTournamentOngoing.value) {
    error.value = t('tournamentDetail.errors.onlyCancelledCanBeOngoing')
    return
  }

  loading.value = true
  clearMessages()

  try {
    const response = await instance_api.post(`/tournaments/${tournamentId}/mark-ongoing/`)

    tournament.value = response.data
    success.value = t('tournamentDetail.success.ongoing')
  } catch (err) {
    error.value = extractError(err)
  } finally {
    loading.value = false
  }
}

async function loadPage() {
  loading.value = true
  clearMessages()

  try {
    if (!isLoaded.value) {
      await loadUser()
    }

    await Promise.all([
      fetchTournament(),
      fetchMatches(),
      fetchStandings(),
    ])

    if (isTeamManager.value) {
      await fetchMyTeams()
    }

    if (isSportsAdmin.value) {
      await Promise.all([
        fetchRegistrations(),
        fetchStadiums(),
        fetchReferees(),
      ])
    }
  } catch (err) {
    error.value = extractError(err)
  } finally {
    loading.value = false
  }
}

onMounted(loadPage)
</script>

<template>
  <main class="min-h-screen bg-gray-100 p-6">
    <div class="mx-auto max-w-7xl space-y-6">
      <header class="rounded-2xl bg-white p-6 shadow">
        <RouterLink
          :to="{ name: 'tournaments' }"
          class="text-sm font-semibold text-blue-700 hover:text-blue-900"
        >
          {{ t('tournamentDetail.back') }}
        </RouterLink>

        <div
          v-if="tournament"
          class="mt-4 flex flex-col gap-4 md:flex-row md:items-start md:justify-between"
        >
          <div>
            <h1 class="text-3xl font-bold text-gray-900">
              {{ tournament.name }}
            </h1>

            <p class="mt-2 text-gray-600">
              {{ t('tournamentDetail.header.subtitle', {
                sport: tournament.sport,
                location: tournament.location,
              }) }}
            </p>
          </div>

          <span class="w-fit rounded-full bg-blue-100 px-4 py-2 text-sm font-semibold text-blue-800">
            {{ translatedStatus(tournament.status) }}
          </span>
        </div>

        <div v-else class="mt-4">
          <h1 class="text-3xl font-bold text-gray-900">
            {{ t('tournamentDetail.fallbackTitle') }}
          </h1>
        </div>
      </header>

      <section v-if="error" class="rounded-lg bg-red-100 p-4">
        <h2 class="font-semibold text-red-900">
          {{ t('tournamentDetail.errorTitle') }}
        </h2>

        <pre class="mt-2 whitespace-pre-wrap text-sm text-red-800">{{ error }}</pre>
      </section>

      <section v-if="success" class="rounded-lg bg-green-100 p-4 text-green-800">
        {{ success }}
      </section>

      <section v-if="loading" class="rounded-2xl bg-white p-6 shadow">
        <p class="text-gray-600">
          {{ t('tournamentDetail.loadingData') }}
        </p>
      </section>

      <template v-if="!loading && tournament">
        <section class="grid gap-4 md:grid-cols-4">
          <article class="rounded-2xl bg-white p-5 shadow">
            <p class="text-sm font-semibold text-gray-500">
              {{ t('tournamentDetail.summary.sport') }}
            </p>

            <p class="mt-1 text-lg font-bold text-gray-900">
              {{ tournament.sport }}
            </p>
          </article>

          <article class="rounded-2xl bg-white p-5 shadow">
            <p class="text-sm font-semibold text-gray-500">
              {{ t('tournamentDetail.summary.location') }}
            </p>

            <p class="mt-1 text-lg font-bold text-gray-900">
              {{ tournament.location }}
            </p>
          </article>

          <article class="rounded-2xl bg-white p-5 shadow">
            <p class="text-sm font-semibold text-gray-500">
              {{ t('tournamentDetail.summary.startDate') }}
            </p>

            <p class="mt-1 text-lg font-bold text-gray-900">
              {{ formatDate(tournament.start_date) }}
            </p>
          </article>

          <article class="rounded-2xl bg-white p-5 shadow">
            <p class="text-sm font-semibold text-gray-500">
              {{ t('tournamentDetail.summary.endDate') }}
            </p>

            <p class="mt-1 text-lg font-bold text-gray-900">
              {{ formatDate(tournament.end_date) }}
            </p>
          </article>
        </section>

        <section
          v-if="tournament.status === 'Scheduled' && isTeamManager"
          class="rounded-2xl bg-white p-6 shadow"
        >
          <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 class="text-xl font-bold text-gray-900">
                {{ t('tournamentDetail.registration.title') }}
              </h2>

              <p class="mt-1 text-sm text-gray-600">
                {{ t('tournamentDetail.registration.subtitle') }}
              </p>
            </div>
          </div>

          <form
            class="mt-4 grid gap-3 md:grid-cols-3"
            @submit.prevent="requestRegistration"
          >
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700">
                {{ t('tournamentDetail.registration.selectTeam') }}
              </label>

              <select
                v-model="selectedTeamId"
                class="mt-1 w-full rounded-lg border border-gray-300 p-3 focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
                required
              >
                <option value="" disabled>
                  {{ t('tournamentDetail.registration.chooseTeam') }}
                </option>

                <option
                  v-for="team in teams"
                  :key="team.id"
                  :value="team.id"
                >
                  {{ team.team_name }}
                </option>
              </select>
            </div>

            <div class="flex items-end">
              <button
                type="submit"
                class="w-full rounded-lg bg-green-600 px-4 py-3 font-semibold text-white hover:bg-green-700 disabled:opacity-50"
                :disabled="loading"
              >
                {{ t('tournamentDetail.registration.requestButton') }}
              </button>
            </div>
          </form>
        </section>

        <section
          v-if="canViewRegistrationRequests"
          class="rounded-2xl bg-white p-6 shadow"
        >
          <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 class="text-xl font-bold text-gray-900">
                {{ t('tournamentDetail.requests.title') }}
              </h2>

              <p class="mt-1 text-sm text-gray-600">
                {{ t('tournamentDetail.requests.subtitle') }}
              </p>
            </div>

            <button
              class="rounded-lg bg-gray-900 px-4 py-2 text-sm font-semibold text-white hover:bg-black disabled:opacity-50"
              :disabled="loading"
              @click="fetchRegistrations"
            >
              {{ t('tournamentDetail.requests.refresh') }}
            </button>
          </div>

          <div
            v-if="registrations.length === 0"
            class="mt-4 rounded-xl border border-dashed border-gray-300 p-6 text-center text-gray-600"
          >
            {{ t('tournamentDetail.requests.empty') }}
          </div>

          <div v-else class="mt-4 overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200 text-sm">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left font-semibold text-gray-700">
                    {{ t('tournamentDetail.requests.team') }}
                  </th>
                  <th class="px-4 py-3 text-left font-semibold text-gray-700">
                    {{ t('tournamentDetail.requests.status') }}
                  </th>
                  <th class="px-4 py-3 text-left font-semibold text-gray-700">
                    {{ t('tournamentDetail.requests.requestedAt') }}
                  </th>
                  <th class="px-4 py-3 text-right font-semibold text-gray-700">
                    {{ t('tournamentDetail.requests.actions') }}
                  </th>
                </tr>
              </thead>

              <tbody class="divide-y divide-gray-200 bg-white">
                <tr
                  v-for="registration in registrations"
                  :key="registration.id"
                >
                  <td class="px-4 py-3 font-medium text-gray-900">
                    {{ registration.team_name }}
                  </td>

                  <td class="px-4 py-3">
                    {{ translatedStatus(registration.status) }}
                  </td>

                  <td class="px-4 py-3 text-gray-600">
                    {{ formatDateTime(registration.requested_at) }}
                  </td>

                  <td class="px-4 py-3 text-right">
                    <div
                      v-if="registration.status === 'Pending'"
                      class="flex justify-end gap-2"
                    >
                      <button
                        class="rounded-lg bg-green-600 px-3 py-2 text-xs font-semibold text-white hover:bg-green-700 disabled:opacity-50"
                        :disabled="loading"
                        @click="acceptRegistration(registration)"
                      >
                        {{ t('tournamentDetail.requests.accept') }}
                      </button>

                      <button
                        class="rounded-lg bg-red-600 px-3 py-2 text-xs font-semibold text-white hover:bg-red-700 disabled:opacity-50"
                        :disabled="loading"
                        @click="rejectRegistration(registration)"
                      >
                        {{ t('tournamentDetail.requests.reject') }}
                      </button>
                    </div>

                    <span v-else class="text-gray-500">
                      {{ t('tournamentDetail.requests.decided') }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section class="rounded-2xl bg-white p-6 shadow">
          <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 class="text-xl font-bold text-gray-900">
                {{ t('tournamentDetail.participatingTeams.title') }}
              </h2>

              <p class="mt-1 text-sm text-gray-600">
                {{ t('tournamentDetail.participatingTeams.subtitle') }}
              </p>
            </div>

            <button
              class="rounded-lg bg-gray-900 px-4 py-2 text-sm font-semibold text-white hover:bg-black disabled:opacity-50"
              :disabled="loading"
              @click="loadPage"
            >
              {{ t('tournamentDetail.participatingTeams.refresh') }}
            </button>
          </div>

          <div
            v-if="!tournament.teams || tournament.teams.length === 0"
            class="mt-4 rounded-xl border border-dashed border-gray-300 p-6 text-center text-gray-600"
          >
            {{ t('tournamentDetail.participatingTeams.empty') }}
          </div>

          <div v-else class="mt-4 flex flex-wrap gap-2">
            <span
              v-for="team in tournament.teams"
              :key="typeof team === 'object' ? team.id : team"
              class="rounded-full bg-green-100 px-4 py-2 text-sm font-semibold text-green-800"
            >
              <template v-if="typeof team === 'object'">
                {{ team.team_name }}
              </template>

              <template v-else>
                {{ t('tournamentDetail.participatingTeams.teamFallback', { id: team }) }}
              </template>
            </span>
          </div>
        </section>

        <section class="rounded-2xl bg-white p-6 shadow">
          <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 class="text-xl font-bold text-gray-900">
                {{ t('tournamentDetail.standings.title') }}
              </h2>

              <p class="mt-1 text-sm text-gray-600">
                {{ t('tournamentDetail.standings.subtitle') }}
              </p>
            </div>

            <button
              class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
              :disabled="loading"
              @click="fetchStandings"
            >
              {{ t('tournamentDetail.standings.refresh') }}
            </button>
          </div>

          <div
            v-if="standings.length === 0"
            class="mt-4 rounded-xl border border-dashed border-gray-300 p-6 text-center text-gray-600"
          >
            {{ t('tournamentDetail.standings.empty') }}
          </div>

          <StandingsTable
            v-else
            class="mt-4"
            :standings="standings"
          />
        </section>

        <section
          v-if="canManageTournament"
          class="rounded-2xl bg-white p-6 shadow"
        >
          <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 class="text-xl font-bold text-gray-900">
                {{ t('tournamentDetail.admin.title') }}
              </h2>

              <p class="mt-1 text-sm text-gray-600">
                {{ t('tournamentDetail.admin.subtitle') }}
              </p>
            </div>

            <label class="flex items-center gap-2 text-sm text-gray-700">
              <input
                v-model="generateMatchesOnCommence"
                type="checkbox"
                class="rounded border-gray-300"
              />

              {{ t('tournamentDetail.admin.autoGenerateMatches') }}
            </label>

            <div class="flex flex-col gap-2 sm:flex-row">
              <button
                v-if="tournament.status === 'Scheduled'"
                class="rounded-lg bg-purple-600 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-700 disabled:opacity-50"
                :disabled="loading || !tournament.teams || tournament.teams.length < 2"
                @click="commenceTournament"
              >
                {{ t('tournamentDetail.admin.commenceAndGenerate') }}
              </button>

              <button
                v-if="tournament.status === 'Ongoing'"
                class="rounded-lg bg-gray-900 px-4 py-2 text-sm font-semibold text-white hover:bg-black disabled:opacity-50"
                :disabled="loading"
                @click="generateMatches"
              >
                {{ t('tournamentDetail.admin.generateMissing') }}
              </button>
            </div>
          </div>

          <p
            v-if="!tournament.teams || tournament.teams.length < 2"
            class="mt-3 text-sm text-red-700"
          >
            {{ t('tournamentDetail.admin.minTeamsRequired') }}
          </p>
        </section>

        <section
          v-if="canCreateMatches"
          class="rounded-2xl bg-white p-6 shadow"
        >
          <div>
            <h2 class="text-xl font-bold text-gray-900">
              {{ t('tournamentDetail.manualMatch.title') }}
            </h2>

            <p class="mt-1 text-sm text-gray-600">
              {{ t('tournamentDetail.manualMatch.subtitle') }}
            </p>
          </div>

          <form
            class="mt-4 grid gap-4 md:grid-cols-2 lg:grid-cols-3"
            @submit.prevent="createManualMatch"
          >
            <div>
              <label class="block text-sm font-medium text-gray-700">
                {{ t('tournamentDetail.manualMatch.team1') }}
              </label>

              <select
                v-model="manualMatchForm.team1"
                class="mt-1 w-full rounded-lg border border-gray-300 p-3"
                required
              >
                <option value="" disabled>
                  {{ t('tournamentDetail.manualMatch.selectFirstTeam') }}
                </option>

                <option
                  v-for="team in tournament.teams"
                  :key="team.id"
                  :value="team.id"
                >
                  {{ team.team_name }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">
                {{ t('tournamentDetail.manualMatch.team2') }}
              </label>

              <select
                v-model="manualMatchForm.team2"
                class="mt-1 w-full rounded-lg border border-gray-300 p-3"
                required
              >
                <option value="" disabled>
                  {{ t('tournamentDetail.manualMatch.selectSecondTeam') }}
                </option>

                <option
                  v-for="team in tournament.teams"
                  :key="team.id"
                  :value="team.id"
                >
                  {{ team.team_name }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">
                {{ t('tournamentDetail.manualMatch.stadium') }}
              </label>

              <select
                v-model="manualMatchForm.stadium"
                class="mt-1 w-full rounded-lg border border-gray-300 p-3"
                required
              >
                <option value="" disabled>
                  {{ t('tournamentDetail.manualMatch.selectStadium') }}
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
                {{ t('tournamentDetail.manualMatch.referee') }}
              </label>

              <select
                v-model="manualMatchForm.referee"
                class="mt-1 w-full rounded-lg border border-gray-300 p-3"
                required
              >
                <option value="" disabled>
                  {{ t('tournamentDetail.manualMatch.selectReferee') }}
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
                {{ t('tournamentDetail.manualMatch.dateTime') }}
              </label>

              <input
                v-model="manualMatchForm.scheduled_date"
                type="datetime-local"
                class="mt-1 w-full rounded-lg border border-gray-300 p-3"
                required
              />
            </div>

            <div class="md:col-span-2">
              <button
                type="submit"
                class="rounded-lg bg-purple-600 px-5 py-3 font-semibold text-white hover:bg-purple-700 disabled:opacity-50"
                :disabled="loading"
              >
                {{ t('tournamentDetail.manualMatch.createButton') }}
              </button>
            </div>
          </form>
        </section>

        <section class="rounded-2xl bg-white p-6 shadow">
          <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 class="text-xl font-bold text-gray-900">
                {{ t('tournamentDetail.matches.title') }}
              </h2>

              <p class="mt-1 text-sm text-gray-600">
                {{ t('tournamentDetail.matches.subtitle') }}
              </p>
            </div>

            <button
              class="rounded-lg bg-gray-900 px-4 py-2 text-sm font-semibold text-white hover:bg-black disabled:opacity-50"
              :disabled="loading"
              @click="fetchMatches"
            >
              {{ t('tournamentDetail.matches.refresh') }}
            </button>
          </div>

          <div
            v-if="matches.length === 0"
            class="mt-4 rounded-xl border border-dashed border-gray-300 p-6 text-center text-gray-600"
          >
            {{ t('tournamentDetail.matches.empty') }}
          </div>

          <div v-else class="mt-4 space-y-4">
            <article
              v-for="match in matches"
              :key="match.id"
              class="rounded-xl border border-gray-200 p-4"
            >
              <div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                <div>
                  <h3 class="text-lg font-bold text-gray-900">
                    {{ teamLabel(match, 'team1') }}
                    {{ t('tournamentDetail.matches.versus') }}
                    {{ teamLabel(match, 'team2') }}
                  </h3>

                  <p class="mt-1 text-sm text-gray-600">
                    {{ t('tournamentDetail.matches.matchNumber', { id: match.id }) }}
                  </p>

                  <p class="mt-1 text-sm text-gray-600">
                    {{ t('tournamentDetail.matches.date') }}:
                    {{ formatDateTime(match.scheduled_date) }}
                  </p>

                  <p class="mt-1 text-sm text-gray-600">
                    {{ t('tournamentDetail.matches.stadium') }}:
                    <span class="font-semibold text-gray-800">
                      {{ stadiumLabel(match) }}
                    </span>
                  </p>

                  <p class="mt-1 text-sm">
                    {{ t('tournamentDetail.matches.status') }}:
                    <span
                      class="font-semibold"
                      :class="{
                        'text-green-700': match.match_status === 'Completed',
                        'text-blue-700': match.match_status === 'Scheduled',
                        'text-red-700': match.match_status === 'Cancelled'
                      }"
                    >
                      {{ translatedStatus(match.match_status) }}
                    </span>
                  </p>

                  <p class="mt-1 text-sm text-gray-600">
                    {{ t('tournamentDetail.matches.referee') }}:
                    <span class="font-semibold text-gray-800">
                      {{ match.referee_username || t('tournamentDetail.matches.notAssigned') }}
                    </span>
                  </p>
                </div>

                <div class="rounded-xl bg-gray-100 px-6 py-4 text-center">
                  <p class="text-sm font-semibold text-gray-500">
                    {{ t('tournamentDetail.matches.score') }}
                  </p>

                  <p class="mt-1 text-3xl font-bold text-gray-900">
                    {{ match.team1_score ?? '-' }}
                    :
                    {{ match.team2_score ?? '-' }}
                  </p>
                </div>
              </div>

              <div class="mt-4 flex justify-end">
                <RouterLink
                  :to="{ name: 'match', params: { id: match.id } }"
                  class="rounded-lg px-4 py-2 text-sm font-semibold text-white"
                  :class="canSubmitThisMatch(match) ? 'bg-purple-600 hover:bg-purple-700' : 'bg-gray-900 hover:bg-black'"
                >
                  {{ canSubmitThisMatch(match)
                    ? t('tournamentDetail.matches.openMatchSheet')
                    : t('tournamentDetail.matches.viewMatchDetails')
                  }}
                </RouterLink>
              </div>
            </article>
          </div>
        </section>

        <section
          v-if="canManageTournament"
          class="rounded-2xl bg-white p-6 shadow"
        >
          <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 class="text-xl font-bold text-gray-900">
                {{ t('tournamentDetail.statusControls.title') }}
              </h2>

              <p class="mt-1 text-sm text-gray-600">
                {{ t('tournamentDetail.statusControls.subtitle') }}
              </p>
            </div>

            <span class="w-fit rounded-full bg-blue-100 px-3 py-1 text-sm font-semibold text-blue-800">
              {{ translatedStatus(tournament.status) }}
            </span>
          </div>

          <div class="mt-5 flex flex-col gap-3 sm:flex-row">
            <button
              v-if="canCompleteTournament"
              class="rounded-lg bg-green-600 px-4 py-2 text-sm font-semibold text-white hover:bg-green-700 disabled:opacity-50"
              :disabled="loading"
              @click="completeTournament"
            >
              {{ t('tournamentDetail.statusControls.markCompleted') }}
            </button>

            <button
              v-if="canCancelTournament"
              class="rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700 disabled:opacity-50"
              :disabled="loading"
              @click="cancelTournament"
            >
              {{ t('tournamentDetail.statusControls.cancelTournament') }}
            </button>

            <button
              v-if="canMarkTournamentOngoing"
              class="rounded-lg bg-purple-600 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-700 disabled:opacity-50"
              :disabled="loading"
              @click="markTournamentOngoing"
            >
              {{ t('tournamentDetail.statusControls.markOngoing') }}
            </button>
          </div>

          <p
            v-if="tournament.status === 'Ongoing' && !canCompleteTournament"
            class="mt-4 text-sm text-gray-600"
          >
            {{ t('tournamentDetail.statusControls.finishRequirement') }}
          </p>
        </section>
      </template>
    </div>
  </main>
</template>