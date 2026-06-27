<script setup>
import { onMounted, ref } from "vue";
import { useRoute, RouterLink } from "vue-router";
import instance_api from "@/services/api.js";
import StandingsTable from "@/components/helpers/StandingsTable.vue";

const route = useRoute();

const tournamentId = route.params.id;

const teams = ref([]);
const registrations = ref([]);
const selectedTeamId = ref("");
const isAdmin = ref(true);
const isTeamManager = ref(true);

const generateMatchesOnCommence = ref(true);

const stadiums = ref([]);

const manualMatchForm = ref({
  team1: "",
  team2: "",
  stadium: "",
  scheduled_date: "",
});

async function fetchStadiums() {
  const response = await instance_api.get("/stadiums/");
  stadiums.value = normalizeList(response.data);
}

function toApiDateTime(datetimeLocalValue) {
  if (!datetimeLocalValue) {
    return null;
  }

  return new Date(datetimeLocalValue).toISOString();
}

async function createManualMatch() {
  loading.value = true;
  clearMessages();

  try {
    await instance_api.post("/matches/", {
      tournament: tournamentId,
      team1: manualMatchForm.value.team1,
      team2: manualMatchForm.value.team2,
      stadium: manualMatchForm.value.stadium,
      scheduled_date: toApiDateTime(manualMatchForm.value.scheduled_date),
    });

    success.value = "Match created successfully.";

    manualMatchForm.value = {
      team1: "",
      team2: "",
      stadium: "",
      scheduled_date: "",
    };

    await fetchMatches();
  } catch (err) {
    error.value = extractError(err);
  } finally {
    loading.value = false;
  }
}

async function fetchTeams() {
  const response = await instance_api.get("/teams/");
  teams.value = normalizeList(response.data);
}

async function fetchRegistrations() {
  const response = await instance_api.get(`/tournaments/${tournamentId}/registrations/`);
  registrations.value = normalizeList(response.data);
}

async function requestRegistration() {
  loading.value = true;
  clearMessages();

  try {
    await instance_api.post(`/tournaments/${tournamentId}/request-registration/`, {
      team_id: selectedTeamId.value,
    });

    success.value = "Registration request submitted successfully.";

    await fetchRegistrations();
  } catch (err) {
    error.value = extractError(err);
  } finally {
    loading.value = false;
  }
}

async function acceptRegistration(registration) {
  loading.value = true;
  clearMessages();

  try {
    await instance_api.post(`/tournament-registrations/${registration.id}/accept/`);

    success.value = "Registration accepted.";

    await Promise.all([
      fetchTournament(),
      fetchRegistrations(),
      fetchStandings(),
    ]);
  } catch (err) {
    error.value = extractError(err);
  } finally {
    loading.value = false;
  }
}

async function rejectRegistration(registration) {
  loading.value = true;
  clearMessages();

  try {
    await instance_api.post(`/tournament-registrations/${registration.id}/reject/`);

    success.value = "Registration rejected.";

    await fetchRegistrations();
  } catch (err) {
    error.value = extractError(err);
  } finally {
    loading.value = false;
  }
}

