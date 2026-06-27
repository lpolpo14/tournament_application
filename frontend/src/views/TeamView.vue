<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { playerApi, teamApi } from '@/services/api.js'

const route = useRoute()

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

const matchesLoading = ref(false)
const matchesError = ref('')
const showPastMatches = ref(false)

const futureMatches = computed(() => {
  return teamMatches.value.future_matches ?? []
})

const pastMatches = computed(() => {
  return teamMatches.value.past_matches ?? []
})

function formatMatchDate(dateValue) {
  if (!dateValue) {
    return 'Not scheduled'
  }

  return new Intl.DateTimeFormat('en-GB', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(dateValue))
}

function getOpponentName(match) {
  if (!team.value) {
    return 'Opponent'
  }

  const currentTeamId = Number(team.value.id)

  if (Number(match.team1) === currentTeamId) {
    return match.team2_name
  }

  return match.team1_name
}

function getScoreText(match) {
  if (match.team1_score === null || match.team2_score === null) {
    return 'Score not submitted'
  }

  return `${match.team1_score} - ${match.team2_score}`
}

function getStadiumText(match) {
  const parts = [match.stadium_name, match.stadium_city].filter(Boolean)

  if (parts.length === 0) {
    return 'No stadium assigned'
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
    matchesError.value = 'Could not load team matches.'
  } finally {
    matchesLoading.value = false
  }
}

const selectedLogo = ref(null)
const logoPreview = ref('')

function handleLogoChange(event) {
  const file = event.target.files[0]

  selectedLogo.value = file ?? null

  if (file) {
    logoPreview.value = URL.createObjectURL(file)
  } else {
    logoPreview.value = ''
  }
}

const playerSearchQuery = ref('')

const deletePlayerError = ref('')
const deletePlayerSuccess = ref('')

async function removePlayerFromTeam(member) {
  deletePlayerError.value = ''
  deletePlayerSuccess.value = ''

  const playerName = member.player?.full_name ?? 'Player'

  try {
    await teamApi.removePlayer(route.params.id, member.id)

    deletePlayerSuccess.value = `${playerName} was removed from the team.`

    await loadTeam()
  } catch (err) {
    deletePlayerError.value = 'Could not remove player from team.'
  }
}

const editForm = ref({
  team_name: '',
  sport_name: '',
})

const shirtNumbers = ref({})

// Temporary ownership placeholder.
// Later this should check if the logged-in user owns this team.
const isOwner = ref(true)

const canEditTeam = computed(() => {
  return isOwner.value
})

const positions = [
  { value: 'UK', label: 'Unknown' },
  { value: 'GK', label: 'Goalkeeper' },
  { value: 'DF', label: 'Defender' },
  { value: 'MF', label: 'Midfielder' },
  { value: 'FR', label: 'Forward' },
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
    const position = String(player.position_display ?? player.position ?? '').toLowerCase()

    return (
      fullName.includes(query) ||
      shirtNumber.includes(query) ||
      position.includes(query)
    )
  })
})

function getPositionLabel(positionValue) {
  const position = positions.find((item) => item.value === positionValue)
  return position ? position.label : positionValue
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
    error.value = 'Could not load team.'
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
    addPlayerError.value = 'Could not load players.'
  } finally {
    playersLoading.value = false
  }
}

