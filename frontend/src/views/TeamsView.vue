<script setup>
import { computed, onMounted, ref } from 'vue'
import { teamApi } from '@/services/api.js'
import { useAuth } from '@/services/useAuth.js'

const { role, isAuthenticated, loadUser } = useAuth()

const teams = ref([])
const myTeams = ref([])

const loading = ref(false)
const myTeamsLoading = ref(false)

const error = ref('')
const successfulAdd = ref('')

const teamForm = ref({
  team_name: '',
  sport_name: '',
})

function getTeamInitial(team) {
  return team.team_name?.charAt(0)?.toUpperCase() ?? '?'
}

const canManageTeams = computed(() => {
  return isAuthenticated.value && role.value === 'team_manager'
})

async function loadTeams() {
  loading.value = true
  error.value = ''

  try {
    const response = await teamApi.getAll()
    teams.value = response.data
  } catch (err) {
    error.value = 'Could not load teams.'
  } finally {
    loading.value = false
  }
}

async function loadMyTeams() {
  if (!canManageTeams.value) {
    myTeams.value = []
    return
  }

  myTeamsLoading.value = true

  try {
    const response = await teamApi.getMine()
    myTeams.value = response.data
  } catch (err) {
    myTeams.value = []
  } finally {
    myTeamsLoading.value = false
  }
}

async function createTeam() {
  if (!canManageTeams.value) {
    error.value = 'You must be signed in as a team manager to create teams.'
    return
  }

  error.value = ''
  successfulAdd.value = ''

  try {
    await teamApi.create(teamForm.value)

    successfulAdd.value = 'Team added successfully!'

    teamForm.value = {
      team_name: '',
      sport_name: '',
    }

    await loadTeams()
    await loadMyTeams()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Could not add team.'
  }
}

onMounted(async () => {
  await loadUser()
  await loadTeams()
  await loadMyTeams()
})
</script>


<template>
  <main class="min-h-screen bg-gray-50 px-6 py-10">
    <div class="mx-auto max-w-7xl space-y-10">
      <section>
        <h1 class="text-4xl font-bold text-gray-900">
          Teams
        </h1>

        <p class="mt-3 max-w-2xl text-gray-600">
          Browse registered teams, view their details, and manage your own teams.
        </p>
      </section>

      <section
        v-if="canManageTeams"
        class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm"
      >
        <div class="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 class="text-2xl font-bold text-gray-900">
              My Teams
            </h2>

            <p class="mt-1 text-sm text-gray-600">
              Create and edit the teams you organize.
            </p>
          </div>
        </div>

        <div class="mt-8 grid gap-8 lg:grid-cols-[1fr_2fr]">
          <form
            @submit.prevent="createTeam"
            class="rounded-2xl border border-gray-200 bg-gray-50 p-6"
          >
            <h3 class="text-xl font-semibold text-gray-900">
              Create Team
            </h3>

            <label class="mt-5 block">
              <span class="text-sm font-medium text-gray-700">Team name</span>

              <input
                v-model="teamForm.team_name"
                required
                type="text"
                class="mt-1 w-full rounded-xl border border-gray-300 px-4 py-2 outline-none focus:border-green-600"
                placeholder="Hraklara"
              />
            </label>

            <label class="mt-4 block">
              <span class="text-sm font-medium text-gray-700">Sport</span>

              <input
                v-model="teamForm.sport_name"
                required
                type="text"
                class="mt-1 w-full rounded-xl border border-gray-300 px-4 py-2 outline-none focus:border-green-600"
                placeholder="Football"
              />
            </label>

            <button
              type="submit"
              class="mt-6 rounded-xl bg-green-700 px-5 py-2 font-semibold text-white hover:bg-green-800"
            >
              Create Team
            </button>

            <p
              v-if="successfulAdd"
              class="mt-4 rounded-xl bg-green-50 p-3 text-sm text-green-700"
            >
              {{ successfulAdd }}
            </p>

            <p
              v-if="error"
              class="mt-4 rounded-xl bg-red-50 p-3 text-sm text-red-700"
            >
              {{ error }}
            </p>
          </form>

          <div>
            <p
              v-if="myTeamsLoading"
              class="text-gray-600"
            >
              Your teams are loading...
            </p>

            <p
              v-else-if="myTeams.length === 0"
              class="rounded-xl border border-dashed border-gray-300 p-6 text-gray-600"
            >
              You have not created any teams yet.
            </p>

            <div
              v-else
              class="grid gap-4 md:grid-cols-2"
            >
              <article
                v-for="team in myTeams"
                :key="team.id"
                class="rounded-xl border border-gray-200 bg-white p-5"
              >
                <div class="flex items-center gap-4">
  <div class="flex h-14 w-14 shrink-0 items-center justify-center overflow-hidden rounded-xl border border-gray-200 bg-gray-100">
    <img
      v-if="team.logo_url"
      :src="team.logo_url"
      :alt="`${team.team_name} logo`"
      class="h-full w-full object-cover"
    />

    <span
      v-else
      class="text-xl font-bold text-gray-400"
    >
      {{ getTeamInitial(team) }}
    </span>
  </div>

  <div>
    <h3 class="text-lg font-bold text-gray-900">
      {{ team.team_name }}
    </h3>

    <p class="text-sm text-gray-600">
      {{ team.sport_name }}
    </p>
  </div>