async function commenceTournament() {
  loading.value = true;
  clearMessages();

  try {
    const response = await instance_api.post(`/tournaments/${tournamentId}/commence/`, {
      generate_matches: generateMatchesOnCommence.value,
    });

    success.value = generateMatchesOnCommence.value
      ? `Tournament commenced. Generated ${response.data.generated_matches} matches.`
      : "Tournament commenced. You can now create matches manually.";

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

async function generateMatches() {
  loading.value = true;
  clearMessages();

  try {
    const response = await instance_api.post(`/tournaments/${tournamentId}/generate-matches/`);

    success.value = `Generated ${response.data.generated_matches} matches.`;

    await fetchMatches();
  } catch (err) {
    error.value = extractError(err);
  } finally {
    loading.value = false;
  }
}

function stadiumLabel(match) {
  if (match.stadium_name && match.stadium_city) {
    return `${match.stadium_name} - ${match.stadium_city}`;
  }

  if (match.stadium_name) {
    return match.stadium_name;
  }

  return "No stadium assigned";
}

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
    fetchTeams(),
    fetchRegistrations(),
    fetchStadiums(),
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
        <section
  v-if="tournament.status === 'Scheduled'"
  class="rounded-2xl bg-white p-6 shadow"
>
  <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
    <div>
      <h2 class="text-xl font-bold text-gray-900">
        Tournament Registration
      </h2>

      <p class="mt-1 text-sm text-gray-600">
        Team managers can request participation before the tournament begins.
      </p>
    </div>
  </div>

  <form
    v-if="isTeamManager"
    class="mt-4 grid gap-3 md:grid-cols-3"
    @submit.prevent="requestRegistration"
  >
    <div class="md:col-span-2">
      <label class="block text-sm font-medium text-gray-700">
        Select Team
      </label>

      <select
        v-model="selectedTeamId"
        class="mt-1 w-full rounded-lg border border-gray-300 p-3 focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
        required
      >
        <option value="" disabled>
          Choose a team
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
        Request Registration
      </button>
    </div>
  </form>
</section>

        <section
  v-if="isAdmin"
  class="rounded-2xl bg-white p-6 shadow"
>
  <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
    <div>
      <h2 class="text-xl font-bold text-gray-900">
        Registration Requests
      </h2>

      <p class="mt-1 text-sm text-gray-600">
        Admin can accept or reject teams before commencing the tournament.
      </p>
    </div>

    <button
      class="rounded-lg bg-gray-900 px-4 py-2 text-sm font-semibold text-white hover:bg-black disabled:opacity-50"
      :disabled="loading"
      @click="fetchRegistrations"
    >
      Refresh Requests
    </button>
  </div>

  <div
    v-if="registrations.length === 0"
    class="mt-4 rounded-xl border border-dashed border-gray-300 p-6 text-center text-gray-600"
  >
    No registration requests yet.
  </div>

  <div v-else class="mt-4 overflow-x-auto">
    <table class="min-w-full divide-y divide-gray-200 text-sm">
      <thead class="bg-gray-50">
        <tr>
          <th class="px-4 py-3 text-left font-semibold text-gray-700">Team</th>
          <th class="px-4 py-3 text-left font-semibold text-gray-700">Status</th>
          <th class="px-4 py-3 text-left font-semibold text-gray-700">Requested At</th>
          <th class="px-4 py-3 text-right font-semibold text-gray-700">Actions</th>
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
            {{ registration.status }}
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
                Accept
              </button>

              <button
                class="rounded-lg bg-red-600 px-3 py-2 text-xs font-semibold text-white hover:bg-red-700 disabled:opacity-50"
                :disabled="loading"
                @click="rejectRegistration(registration)"
              >
                Reject
              </button>
            </div>

            <span v-else class="text-gray-500">
              Decided
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
                {{ team.team_name }}
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

        <section
  v-if="isAdmin"
  class="rounded-2xl bg-white p-6 shadow"
>
  <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
    <div>
      <h2 class="text-xl font-bold text-gray-900">
        Admin Controls
      </h2>

      <p class="mt-1 text-sm text-gray-600">
        Commence the tournament and generate matches for accepted teams.
      </p>
    </div>

    <label class="flex items-center gap-2 text-sm text-gray-700">
  <input
    v-model="generateMatchesOnCommence"
    type="checkbox"
    class="rounded border-gray-300"
  />

  Automatically generate matches
</label>

    <div class="flex flex-col gap-2 sm:flex-row">
      <button
        v-if="tournament.status === 'Scheduled'"
        class="rounded-lg bg-purple-600 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-700 disabled:opacity-50"
        :disabled="loading || !tournament.teams || tournament.teams.length < 2"
        @click="commenceTournament"
      >
        Commence & Generate Matches
      </button>

      <button
        v-if="tournament.status === 'Ongoing'"
        class="rounded-lg bg-gray-900 px-4 py-2 text-sm font-semibold text-white hover:bg-black disabled:opacity-50"
        :disabled="loading"
        @click="generateMatches"
      >
        Generate Missing Matches
      </button>
    </div>
  </div>

  <p
    v-if="!tournament.teams || tournament.teams.length < 2"
    class="mt-3 text-sm text-red-700"
  >
    At least two accepted teams are required before commencing the tournament.
  </p>
</section>

        <section
  v-if="isAdmin && tournament.status !== 'Completed' && tournament.status !== 'Cancelled'"
  class="rounded-2xl bg-white p-6 shadow"
>
  <div>
    <h2 class="text-xl font-bold text-gray-900">
      Create Match Manually
    </h2>

    <p class="mt-1 text-sm text-gray-600">
      Assign two accepted teams, a date/time, and a stadium.
    </p>
  </div>

  <form
    class="mt-4 grid gap-4 md:grid-cols-2"
    @submit.prevent="createManualMatch"
  >
    <div>
      <label class="block text-sm font-medium text-gray-700">
        Team 1
      </label>

      <select
        v-model="manualMatchForm.team1"
        class="mt-1 w-full rounded-lg border border-gray-300 p-3"
        required
      >
        <option value="" disabled>Select first team</option>

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
        Team 2
      </label>

      <select
        v-model="manualMatchForm.team2"
        class="mt-1 w-full rounded-lg border border-gray-300 p-3"
        required
      >
        <option value="" disabled>Select second team</option>

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
        Stadium
      </label>

      <select
        v-model="manualMatchForm.stadium"
        class="mt-1 w-full rounded-lg border border-gray-300 p-3"
        required
      >
        <option value="" disabled>Select stadium</option>

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
        Date and Time
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
        Create Match
      </button>
    </div>
  </form>
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
                    Stadium:
                      <span class="font-semibold text-gray-800">
                        {{ stadiumLabel(match) }}
                      </span>
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