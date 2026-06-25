<script setup>
import { onMounted, ref } from "vue";
import { useRoute, RouterLink } from "vue-router";
import instance_api from "@/services/api.js";
import StandingsTable from "@/components/helpers/StandingsTable.vue";

const route = useRoute();

const tournamentId = route.params.id;

const tournament = ref(null);
const matches = ref([]);
const standings = ref([]);

const scoreForms = ref({});

const loading = ref(false);
const error = ref("");
const success = ref("");

function clearMessages() {
  error.value = "";
  success.value = "";
}

function extractError(err) {
  if (err.response?.data) {
    return JSON.stringify(err.response.data, null, 2);
  }

  return err.message || "Something went wrong.";
}

function normalizeList(data) {
  return Array.isArray(data) ? data : data.results || [];
}

function formatDate(value) {
  if (!value) {
    return "Not set";
  }

  return new Date(value).toLocaleDateString();
}

function formatDateTime(value) {
  if (!value) {
    return "Not set";
  }

  return new Date(value).toLocaleString();
}

function teamLabel(match, side) {
  if (side === "team1") {
    return match.team1_name || `Team #${match.team1}`;
  }

  return match.team2_name || `Team #${match.team2}`;
}

async function fetchTournament() {
  const response = await instance_api.get(`/tournaments/${tournamentId}/`);
  tournament.value = response.data;
}

async function fetchMatches() {
  const response = await instance_api.get("/matches/", {
    params: {
      tournament: tournamentId,
    },
  });

  matches.value = normalizeList(response.data);

  for (const match of matches.value) {
    scoreForms.value[match.id] = {
      team1_score: match.team1_score ?? "",
      team2_score: match.team2_score ?? "",
    };
  }
}

async function fetchStandings() {
  const response = await instance_api.get(`/tournaments/${tournamentId}/standings/`);
  standings.value = normalizeList(response.data);
}

async function loadPage() {
  loading.value = true;
  clearMessages();

  try {
    await Promise.all([
      fetchTournament(),
      fetchMatches(),
      fetchStandings(),
    ]);
  } catch (err) {
    error.value = extractError(err);
  } finally {
    loading.value = false;
  }
}

async function submitScore(match) {
  loading.value = true;
  clearMessages();

  try {
    const form = scoreForms.value[match.id];

    await instance_api.patch(`/matches/${match.id}/submit-score/`, {
      team1_score: Number(form.team1_score),
      team2_score: Number(form.team2_score),
    });

    success.value = "Score submitted successfully.";

    await Promise.all([
      fetchMatches(),
      fetchStandings(),
    ]);
  } catch (err) {
    error.value = extractError(err);
  } finally {
    loading.value = false;
  }
}

onMounted(loadPage);
</script>