</div>

                <p class="mt-3 text-sm text-gray-700">
                  Players:
                  <span class="font-semibold">
                    {{ team.members?.length ?? 0 }}
                  </span>
                </p>

                <div class="mt-5 flex gap-3">
                  <RouterLink
                    :to="{ name: 'team', params: { id: team.id } }"
                    class="rounded-lg border border-gray-300 px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-50"
                  >
                    View
                  </RouterLink>

                  <RouterLink
                    :to="{ name: 'team', params: { id: team.id }, query: { edit: 'true' } }"
                    class="rounded-lg bg-green-700 px-4 py-2 text-sm font-semibold text-white hover:bg-green-800"
                  >
                    Edit
                  </RouterLink>
                </div>
              </article>
            </div>
          </div>
        </div>
      </section>

      <section class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
        <h2 class="text-2xl font-bold text-gray-900">
          Browse All Teams
        </h2>

        <p class="mt-1 text-sm text-gray-600">
          View all teams registered in the platform.
        </p>

        <p
          v-if="loading"
          class="mt-6 text-gray-600"
        >
          Teams are loading...
        </p>

        <p
          v-else-if="teams.length === 0"
          class="mt-6 rounded-xl border border-dashed border-gray-300 p-6 text-gray-600"
        >
          No teams are available.
        </p>

        <div
          v-else
          class="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-3"
        >
          <RouterLink
  v-for="team in teams"
  :key="team.id"
  :to="{ name: 'team', params: { id: team.id } }"
  class="rounded-xl border border-gray-200 p-5 hover:border-green-600 hover:bg-green-50"
>
  <div class="flex items-center gap-4">
    <div class="flex h-14 w-14 shrink-0 items-center justify-center overflow-hidden rounded-xl border border-gray-200 bg-gray-100">
      <img
        v-if="team.logo_url"
        :src="team.logo_url"
        :alt="`${team.team_name} logo`"
        class="h-full w-full object-cover"
      />

      <span
        v-else
        class="text-xl font-bold text-gray-400"
      >
        {{ getTeamInitial(team) }}
      </span>
    </div>

    <div>
      <h3 class="text-lg font-bold text-gray-900">
        {{ team.team_name }}
      </h3>

      <p class="text-sm text-gray-600">
        {{ team.sport_name }}
      </p>
    </div>
  </div>

  <p class="mt-4 text-sm text-gray-700">
    Players:
    <span class="font-semibold">
      {{ team.members?.length ?? 0 }}
    </span>
  </p>
</RouterLink>
        </div>
      </section>
    </div>
  </main>
</template>