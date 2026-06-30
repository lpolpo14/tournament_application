<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { playerApi, teamApi } from '@/services/api.js'
import StandingsTeamTable from '@/components/helpers/StandingsTeamTable.vue'
import { useAuth } from '@/services/useAuth.js'

const route = useRoute()
const { t, locale } = useI18n()
const { user, role, isAuthenticated, loadUser } = useAuth()

const team = ref(null)
const availablePlayers = ref([])

const loading = ref(false)
const playersLoading = ref(false)

const error = ref('')
const success = ref('')
const editError = ref('')

const addPlayerError = ref('')
const addPlayerSuccess = ref('')

const editMode = ref(route.query.edit === 'true')

const teamMatches = ref({
  future_matches: [],
  past_matches: [],
})

const tournamentStandings = ref([])
const tournamentStandingsLoading = ref(false)
const tournamentStandingsError = ref('')

const matchesLoading = ref(false)
const matchesError = ref('')
const showPastMatches = ref(false)

const selectedLogo = ref(null)
const logoPreview = ref('')

const playerSearchQuery = ref('')

const deletePlayerError = ref('')
const deletePlayerSuccess = ref('')

const editForm = ref({
  team_name: '',
  sport_name: '',
})

const shirtNumbers = ref({})

const futureMatches = computed(() => {
  return teamMatches.value.future_matches ?? []
})

const pastMatches = computed(() => {
  return teamMatches.value.past_matches ?? []
})

const canEditTeam = computed(() => {
  if (!isAuthenticated.value) {
    return false
  }

  if (role.value !== 'team_manager') {
    return false
  }

  if (!team.value?.manager_id || !user.value?.id) {
    return false
  }

  return Number(team.value.manager_id) === Number(user.value.id)
})

const positions = [
  { value: 'UK', labelKey: 'teamDetail.positions.unknown' },
  { value: 'GK', labelKey: 'teamDetail.positions.goalkeeper' },
  { value: 'DF', labelKey: 'teamDetail.positions.defender' },
  { value: 'MF', labelKey: 'teamDetail.positions.midfielder' },
  { value: 'FR', labelKey: 'teamDetail.positions.forward' },
]

const teamPlayerIds = computed(() => {
  if (!team.value?.members) {
    return []
  }

  return team.value.members.map((member) => member.player.id)
})

const filteredPlayers = computed(() => {
  const query = playerSearchQuery.value.trim().toLowerCase()

  let players = [...availablePlayers.value]

  players.sort((a, b) => {
    return new Date(b.created_at) - new Date(a.created_at)
  })

  if (!query) {
    return players
  }

  return players.filter((player) => {
    const fullName = `${player.name ?? ''} ${player.surname ?? ''}`.toLowerCase()
    const shirtNumber = String(player.main_shirt_number ?? '')
    const position = getPositionLabel(player.position).toLowerCase()

    return (
      fullName.includes(query) ||
      shirtNumber.includes(query) ||
      position.includes(query)
    )
  })
})

function browserLocale() {
  return locale.value === 'el' ? 'el-GR' : 'en-GB'
}

function translatedStatus(status) {
  const statusMap = {
    Scheduled: 'teamDetail.status.scheduled',
    Ongoing: 'teamDetail.status.ongoing',
    Completed: 'teamDetail.status.completed',
    Cancelled: 'teamDetail.status.cancelled',
  }

  return statusMap[status] ? t(statusMap[status]) : status
}