<template>
  <main class="min-h-screen bg-gray-100 p-6">
    <div class="mx-auto max-w-7xl space-y-6">
      <header class="rounded-2xl bg-white p-6 shadow">
        <RouterLink
          :to="{ name: 'tournaments' }"
          class="text-sm font-semibold text-blue-700 hover:text-blue-900"
        >
          ← Back to tournaments
        </RouterLink>

        <div v-if="tournament" class="mt-4 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">
              {{ tournament.name }}
            </h1>

            <p class="mt-2 text-gray-600">
              {{ tournament.sport }} tournament in {{ tournament.location }}
            </p>
          </div>

          <span class="w-fit rounded-full bg-blue-100 px-4 py-2 text-sm font-semibold text-blue-800">
            {{ tournament.status }}
          </span>
        </div>

        <div v-else class="mt-4">
          <h1 class="text-3xl font-bold text-gray-900">
            Tournament
          </h1>
        </div>
      </header>

      <section v-if="error" class="rounded-lg bg-red-100 p-4">
        <h2 class="font-semibold text-red-900">Error</h2>
        <pre class="mt-2 whitespace-pre-wrap text-sm text-red-800">{{ error }}</pre>
      </section>

      <section v-if="success" class="rounded-lg bg-green-100 p-4 text-green-800">
        {{ success }}
      </section>

      <section v-if="loading" class="rounded-2xl bg-white p-6 shadow">
        <p class="text-gray-600">Loading tournament data...</p>
      </section>

      <template v-if="!loading && tournament">
        <section class="grid gap-4 md:grid-cols-4">
          <article class="rounded-2xl bg-white p-5 shadow">
            <p class="text-sm font-semibold text-gray-500">Sport</p>
            <p class="mt-1 text-lg font-bold text-gray-900">
              {{ tournament.sport }}
            </p>
          </article>

          <article class="rounded-2xl bg-white p-5 shadow">
            <p class="text-sm font-semibold text-gray-500">Location</p>
            <p class="mt-1 text-lg font-bold text-gray-900">
              {{ tournament.location }}
            </p>
          </article>

          <article class="rounded-2xl bg-white p-5 shadow">
            <p class="text-sm font-semibold text-gray-500">Start Date</p>
            <p class="mt-1 text-lg font-bold text-gray-900">
              {{ formatDate(tournament.start_date) }}
            </p>
          </article>

          <article class="rounded-2xl bg-white p-5 shadow">
            <p class="text-sm font-semibold text-gray-500">End Date</p>
            <p class="mt-1 text-lg font-bold text-gray-900">
              {{ formatDate(tournament.end_date) }}
            </p>
          </article>
        </section>

        <section class="rounded-2xl bg-white p-6 shadow">
          <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 class="text-xl font-bold text-gray-900">
                Participating Teams
              </h2>

              <p class="mt-1 text-sm text-gray-600">
                Teams currently assigned to this tournament.
              </p>
            </div>

            <button
              class="rounded-lg bg-gray-900 px-4 py-2 text-sm font-semibold text-white hover:bg-black disabled:opacity-50"
              :disabled="loading"
              @click="loadPage"
            >
              Refresh
            </button>
          </div>

          <div
            v-if="!tournament.teams || tournament.teams.length === 0"
            class="mt-4 rounded-xl border border-dashed border-gray-300 p-6 text-center text-gray-600"
          >
            No teams assigned yet.
          </div>

          <div v-else class="mt-4 flex flex-wrap gap-2">
            <span
              v-for="team in tournament.teams"
              :key="typeof team === 'object' ? team.id : team"
              class="rounded-full bg-green-100 px-4 py-2 text-sm font-semibold text-green-800"
            >
              <template v-if="typeof team === 'object'">
                {{ team.name }}
              </template>

              <template v-else>
                Team #{{ team }}
              </template>
            </span>
          </div>
        </section>

        <section class="rounded-2xl bg-white p-6 shadow">
          <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 class="text-xl font-bold text-gray-900">
                Standings
              </h2>

              <p class="mt-1 text-sm text-gray-600">
                Automatically calculated from completed matches.
              </p>
            </div>

            <button
              class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
              :disabled="loading"
              @click="fetchStandings"
            >
              Refresh Standings
            </button>
          </div>

          <div
            v-if="standings.length === 0"
            class="mt-4 rounded-xl border border-dashed border-gray-300 p-6 text-center text-gray-600"
          >
            No standings available yet.
          </div>

          <StandingsTable
          v-else
          class="mt-4"
          :standings="standings"
          />
        </section>

        <section class="rounded-2xl bg-white p-6 shadow">
          <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 class="text-xl font-bold text-gray-900">
                Matches
              </h2>

              <p class="mt-1 text-sm text-gray-600">
                View matches and submit final scores.
              </p>
            </div>

            <button
              class="rounded-lg bg-gray-900 px-4 py-2 text-sm font-semibold text-white hover:bg-black disabled:opacity-50"
              :disabled="loading"
              @click="fetchMatches"
            >
              Refresh Matches
            </button>
          </div>

          <div
            v-if="matches.length === 0"
            class="mt-4 rounded-xl border border-dashed border-gray-300 p-6 text-center text-gray-600"
          >
            No matches created yet.
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
                    {{ teamLabel(match, "team1") }}
                    vs
                    {{ teamLabel(match, "team2") }}
                  </h3>

                  <p class="mt-1 text-sm text-gray-600">
                    Match #{{ match.id }}
                  </p>

                  <p class="mt-1 text-sm text-gray-600">
                    Date:
                    {{ formatDateTime(match.scheduled_date) }}
                  </p>

                  <p class="mt-1 text-sm text-gray-600">
                    Location:
                    {{ match.location }}
                  </p>

                  <p class="mt-1 text-sm">
                    Status:
                    <span
                      class="font-semibold"
                      :class="{
                        'text-green-700': match.match_status === 'Completed',
                        'text-blue-700': match.match_status === 'Scheduled',
                        'text-red-700': match.match_status === 'Cancelled'
                      }"
                    >
                      {{ match.match_status }}
                    </span>
                  </p>
                </div>

                <div class="rounded-xl bg-gray-100 px-6 py-4 text-center">
                  <p class="text-sm font-semibold text-gray-500">Score</p>

                  <p class="mt-1 text-3xl font-bold text-gray-900">
                    {{ match.team1_score ?? "-" }}
                    :
                    {{ match.team2_score ?? "-" }}
                  </p>
                </div>
              </div>

              <form
                class="mt-4 grid gap-3 md:grid-cols-3"
                @submit.prevent="submitScore(match)"
              >
                <div>
                  <label class="block text-sm font-medium text-gray-700">
                    {{ teamLabel(match, "team1") }} Score
                  </label>

                  <input
                    v-model="scoreForms[match.id].team1_score"
                    type="number"
                    min="0"
                    class="mt-1 w-full rounded-lg border border-gray-300 p-2 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
                    required
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">
                    {{ teamLabel(match, "team2") }} Score
                  </label>

                  <input
                    v-model="scoreForms[match.id].team2_score"
                    type="number"
                    min="0"
                    class="mt-1 w-full rounded-lg border border-gray-300 p-2 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
                    required
                  />
                </div>

                <div class="flex items-end">
                  <button
                    type="submit"
                    class="w-full rounded-lg bg-purple-600 px-4 py-2 font-semibold text-white hover:bg-purple-700 disabled:opacity-50"
                    :disabled="loading"
                  >
                    Submit Score
                  </button>
                </div>
              </form>
            </article>
          </div>
        </section>
      </template>
    </div>
  </main>
</template>