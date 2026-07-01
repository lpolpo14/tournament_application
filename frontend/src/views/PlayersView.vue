<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { playerApi } from '@/services/api.js'
import { useAuth } from '@/services/useAuth.js'

const { t } = useI18n()
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

// Used for translating the backend representation to the localized frontend version.
const positions = [
  { value: 'UK', labelKey: 'players.positions.unknown' },
  { value: 'GK', labelKey: 'players.positions.goalkeeper' },
  { value: 'DF', labelKey: 'players.positions.defender' },
  { value: 'MF', labelKey: 'players.positions.midfielder' },
  { value: 'FR', labelKey: 'players.positions.forward' },
]

const canAddPlayers = computed(() => {
  return isAuthenticated.value && role.value === 'team_manager'
})

const filteredPlayers = computed(() => {
  /*
  Simple function that filters players using multiple fields.
   */
  const query = searchQuery.value.trim().toLowerCase()

  if (!query) {
    return players.value
  }

  return players.value.filter((player) => {
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

function getPositionLabel(positionValue) {
  const position = positions.find((item) => item.value === positionValue)
  return position ? t(position.labelKey) : positionValue
}

async function loadPlayers() {
  loading.value = true
  error.value = ''

  try {
    const response = await playerApi.getAll()
    players.value = response.data
  } catch (err) {
    error.value = t('players.errors.loadFailed')
  } finally {
    loading.value = false
  }
}

async function createPlayer() {
  if (!canAddPlayers.value) { // Simple check
    error.value = t('players.errors.addForbidden')
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

    successAdd.value = t('players.successAdded')

    await loadPlayers()
  } catch (err) {
    error.value = err.response?.data?.detail || t('players.errors.addFailed')
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
          {{ t('players.title') }}
        </h1>

        <p class="mt-3 max-w-2xl text-gray-600">
          {{ t('players.subtitle') }}
        </p>
      </section>

      <section
        v-if="canAddPlayers"
        class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm"
      >
        <h2 class="text-2xl font-bold text-gray-900">
          {{ t('players.addTitle') }}
        </h2>

        <p class="mt-1 text-sm text-gray-600">
          {{ t('players.addSubtitle') }}
        </p>

        <form
          @submit.prevent="createPlayer"
          class="mt-8 grid gap-5 md:grid-cols-2"
        >
          <label class="block">
            <span class="text-sm font-medium text-gray-700">
              {{ t('players.fields.name') }}
            </span>

            <input
              v-model="playerForm.name"
              required
              type="text"
              class="mt-1 w-full rounded-xl border border-gray-300 px-4 py-2 outline-none focus:border-green-600"
              :placeholder="t('players.placeholders.name')"
            />
          </label>

          <label class="block">
            <span class="text-sm font-medium text-gray-700">
              {{ t('players.fields.surname') }}
            </span>

            <input
              v-model="playerForm.surname"
              required
              type="text"
              class="mt-1 w-full rounded-xl border border-gray-300 px-4 py-2 outline-none focus:border-green-600"
              :placeholder="t('players.placeholders.surname')"
            />
          </label>

          <label class="block">
            <span class="text-sm font-medium text-gray-700">
              {{ t('players.fields.mainShirtNumber') }}
            </span>

            <input
              v-model.number="playerForm.main_shirt_number"
              required
              type="number"
              min="1"
              max="99"
              class="mt-1 w-full rounded-xl border border-gray-300 px-4 py-2 outline-none focus:border-green-600"
              :placeholder="t('players.placeholders.shirtNumber')"
            />
          </label>

          <label class="block">
            <span class="text-sm font-medium text-gray-700">
              {{ t('players.fields.position') }}
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
                {{ t(position.labelKey) }}
              </option>
            </select>
          </label>

          <div class="md:col-span-2">
            <button
              type="submit"
              class="rounded-xl bg-green-700 px-5 py-2 font-semibold text-white hover:bg-green-800"
            >
              {{ t('players.addButton') }}
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
              {{ t('players.searchTitle') }}
            </h2>

            <p class="mt-1 text-sm text-gray-600">
              {{ t('players.searchSubtitle') }}
            </p>
          </div>

          <label class="w-full md:max-w-sm">
            <span class="text-sm font-medium text-gray-700">
              {{ t('players.searchLabel') }}
            </span>

            <input
              v-model="searchQuery"
              type="search"
              class="mt-1 w-full rounded-xl border border-gray-300 px-4 py-2 outline-none focus:border-green-600"
              :placeholder="t('players.searchPlaceholder')"
            />
          </label>
        </div>

        <p
          v-if="loading"
          class="mt-6 text-gray-600"
        >
          {{ t('players.loading') }}
        </p>

        <p
          v-else-if="players.length === 0"
          class="mt-6 rounded-xl border border-dashed border-gray-300 p-6 text-gray-600"
        >
          {{ t('players.empty') }}
        </p>

        <p
          v-else-if="filteredPlayers.length === 0"
          class="mt-6 rounded-xl border border-dashed border-gray-300 p-6 text-gray-600"
        >
          {{ t('players.noSearchResults') }}
        </p>

        <div
          v-else
          class="mt-6 overflow-hidden rounded-xl border border-gray-200"
        >
          <table class="w-full text-left text-sm">
            <thead class="bg-gray-50 text-gray-700">
              <tr>
                <th class="px-4 py-3">
                  {{ t('players.table.name') }}
                </th>
                <th class="px-4 py-3">
                  {{ t('players.table.surname') }}
                </th>
                <th class="px-4 py-3">
                  {{ t('players.table.shirtNumber') }}
                </th>
                <th class="px-4 py-3">
                  {{ t('players.table.position') }}
                </th>
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