function formatMatchDate(dateValue) {
  if (!dateValue) {
    return t('teamDetail.matches.notScheduled')
  }

  return new Intl.DateTimeFormat(browserLocale(), {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(dateValue))
}

function formatSimpleDate(value) {
  if (!value) {
    return t('teamDetail.standings.notSet')
  }

  return new Date(value).toLocaleDateString(browserLocale())
}

function getOpponentName(match) {
  if (!team.value) {
    return t('teamDetail.matches.opponent')
  }

  const currentTeamId = Number(team.value.id)

  if (Number(match.team1) === currentTeamId) {
    return match.team2_name
  }

  return match.team1_name
}

async function loadTournamentStandings() {
  tournamentStandingsLoading.value = true
  tournamentStandingsError.value = ''

  try {
    const response = await teamApi.getTournamentStandings(route.params.id)
    tournamentStandings.value = response.data
  } catch (err) {
    tournamentStandingsError.value = t('teamDetail.errors.loadStandings')
  } finally {
    tournamentStandingsLoading.value = false
  }
}

function formatTournamentDate(value) {
  return formatSimpleDate(value)
}

function getGoalDifference(standing) {
  return standing.goals_scored - standing.goals_conceded
}

function getGoalDifferenceLabel(standing) {
  const goalDifference = getGoalDifference(standing)

  if (goalDifference > 0) {
    return `+${goalDifference}`
  }

  return String(goalDifference)
}

function getScoreText(match) {
  if (match.team1_score === null || match.team2_score === null) {
    return t('teamDetail.matches.scoreNotSubmitted')
  }

  return `${match.team1_score} - ${match.team2_score}`
}

function getStadiumText(match) {
  const parts = [match.stadium_name, match.stadium_city].filter(Boolean)

  if (parts.length === 0) {
    return t('teamDetail.matches.noStadiumAssigned')
  }

  return parts.join(', ')
}

async function loadTeamMatches() {
  matchesLoading.value = true
  matchesError.value = ''

  try {
    const response = await teamApi.getMatches(route.params.id, {
      future_limit: 3,
    })

    teamMatches.value = response.data
  } catch (err) {
    matchesError.value = t('teamDetail.errors.loadMatches')
  } finally {
    matchesLoading.value = false
  }
}

function handleLogoChange(event) {
  const file = event.target.files[0]

  selectedLogo.value = file ?? null

  if (file) {
    logoPreview.value = URL.createObjectURL(file)
  } else {
    logoPreview.value = ''
  }
}

async function removePlayerFromTeam(member) {
  if (!canEditTeam.value) {
    deletePlayerError.value = t('teamDetail.errors.removeForbidden')
    return
  }

  deletePlayerError.value = ''
  deletePlayerSuccess.value = ''

  const playerName = member.player?.full_name ?? t('teamDetail.players.name')

  try {
    await teamApi.removePlayer(route.params.id, member.id)

    deletePlayerSuccess.value = t('teamDetail.success.playerRemoved', {
      name: playerName,
    })

    await loadTeam()
  } catch (err) {
    deletePlayerError.value = t('teamDetail.errors.removeFailed')
  }
}

function getPositionLabel(positionValue) {
  const position = positions.find((item) => item.value === positionValue)
  return position ? t(position.labelKey) : positionValue
}

function isPlayerAlreadyInTeam(playerId) {
  return teamPlayerIds.value.includes(playerId)
}

function getDefaultShirtNumber(player) {
  return shirtNumbers.value[player.id] ?? player.main_shirt_number ?? 1
}

async function loadTeam() {
  loading.value = true
  error.value = ''

  try {
    const response = await teamApi.getOne(route.params.id)

    team.value = response.data

    editForm.value = {
      team_name: response.data.team_name,
      sport_name: response.data.sport_name,
    }
  } catch (err) {
    error.value = t('teamDetail.errors.loadTeam')
  } finally {
    loading.value = false
  }
}

async function loadAvailablePlayers() {
  playersLoading.value = true
  addPlayerError.value = ''

  try {
    const response = await playerApi.getAll()

    availablePlayers.value = response.data

    for (const player of response.data) {
      shirtNumbers.value[player.id] = player.main_shirt_number ?? 1
    }
  } catch (err) {
    addPlayerError.value = t('teamDetail.errors.loadPlayers')
  } finally {
    playersLoading.value = false
  }
}

function formatApiErrors(errorData) {
  if (!errorData) {
    return t('teamDetail.errors.generic')
  }

  if (typeof errorData === 'string') {
    return errorData
  }

  if (Array.isArray(errorData)) {
    return errorData.join(' ')
  }

  if (typeof errorData === 'object') {
    const fieldLabels = {
      team_name: t('teamDetail.fields.teamName'),
      sport_name: t('teamDetail.fields.sport'),
      logo_img: t('teamDetail.fields.teamLogo'),
      non_field_errors: t('teamDetail.fields.error'),
      detail: t('teamDetail.fields.error'),
    }

    return Object.entries(errorData)
      .map(([field, messages]) => {
        const label = fieldLabels[field] ?? field

        if (Array.isArray(messages)) {
          return `${label}: ${messages.join(' ')}`
        }

        if (typeof messages === 'object') {
          return `${label}: ${formatApiErrors(messages)}`
        }

        return `${label}: ${messages}`
      })
      .join(' ')
  }

  return t('teamDetail.errors.generic')
}

async function updateTeam() {
  if (!canEditTeam.value) {
    editError.value = t('teamDetail.errors.editForbidden')
    return
  }

  error.value = ''
  editError.value = ''
  success.value = ''

  const formData = new FormData()

  formData.append('team_name', editForm.value.team_name)
  formData.append('sport_name', editForm.value.sport_name)

  if (selectedLogo.value instanceof File) {
    formData.append('logo_img', selectedLogo.value)
  }

  try {
    const response = await teamApi.update(route.params.id, formData)

    team.value = response.data
    success.value = t('teamDetail.success.updated')
    editMode.value = false

    selectedLogo.value = null
    logoPreview.value = ''
  } catch (err) {
    editError.value = formatApiErrors(err.response?.data)
  }
}

async function addPlayerToTeam(player) {
  if (!canEditTeam.value) {
    addPlayerError.value = t('teamDetail.errors.addForbidden')
    return
  }

  addPlayerError.value = ''
  addPlayerSuccess.value = ''

  try {
    await teamApi.addPlayer(route.params.id, {
      player_id: player.id,
      shirt_number: getDefaultShirtNumber(player),
    })

    addPlayerSuccess.value = t('teamDetail.success.playerAdded', {
      name: `${player.name} ${player.surname}`,
    })

    await loadTeam()
  } catch (err) {
    if (err.response?.data?.non_field_errors) {
      addPlayerError.value = err.response.data.non_field_errors[0]
    } else if (err.response?.data?.shirt_number) {
      addPlayerError.value = err.response.data.shirt_number[0]
    } else if (err.response?.data?.player_id) {
      addPlayerError.value = err.response.data.player_id[0]
    } else {
      addPlayerError.value = t('teamDetail.errors.addFailed')
    }
  }
}

onMounted(async () => {
  await loadUser()
  await loadTeam()

  if (!canEditTeam.value) {
    editMode.value = false
  }

  await loadTeamMatches()
  await loadTournamentStandings()

  if (canEditTeam.value) {
    await loadAvailablePlayers()
  }
})
</script>

<template>
  <main class="min-h-screen bg-gray-50 px-6 py-10">
    <div class="mx-auto max-w-6xl">
      <p
        v-if="loading"
        class="text-gray-600"
      >
        {{ t('teamDetail.loading') }}
      </p>

      <p
        v-else-if="error"
        class="rounded-xl bg-red-50 p-4 text-sm text-red-700"
      >
        {{ error }}
      </p>

      <section
        v-else-if="team"
        class="space-y-8"
      >
        <div class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <div class="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
            <div class="flex items-center gap-5">
              <div class="flex h-24 w-24 items-center justify-center overflow-hidden rounded-2xl border border-gray-200 bg-gray-100">
                <img
                  v-if="team.logo_url"
                  :src="team.logo_url"
                  :alt="t('teamDetail.logoAlt', { name: team.team_name })"
                  class="h-full w-full object-cover"
                />

                <span
                  v-else
                  class="text-3xl font-bold text-gray-400"
                >
                  {{ team.team_name?.charAt(0) }}
                </span>
              </div>

              <div>
                <h1 class="text-4xl font-bold text-gray-900">
                  {{ team.team_name }}
                </h1>

                <p class="mt-2 text-lg text-gray-600">
                  {{ team.sport_name }}
                </p>
              </div>
            </div>

            <button
              v-if="canEditTeam && !editMode"
              class="rounded-xl bg-green-700 px-5 py-2 font-semibold text-white hover:bg-green-800"
              @click="editMode = true"
            >
              {{ t('teamDetail.editTeam') }}
            </button>
          </div>
        </div>

        <section
          v-if="canEditTeam && editMode"
          class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm"
        >
          <h2 class="text-2xl font-bold text-gray-900">
            {{ t('teamDetail.editTeam') }}
          </h2>

          <form
            class="mt-6 space-y-4"
            @submit.prevent="updateTeam"
          >
            <label class="block">
              <span class="text-sm font-medium text-gray-700">
                {{ t('teamDetail.teamName') }}
              </span>

              <input
                v-model="editForm.team_name"
                required
                type="text"
                class="mt-1 w-full rounded-xl border border-gray-300 px-4 py-2 outline-none focus:border-green-600"
              />
            </label>

            <label class="block">
              <span class="text-sm font-medium text-gray-700">
                {{ t('teamDetail.sport') }}
              </span>

              <input
                v-model="editForm.sport_name"
                required
                type="text"
                class="mt-1 w-full rounded-xl border border-gray-300 px-4 py-2 outline-none focus:border-green-600"
              />
            </label>

            <label class="block">
              <span class="text-sm font-medium text-gray-700">
                {{ t('teamDetail.teamLogo') }}
              </span>

              <input
                type="file"
                accept="image/png,image/jpeg,image/jpg,image/webp"
                class="mt-1 w-full rounded-xl border border-gray-300 px-4 py-2 text-sm text-gray-700 outline-none focus:border-green-600"
                @change="handleLogoChange"
              />
            </label>

            <div
              v-if="logoPreview || team.logo_url"
              class="mt-4 flex items-center gap-4"
            >
              <img
                :src="logoPreview || team.logo_url"
                :alt="t('teamDetail.logoPreviewAlt')"
                class="h-20 w-20 rounded-xl border border-gray-200 object-cover"
              />

              <p class="text-sm text-gray-600">
                {{ t('teamDetail.logoPreview') }}
              </p>
            </div>

            <div class="flex gap-3">
              <button
                type="submit"
                class="rounded-xl bg-green-700 px-5 py-2 font-semibold text-white hover:bg-green-800"
              >
                {{ t('teamDetail.saveChanges') }}
              </button>

              <button
                type="button"
                class="rounded-xl border border-gray-300 px-5 py-2 font-semibold text-gray-700 hover:bg-gray-50"
                @click="editMode = false"
              >
                {{ t('teamDetail.cancel') }}
              </button>
            </div>

            <p
              v-if="editError"
              class="rounded-xl bg-red-50 p-3 text-sm text-red-700"
            >
              {{ editError }}
            </p>
          </form>
        </section>

        <p
          v-if="success"
          class="rounded-xl bg-green-50 p-3 text-sm text-green-700"
        >
          {{ success }}
        </p>

        <section class="grid gap-6 lg:grid-cols-2">
          <section class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
            <h2 class="text-2xl font-bold text-gray-900">
              {{ t('teamDetail.matches.upcomingTitle') }}
            </h2>

            <p class="mt-1 text-sm text-gray-600">
              {{ t('teamDetail.matches.upcomingSubtitle') }}
            </p>

            <p
              v-if="matchesLoading"
              class="mt-6 text-gray-600"
            >
              {{ t('teamDetail.matches.loading') }}
            </p>

            <p
              v-else-if="matchesError"
              class="mt-6 rounded-xl bg-red-50 p-3 text-sm text-red-700"
            >
              {{ matchesError }}
            </p>

            <p
              v-else-if="futureMatches.length === 0"
              class="mt-6 rounded-xl border border-dashed border-gray-300 p-6 text-gray-600"
            >
              {{ t('teamDetail.matches.noUpcoming') }}
            </p>

            <div
              v-else
              class="mt-6 space-y-4"
            >
              <article
                v-for="match in futureMatches"
                :key="match.id"
                class="rounded-xl border border-gray-200 p-4"
              >
                <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <p class="font-semibold text-gray-900">
                      {{ t('teamDetail.matches.versus') }}
                      {{ getOpponentName(match) }}
                    </p>

                    <p class="mt-1 text-sm text-gray-600">
                      {{ t('teamDetail.matches.tournament') }}:
                      {{ match.tournament_name }}
                    </p>

                    <p class="mt-1 text-sm text-gray-600">
                      {{ formatMatchDate(match.scheduled_date) }}
                    </p>

                    <p class="mt-1 text-sm text-gray-600">
                      {{ getStadiumText(match) }}
                    </p>
                  </div>

                  <span class="rounded-full bg-green-50 px-3 py-1 text-sm font-semibold text-green-700">
                    {{ translatedStatus(match.match_status) }}
                  </span>
                </div>

                <RouterLink
                  :to="`/tournament/${match.tournament}`"
                  class="mt-4 inline-block text-sm font-semibold text-green-700 hover:text-green-800"
                >
                  {{ t('teamDetail.matches.viewTournament') }}
                </RouterLink>
              </article>
            </div>
          </section>

          <section class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
            <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 class="text-2xl font-bold text-gray-900">
                  {{ t('teamDetail.matches.pastTitle') }}
                </h2>

                <p class="mt-1 text-sm text-gray-600">
                  {{ t('teamDetail.matches.pastSubtitle') }}
                </p>
              </div>

              <button
                class="rounded-xl border border-gray-300 px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-50"
                @click="showPastMatches = !showPastMatches"
              >
                {{ showPastMatches
                  ? t('teamDetail.matches.hidePast')
                  : t('teamDetail.matches.viewPast', { count: pastMatches.length })
                }}
              </button>
            </div>

            <p
              v-if="matchesLoading"
              class="mt-6 text-gray-600"
            >
              {{ t('teamDetail.matches.loading') }}
            </p>

            <p
              v-else-if="matchesError"
              class="mt-6 rounded-xl bg-red-50 p-3 text-sm text-red-700"
            >
              {{ matchesError }}
            </p>

            <p
              v-else-if="pastMatches.length === 0"
              class="mt-6 rounded-xl border border-dashed border-gray-300 p-6 text-gray-600"
            >
              {{ t('teamDetail.matches.noPast') }}
            </p>

            <div
              v-else-if="showPastMatches"
              class="mt-6 overflow-hidden rounded-xl border border-gray-200"
            >
              <table class="w-full text-left text-sm">
                <thead class="bg-gray-50 text-gray-700">
                  <tr>
                    <th class="px-4 py-3">
                      {{ t('teamDetail.matches.table.match') }}
                    </th>
                    <th class="px-4 py-3">
                      {{ t('teamDetail.matches.table.tournament') }}
                    </th>
                    <th class="px-4 py-3">
                      {{ t('teamDetail.matches.table.date') }}
                    </th>
                    <th class="px-4 py-3">
                      {{ t('teamDetail.matches.table.score') }}
                    </th>
                    <th class="px-4 py-3">
                      {{ t('teamDetail.matches.table.status') }}
                    </th>
                  </tr>
                </thead>

                <tbody class="divide-y divide-gray-200">
                  <tr
                    v-for="match in pastMatches"
                    :key="match.id"
                    class="hover:bg-gray-50"
                  >
                    <td class="px-4 py-3 font-medium text-gray-900">
                      {{ match.team1_name }}
                      {{ t('teamDetail.matches.versus') }}
                      {{ match.team2_name }}
                    </td>

                    <td class="px-4 py-3 text-gray-700">
                      <RouterLink
                        :to="`/tournament/${match.tournament}`"
                        class="font-semibold text-green-700 hover:text-green-800"
                      >
                        {{ match.tournament_name }}
                      </RouterLink>
                    </td>

                    <td class="px-4 py-3 text-gray-700">
                      {{ formatMatchDate(match.scheduled_date) }}
                    </td>

                    <td class="px-4 py-3 font-semibold text-gray-900">
                      {{ getScoreText(match) }}
                    </td>

                    <td class="px-4 py-3 text-gray-700">
                      {{ translatedStatus(match.match_status) }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <p
              v-else
              class="mt-6 rounded-xl border border-dashed border-gray-300 p-6 text-gray-600"
            >
              {{ t('teamDetail.matches.clickToShow') }}
            </p>
          </section>
        </section>

        <section class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 class="text-2xl font-bold text-gray-900">
                {{ t('teamDetail.standings.title') }}
              </h2>

              <p class="mt-1 text-sm text-gray-600">
                {{ t('teamDetail.standings.subtitle') }}
              </p>
            </div>

            <button
              class="rounded-xl border border-gray-300 px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-50"
              @click="loadTournamentStandings"
            >
              {{ t('teamDetail.standings.refresh') }}
            </button>
          </div>

          <p
            v-if="tournamentStandingsLoading"
            class="mt-6 text-gray-600"
          >
            {{ t('teamDetail.standings.loading') }}
          </p>

          <p
            v-else-if="tournamentStandingsError"
            class="mt-6 rounded-xl bg-red-50 p-3 text-sm text-red-700"
          >
            {{ tournamentStandingsError }}
          </p>

          <p
            v-else-if="tournamentStandings.length === 0"
            class="mt-6 rounded-xl border border-dashed border-gray-300 p-6 text-gray-600"
          >
            {{ t('teamDetail.standings.empty') }}
          </p>

          <div
            v-else
            class="mt-6 space-y-6"
          >
            <article
              v-for="item in tournamentStandings"
              :key="item.tournament_id"
              class="rounded-2xl border border-gray-200 p-5"
            >
              <div class="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                <div>
                  <h3 class="text-xl font-bold text-gray-900">
                    {{ item.tournament_name }}
                  </h3>

                  <p class="mt-1 text-sm text-gray-600">
                    {{ item.sport }} · {{ item.location }}
                  </p>

                  <p class="mt-1 text-sm text-gray-600">
                    {{ formatTournamentDate(item.start_date) }}
                    -
                    {{ formatTournamentDate(item.end_date) }}
                  </p>
                </div>

                <span class="w-fit rounded-full bg-blue-50 px-3 py-1 text-sm font-semibold text-blue-700">
                  {{ translatedStatus(item.status) }}
                </span>
              </div>

              <div class="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
                <div class="rounded-xl bg-gray-50 p-4 text-center">
                  <p class="text-xs font-semibold uppercase text-gray-500">
                    {{ t('teamDetail.standings.position') }}
                  </p>

                  <p class="mt-1 text-2xl font-bold text-gray-900">
                    #{{ item.team_standing.position }}
                  </p>
                </div>

                <div class="rounded-xl bg-gray-50 p-4 text-center">
                  <p class="text-xs font-semibold uppercase text-gray-500">
                    {{ t('teamDetail.standings.points') }}
                  </p>

                  <p class="mt-1 text-2xl font-bold text-gray-900">
                    {{ item.team_standing.points }}
                  </p>
                </div>

                <div class="rounded-xl bg-gray-50 p-4 text-center">
                  <p class="text-xs font-semibold uppercase text-gray-500">
                    {{ t('teamDetail.standings.played') }}
                  </p>

                  <p class="mt-1 text-2xl font-bold text-gray-900">
                    {{ item.team_standing.played_games }}
                  </p>
                </div>

                <div class="rounded-xl bg-gray-50 p-4 text-center">
                  <p class="text-xs font-semibold uppercase text-gray-500">
                    {{ t('teamDetail.standings.record') }}
                  </p>

                  <p class="mt-1 text-lg font-bold text-gray-900">
                    {{ item.team_standing.wins }}{{ t('teamDetail.standings.winsShort') }}
                    {{ item.team_standing.draws }}{{ t('teamDetail.standings.drawsShort') }}
                    {{ item.team_standing.losses }}{{ t('teamDetail.standings.lossesShort') }}
                  </p>
                </div>

                <div class="rounded-xl bg-gray-50 p-4 text-center">
                  <p class="text-xs font-semibold uppercase text-gray-500">
                    {{ t('teamDetail.standings.goalDifference') }}
                  </p>

                  <p class="mt-1 text-2xl font-bold text-gray-900">
                    {{ getGoalDifferenceLabel(item.team_standing) }}
                  </p>
                </div>
              </div>

              <details class="mt-5">
                <summary class="cursor-pointer text-sm font-semibold text-green-700 hover:text-green-800">
                  {{ t('teamDetail.standings.viewFull') }}
                </summary>

                <StandingsTeamTable
                  class="mt-4"
                  :standings="item.standings"
                  :highlight-team-id="team.id"
                />
              </details>

              <RouterLink
                :to="`/tournament/${item.tournament_id}`"
                class="mt-4 inline-block text-sm font-semibold text-green-700 hover:text-green-800"
              >
                {{ t('teamDetail.standings.openTournament') }}
              </RouterLink>
            </article>
          </div>
        </section>

        <section class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 class="text-2xl font-bold text-gray-900">
            {{ t('teamDetail.players.title') }}
          </h2>

          <p class="mt-1 text-sm text-gray-600">
            {{ t('teamDetail.players.subtitle') }}
          </p>

          <p
            v-if="!team.members || team.members.length === 0"
            class="mt-6 rounded-xl border border-dashed border-gray-300 p-6 text-gray-600"
          >
            {{ t('teamDetail.players.empty') }}
          </p>

          <div
            v-else
            class="mt-6 overflow-hidden rounded-xl border border-gray-200"
          >
            <table class="w-full text-left text-sm">
              <thead class="bg-gray-50 text-gray-700">
                <tr>
                  <th class="px-4 py-3">
                    {{ t('teamDetail.players.teamNumber') }}
                  </th>
                  <th class="px-4 py-3">
                    {{ t('teamDetail.players.name') }}
                  </th>
                  <th class="px-4 py-3">
                    {{ t('teamDetail.players.mainNumber') }}
                  </th>
                  <th class="px-4 py-3">
                    {{ t('teamDetail.players.position') }}
                  </th>
                  <th v-if="canEditTeam" class="px-4 py-3">
                    {{ t('teamDetail.players.action') }}
                  </th>
                </tr>
              </thead>

              <tbody class="divide-y divide-gray-200">
                <tr
                  v-for="member in team.members"
                  :key="member.id"
                  class="hover:bg-gray-50"
                >
                  <td class="px-4 py-3 font-semibold">
                    #{{ member.shirt_number }}
                  </td>

                  <td class="px-4 py-3 font-medium text-gray-900">
                    <RouterLink
                      :to="{ name: 'player', params: { id: member.player.id } }"
                      class="font-semibold text-green-700 hover:text-green-800"
                    >
                      {{ member.player.full_name }}
                    </RouterLink>
                  </td>

                  <td class="px-4 py-3 text-gray-700">
                    #{{ member.player.main_shirt_number }}
                  </td>

                  <td class="px-4 py-3 text-gray-700">
                    {{ getPositionLabel(member.player.position) }}
                  </td>

                  <td
                    v-if="canEditTeam"
                    class="px-4 py-3"
                  >
                    <button
                      class="rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700"
                      @click="removePlayerFromTeam(member)"
                    >
                      {{ t('teamDetail.players.delete') }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <p
          v-if="deletePlayerSuccess"
          class="mt-6 rounded-xl bg-green-50 p-3 text-sm text-green-700"
        >
          {{ deletePlayerSuccess }}
        </p>

        <p
          v-if="deletePlayerError"
          class="mt-6 rounded-xl bg-red-50 p-3 text-sm text-red-700"
        >
          {{ deletePlayerError }}
        </p>

        <section
          v-if="canEditTeam"
          class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm"
        >
          <div class="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div>
              <h2 class="text-2xl font-bold text-gray-900">
                {{ t('teamDetail.players.addTitle') }}
              </h2>

              <p class="mt-1 text-sm text-gray-600">
                {{ t('teamDetail.players.addSubtitle') }}
              </p>
            </div>

            <label class="w-full md:max-w-sm">
              <span class="text-sm font-medium text-gray-700">
                {{ t('teamDetail.players.searchPlayers') }}
              </span>

              <input
                v-model="playerSearchQuery"
                type="search"
                class="mt-1 w-full rounded-xl border border-gray-300 px-4 py-2 outline-none focus:border-green-600"
                :placeholder="t('teamDetail.players.searchPlaceholder')"
              />
            </label>
          </div>

          <p
            v-if="addPlayerSuccess"
            class="mt-6 rounded-xl bg-green-50 p-3 text-sm text-green-700"
          >
            {{ addPlayerSuccess }}
          </p>

          <p
            v-if="addPlayerError"
            class="mt-6 rounded-xl bg-red-50 p-3 text-sm text-red-700"
          >
            {{ addPlayerError }}
          </p>

          <p
            v-if="playersLoading"
            class="mt-6 text-gray-600"
          >
            {{ t('teamDetail.players.loading') }}
          </p>

          <p
            v-else-if="availablePlayers.length === 0"
            class="mt-6 rounded-xl border border-dashed border-gray-300 p-6 text-gray-600"
          >
            {{ t('teamDetail.players.emptyAvailable') }}
          </p>

          <p
            v-else-if="filteredPlayers.length === 0"
            class="mt-6 rounded-xl border border-dashed border-gray-300 p-6 text-gray-600"
          >
            {{ t('teamDetail.players.noSearchResults') }}
          </p>

          <div
            v-else
            class="mt-6 overflow-x-auto rounded-xl border border-gray-200"
          >
            <table class="w-full text-left text-sm">
              <thead class="bg-gray-50 text-gray-700">
                <tr>
                  <th class="px-4 py-3">
                    {{ t('teamDetail.players.name') }}
                  </th>
                  <th class="px-4 py-3">
                    {{ t('teamDetail.players.mainNumber') }}
                  </th>
                  <th class="px-4 py-3">
                    {{ t('teamDetail.players.teamNumber') }}
                  </th>
                  <th class="px-4 py-3">
                    {{ t('teamDetail.players.position') }}
                  </th>
                  <th class="px-4 py-3">
                    {{ t('teamDetail.players.created') }}
                  </th>
                  <th class="px-4 py-3">
                    {{ t('teamDetail.players.action') }}
                  </th>
                </tr>
              </thead>

              <tbody class="divide-y divide-gray-200">
                <tr
                  v-for="player in filteredPlayers"
                  :key="player.id"
                  class="hover:bg-gray-50"
                >
                  <td class="px-4 py-3 font-medium text-gray-900">
                    {{ player.full_name }}
                  </td>

                  <td class="px-4 py-3 text-gray-700">
                    #{{ player.main_shirt_number }}
                  </td>

                  <td class="px-4 py-3 text-gray-700">
                    <input
                      v-model.number="shirtNumbers[player.id]"
                      type="number"
                      min="1"
                      max="99"
                      :disabled="isPlayerAlreadyInTeam(player.id)"
                      class="w-20 rounded-lg border border-gray-300 px-3 py-1 outline-none focus:border-green-600 disabled:bg-gray-100"
                    />
                  </td>

                  <td class="px-4 py-3 text-gray-700">
                    {{ getPositionLabel(player.position) }}
                  </td>

                  <td class="px-4 py-3 text-gray-700">
                    {{ formatSimpleDate(player.created_at) }}
                  </td>

                  <td class="px-4 py-3">
                    <button
                      v-if="!isPlayerAlreadyInTeam(player.id)"
                      class="rounded-lg bg-green-700 px-4 py-2 text-sm font-semibold text-white hover:bg-green-800"
                      @click="addPlayerToTeam(player)"
                    >
                      {{ t('teamDetail.players.add') }}
                    </button>

                    <span
                      v-else
                      class="rounded-lg bg-gray-100 px-4 py-2 text-sm font-semibold text-gray-500"
                    >
                      {{ t('teamDetail.players.added') }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </section>
    </div>
  </main>
</template>