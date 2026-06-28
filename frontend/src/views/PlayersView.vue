<script setup>
import { computed, onMounted, ref } from 'vue'
import { playerApi } from '@/services/api.js'
import { useAuth } from '@/services/useAuth.js'

const { role, isAuthenticated, loadUser } = useAuth()

const players = ref([])
const loading = ref(false)
const error = ref('')
const successAdd = ref('')

const searchQuery = ref('')

const playerForm = ref({
  name: '',
  surname: '',
  main_shirt_number: 1,
  position: 'UK',
})

const positions = [
  { value: 'UK', label: 'Unknown' },
  { value: 'GK', label: 'Goalkeeper' },
  { value: 'DF', label: 'Defender' },
  { value: 'MF', label: 'Midfielder' },
  { value: 'FR', label: 'Forward' },
]

const canAddPlayers = computed(() => {
  return isAuthenticated.value && role.value === 'team_manager'
})

const filteredPlayers = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()

  if (!query) {
    return players.value
  }

  return players.value.filter((player) => {
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

async function loadPlayers() {
  loading.value = true
  error.value = ''

  try {
    const response = await playerApi.getAll()
    players.value = response.data
  } catch (err) {
    error.value = 'Could not load players.'
  } finally {
    loading.value = false
  }
}

async function createPlayer() {
  if (!canAddPlayers.value) {
    error.value = 'You must be signed in as a team manager to add players.'
    return
  }

  error.value = ''
  successAdd.value = ''

  try {
    await playerApi.create(playerForm.value)

    playerForm.value = {
      name: '',
      surname: '',
      main_shirt_number: 1,
      position: 'UK',
    }

    successAdd.value = 'Player added successfully.'

    await loadPlayers()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Could not add player.'
  }
}

onMounted(async () => {
  await loadUser()
  await loadPlayers()
})
</script>
<template>
  <main class="min-h-screen bg-gray-50 px-6 py-10">
    <div class="mx-auto max-w-7xl space-y-10">
      <section>
        <h1 class="text-4xl font-bold text-gray-900">
          Players
        </h1>

        <p class="mt-3 max-w-2xl text-gray-600">
          Search existing registered athletes and view their player pages.
        </p>
      </section>

      <section
        v-if="canAddPlayers"
        class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm"
      >
        <h2 class="text-2xl font-bold text-gray-900">
          Add Player
        </h2>

        <p class="mt-1 text-sm text-gray-600">
          Register a player so they can later be added to one of your teams.
        </p>

        <form
          @submit.prevent="createPlayer"
          class="mt-8 grid gap-5 md:grid-cols-2"
        >
          <label class="block">
            <span class="text-sm font-medium text-gray-700">
              Player name
            </span>

            <input
              v-model="playerForm.name"
              required
              type="text"
              class="mt-1 w-full rounded-xl border border-gray-300 px-4 py-2 outline-none focus:border-green-600"
              placeholder="Michael"
            />
          </label>

          <label class="block">
            <span class="text-sm font-medium text-gray-700">
              Player surname
            </span>

            <input
              v-model="playerForm.surname"
              required
              type="text"
              class="mt-1 w-full rounded-xl border border-gray-300 px-4 py-2 outline-none focus:border-green-600"
              placeholder="Favvas"
            />
          </label>

          <label class="block">
            <span class="text-sm font-medium text-gray-700">
              Main shirt number
            </span>

            <input
              v-model.number="playerForm.main_shirt_number"
              required
              type="number"
              min="1"
              max="99"
              class="mt-1 w-full rounded-xl border border-gray-300 px-4 py-2 outline-none focus:border-green-600"
              placeholder="10"
            />
          </label>

          <label class="block">
            <span class="text-sm font-medium text-gray-700">
              Position
            </span>

            <select
              v-model="playerForm.position"
              required
              class="mt-1 w-full rounded-xl border border-gray-300 px-4 py-2 outline-none focus:border-green-600"
            >
              <option
                v-for="position in positions"
                :key="position.value"
                :value="position.value"
              >
                {{ position.label }}
              </option>
            </select>
          </label>

          <div class="md:col-span-2">
            <button
              type="submit"
              class="rounded-xl bg-green-700 px-5 py-2 font-semibold text-white hover:bg-green-800"
            >
              Add Player
            </button>
          </div>

          <p
            v-if="successAdd"
            class="rounded-xl bg-green-50 p-3 text-sm text-green-700 md:col-span-2"
          >
            {{ successAdd }}
          </p>

          <p
            v-if="error"
            class="rounded-xl bg-red-50 p-3 text-sm text-red-700 md:col-span-2"
          >
            {{ error }}
          </p>
        </form>
      </section>

      <section class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
        <div class="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <h2 class="text-2xl font-bold text-gray-900">
              Search Players
            </h2>

            <p class="mt-1 text-sm text-gray-600">
              Check whether a player has already been registered.
            </p>
          </div>

          <label class="w-full md:max-w-sm">
            <span class="text-sm font-medium text-gray-700">
              Search
            </span>

            <input
              v-model="searchQuery"
              type="search"
              class="mt-1 w-full rounded-xl border border-gray-300 px-4 py-2 outline-none focus:border-green-600"
              placeholder="Search by name, shirt number, or position"
            />
          </label>
        </div>

        <p
          v-if="loading"
          class="mt-6 text-gray-600"
        >
          Loading players...
        </p>

        <p
          v-else-if="players.length === 0"
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
          class="mt-6 overflow-hidden rounded-xl border border-gray-200"
        >
          <table class="w-full text-left text-sm">
            <thead class="bg-gray-50 text-gray-700">
              <tr>
                <th class="px-4 py-3">Name</th>
                <th class="px-4 py-3">Surname</th>
                <th class="px-4 py-3">Shirt Number</th>
                <th class="px-4 py-3">Position</th>
              </tr>
            </thead>

            <tbody class="divide-y divide-gray-200">
              <tr
                v-for="player in filteredPlayers"
                :key="player.id"
                class="hover:bg-gray-50"
              >

                   <td class="px-4 py-3 text-gray-700">
                     <RouterLink
                    :to="{ name: 'player', params: { id: player.id } }"
                    class="font-semibold text-green-700 hover:text-green-800"
                  >
                  {{ player.name }}
                  </RouterLink>

                </td>


                   <td class="px-4 py-3 text-gray-700">
                     <RouterLink
                    :to="{ name: 'player', params: { id: player.id } }"
                    class="font-semibold text-green-700 hover:text-green-800"
                  >
                  {{ player.surname }}
                     </RouterLink>

                  </td>

                <td class="px-4 py-3 text-gray-700">
                  #{{ player.main_shirt_number }}
                </td>

                <td class="px-4 py-3 text-gray-700">
                  {{ getPositionLabel(player.position) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  </main>
</template>