function formatApiErrors(errorData) {
  if (!errorData) {
    return 'Something went wrong.'
  }

  if (typeof errorData === 'string') {
    return errorData
  }

  if (Array.isArray(errorData)) {
    return errorData.join(' ')
  }

  if (typeof errorData === 'object') {
    const fieldLabels = {
      team_name: 'Team name',
      sport_name: 'Sport',
      logo_img: 'Team logo',
      non_field_errors: 'Error',
      detail: 'Error',
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

  return 'Something went wrong.'
}

async function updateTeam() {
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
    success.value = 'Team updated successfully.'
    editMode.value = false

    selectedLogo.value = null
    logoPreview.value = ''
  } catch (err) {
    console.log(err.response?.data)

    editError.value = formatApiErrors(err.response?.data)
  }
}

async function addPlayerToTeam(player) {
  addPlayerError.value = ''
  addPlayerSuccess.value = ''

  try {
    await teamApi.addPlayer(route.params.id, {
      player_id: player.id,
      shirt_number: getDefaultShirtNumber(player),
    })

    addPlayerSuccess.value = `${player.name} ${player.surname} was added to the team.`

    await loadTeam()
  } catch (err) {
    if (err.response?.data?.non_field_errors) {
      addPlayerError.value = err.response.data.non_field_errors[0]
    } else if (err.response?.data?.shirt_number) {
      addPlayerError.value = err.response.data.shirt_number[0]
    } else if (err.response?.data?.player_id) {
      addPlayerError.value = err.response.data.player_id[0]
    } else {
      addPlayerError.value = 'Could not add player to team.'
    }
  }
}

onMounted(async () => {
  await loadTeam()
  await loadAvailablePlayers()
  await loadTeamMatches()
})
</script>

<template>
  <main class="min-h-screen bg-gray-50 px-6 py-10">
    <div class="mx-auto max-w-6xl">
      <p
        v-if="loading"
        class="text-gray-600"
      >
        Team is loading...
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
      :alt="`${team.team_name} logo`"
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
              @click="editMode = true"
              class="rounded-xl bg-green-700 px-5 py-2 font-semibold text-white hover:bg-green-800"
            >
              Edit Team
            </button>
          </div>
        </div>

        <section
          v-if="canEditTeam && editMode"
          class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm"
        >
          <h2 class="text-2xl font-bold text-gray-900">
            Edit Team
          </h2>

          <form
            @submit.prevent="updateTeam"
            class="mt-6 space-y-4"
          >
            <label class="block">
              <span class="text-sm font-medium text-gray-700">Team name</span>

              <input
                v-model="editForm.team_name"
                required
                type="text"
                class="mt-1 w-full rounded-xl border border-gray-300 px-4 py-2 outline-none focus:border-green-600"
              />
            </label>

            <label class="block">
              <span class="text-sm font-medium text-gray-700">Sport</span>

              <input
                v-model="editForm.sport_name"
                required
                type="text"
                class="mt-1 w-full rounded-xl border border-gray-300 px-4 py-2 outline-none focus:border-green-600"
              />
            </label>

            <label class="block">
  <span class="text-sm font-medium text-gray-700">Team logo</span>

  <input
    type="file"
    accept="image/png,image/jpeg,image/jpg,image/webp"
    @change="handleLogoChange"
    class="mt-1 w-full rounded-xl border border-gray-300 px-4 py-2 text-sm text-gray-700 outline-none focus:border-green-600"
  />
</label>

<div
  v-if="logoPreview || team.logo_url"
  class="mt-4 flex items-center gap-4"
>
  <img
    :src="logoPreview || team.logo_url"
    alt="Team logo preview"
    class="h-20 w-20 rounded-xl border border-gray-200 object-cover"
  />

  <p class="text-sm text-gray-600">
    Logo preview
  </p>
</div>

            <div class="flex gap-3">
              <button
                type="submit"
                class="rounded-xl bg-green-700 px-5 py-2 font-semibold text-white hover:bg-green-800"
              >
                Save Changes
              </button>

              <button
                type="button"
                @click="editMode = false"
                class="rounded-xl border border-gray-300 px-5 py-2 font-semibold text-gray-700 hover:bg-gray-50"
              >
                Cancel
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
  <!-- Future matches -->
  <section class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
    <h2 class="text-2xl font-bold text-gray-900">
      Upcoming Matches
    </h2>

    <p class="mt-1 text-sm text-gray-600">
      The next scheduled matches for this team.
    </p>

    <p
      v-if="matchesLoading"
      class="mt-6 text-gray-600"
    >
      Loading matches...
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
      No upcoming matches found.
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
              vs {{ getOpponentName(match) }}
            </p>

            <p class="mt-1 text-sm text-gray-600">
              Tournament: {{ match.tournament_name }}
            </p>

            <p class="mt-1 text-sm text-gray-600">
              {{ formatMatchDate(match.scheduled_date) }}
            </p>

            <p class="mt-1 text-sm text-gray-600">
              {{ getStadiumText(match) }}
            </p>
          </div>

          <span class="rounded-full bg-green-50 px-3 py-1 text-sm font-semibold text-green-700">
            {{ match.match_status }}
          </span>
        </div>

        <RouterLink
          :to="`/tournament/${match.tournament}`"
          class="mt-4 inline-block text-sm font-semibold text-green-700 hover:text-green-800"
        >
          View tournament
        </RouterLink>
      </article>
    </div>
  </section>

  <!-- Past matches -->
  <section class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">
          Past Matches
        </h2>

        <p class="mt-1 text-sm text-gray-600">
          Completed or already-played matches for this team.
        </p>
      </div>

      <button
        @click="showPastMatches = !showPastMatches"
        class="rounded-xl border border-gray-300 px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-50"
      >
        {{ showPastMatches ? 'Hide Past Matches' : `View Past Matches (${pastMatches.length})` }}
      </button>
    </div>

    <p
      v-if="matchesLoading"
      class="mt-6 text-gray-600"
    >
      Loading matches...
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
      No past matches found.
    </p>

    <div
      v-else-if="showPastMatches"
      class="mt-6 overflow-hidden rounded-xl border border-gray-200"
    >
      <table class="w-full text-left text-sm">
        <thead class="bg-gray-50 text-gray-700">
          <tr>
            <th class="px-4 py-3">Match</th>
            <th class="px-4 py-3">Tournament</th>
            <th class="px-4 py-3">Date</th>
            <th class="px-4 py-3">Score</th>
            <th class="px-4 py-3">Status</th>
          </tr>
        </thead>

        <tbody class="divide-y divide-gray-200">
          <tr
            v-for="match in pastMatches"
            :key="match.id"
            class="hover:bg-gray-50"
          >
            <td class="px-4 py-3 font-medium text-gray-900">
              {{ match.team1_name }} vs {{ match.team2_name }}
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
              {{ match.match_status }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <p
      v-else
      class="mt-6 rounded-xl border border-dashed border-gray-300 p-6 text-gray-600"
    >
      Click “View Past Matches” to show this team’s match history.
    </p>
  </section>
</section>
        <section class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 class="text-2xl font-bold text-gray-900">
            Team Players
          </h2>

          <p class="mt-1 text-sm text-gray-600">
            Players currently registered in this team.
          </p>

          <p
            v-if="!team.members || team.members.length === 0"
            class="mt-6 rounded-xl border border-dashed border-gray-300 p-6 text-gray-600"
          >
            No players have been added to this team yet.
          </p>

          <div
            v-else
            class="mt-6 overflow-hidden rounded-xl border border-gray-200"
          >
            <table class="w-full text-left text-sm">
              <thead class="bg-gray-50 text-gray-700">
                <tr>
                     <th class="px-4 py-3">Team #</th>
                       <th class="px-4 py-3">Name</th>
                    <th class="px-4 py-3">Main #</th>
                     <th class="px-4 py-3">Position</th>
                      <th v-if="canEditTeam" class="px-4 py-3">Action</th>
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
    {{ member.player.full_name }}
  </td>

  <td class="px-4 py-3 text-gray-700">
    #{{ member.player.main_shirt_number }}
  </td>

  <td class="px-4 py-3 text-gray-700">
    {{ member.player.position_display ?? getPositionLabel(member.player.position) }}
  </td>

  <td
    v-if="canEditTeam"
    class="px-4 py-3"
  >
    <button
      @click="removePlayerFromTeam(member)"
      class="rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700"
    >
      Delete
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

        <!-- Add player to team -->
        <section
          v-if="canEditTeam"
          class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm"
        >
          <div class="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div>
              <h2 class="text-2xl font-bold text-gray-900">
                Add Player to Team
              </h2>

              <p class="mt-1 text-sm text-gray-600">
                Search existing players and add them to this team.
              </p>
            </div>

            <label class="w-full md:max-w-sm">
              <span class="text-sm font-medium text-gray-700">
                Search players
              </span>

              <input
                v-model="playerSearchQuery"
                type="search"
                class="mt-1 w-full rounded-xl border border-gray-300 px-4 py-2 outline-none focus:border-green-600"
                placeholder="Search by name, number, or position"
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
            Loading players...
          </p>

          <p
            v-else-if="availablePlayers.length === 0"
            class="mt-6 rounded-xl border border-dashed border-gray-300 p-6 text-gray-600"
          >
            No players are available.
          </p>

          <p
            v-else-if="filteredPlayers.length === 0"
            class="mt-6 rounded-xl border border-dashed border-gray-300 p-6 text-gray-600"
          >
            No players match your search.
          </p>

          <div
            v-else
            class="mt-6 overflow-x-auto rounded-xl border border-gray-200"
          >
            <table class="w-full text-left text-sm">
              <thead class="bg-gray-50 text-gray-700">
                <tr>
                  <th class="px-4 py-3">Name</th>
                  <th class="px-4 py-3">Main #</th>
                  <th class="px-4 py-3">Team #</th>
                  <th class="px-4 py-3">Position</th>
                  <th class="px-4 py-3">Created</th>
                  <th class="px-4 py-3">Action</th>
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
                    {{ player.position_display ?? getPositionLabel(player.position) }}
                  </td>

                  <td class="px-4 py-3 text-gray-700">
                    {{ new Date(player.created_at).toLocaleDateString() }}
                  </td>

                  <td class="px-4 py-3">
                    <button
                      v-if="!isPlayerAlreadyInTeam(player.id)"
                      @click="addPlayerToTeam(player)"
                      class="rounded-lg bg-green-700 px-4 py-2 text-sm font-semibold text-white hover:bg-green-800"
                    >
                      Add
                    </button>

                    <span
                      v-else
                      class="rounded-lg bg-gray-100 px-4 py-2 text-sm font-semibold text-gray-500"
                    >
                      Added
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