<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { teamApi } from '@/services/api.js'

const route = useRoute()

const team = ref(null)
const loading = ref(false)
const error = ref('')
const success = ref('')

const editMode = ref(route.query.edit === 'true')

const editForm = ref({
  team_name: '',
  sport_name: '',
})


const isOwner = ref(true)

const canEditTeam = computed(() => {
  return isOwner.value
})

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

async function updateTeam() {
  error.value = ''
  success.value = ''

  try {
    const response = await teamApi.update(route.params.id, editForm.value)

    team.value = response.data
    success.value = 'Team updated successfully.'
    editMode.value = false
  } catch (err) {
    error.value = 'Could not update team.'
  }
}

onMounted(loadTeam)
</script>

<template>
  <main class="min-h-screen bg-gray-50 px-6 py-10">
    <div class="mx-auto max-w-5xl">
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
            <div>
              <h1 class="text-4xl font-bold text-gray-900">
                {{ team.team_name }}
              </h1>

              <p class="mt-2 text-lg text-gray-600">
                {{ team.sport_name }}
              </p>
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

          <p class="mt-1 text-sm text-gray-600">
            Later this section can also include the team logo and player management.
          </p>

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
              v-if="success"
              class="rounded-xl bg-green-50 p-3 text-sm text-green-700"
            >
              {{ success }}
            </p>
          </form>
        </section>

        <section class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <div class="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 class="text-2xl font-bold text-gray-900">
                Players
              </h2>

              <p class="mt-1 text-sm text-gray-600">
                Players registered in this team.
              </p>
            </div>

            <button
              v-if="canEditTeam"
              class="rounded-xl border border-gray-300 px-5 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-50"
            >
              Add Player
            </button>
          </div>

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
                  <th class="px-4 py-3">#</th>
                  <th class="px-4 py-3">Name</th>
                  <th class="px-4 py-3">Position</th>
                </tr>
              </thead>

              <tbody class="divide-y divide-gray-200">
                <tr
                  v-for="member in team.members"
                  :key="member.id"
                >
                  <td class="px-4 py-3 font-semibold">
                    {{ member.shirt_number }}
                  </td>

                  <td class="px-4 py-3">
                    {{ member.player?.name }} {{ member.player?.surname }}
                  </td>

                  <td class="px-4 py-3">
                    {{ member.player?.position }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section
          v-if="canEditTeam"
          class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm"
        >
          <h2 class="text-2xl font-bold text-gray-900">
            Team Logo
          </h2>

          <p class="mt-1 text-sm text-gray-600">
            Logo upload can be added after enabling an ImageField in the backend.
          </p>

          <button
            class="mt-5 rounded-xl border border-gray-300 px-5 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-50"
          >
            Upload Logo
          </button>
        </section>
      </section>
    </div>
  </main>
</template>