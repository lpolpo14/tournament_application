<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, RouterLink } from "vue-router";
import instance_api from "@/services/api.js";

const route = useRoute();
const matchId = route.params.id;

// Temporary role placeholder.
// Change to "referee" to test score editing.
// Later this should come from real authentication.
const currentRole = ref("visitor");

const isReferee = computed(() => currentRole.value === "referee");

const match = ref(null);
const loading = ref(false);
const error = ref("");
const success = ref("");

const scoreForm = ref({
  team1_score: "",
  team2_score: "",
});

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

function formatDateTime(value) {
  if (!value) {
    return "Not set";
  }

  return new Date(value).toLocaleString();
}

function teamLabel(side) {
  if (!match.value) {
    return "Team";
  }

  if (side === "team1") {
    return match.value.team1_name || `Team #${match.value.team1}`;
  }

  return match.value.team2_name || `Team #${match.value.team2}`;
}

function stadiumLabel() {
  if (!match.value) {
    return "No stadium assigned";
  }

  if (match.value.stadium_name && match.value.stadium_city) {
    return `${match.value.stadium_name} - ${match.value.stadium_city}`;
  }

  if (match.value.stadium_name) {
    return match.value.stadium_name;
  }

  if (match.value.location) {
    return match.value.location;
  }

  return "No stadium assigned";
}

async function fetchMatch() {
  loading.value = true;
  clearMessages();

  try {
    const response = await instance_api.get(`/matches/${matchId}/`);
    match.value = response.data;

    scoreForm.value = {
      team1_score: response.data.team1_score ?? "",
      team2_score: response.data.team2_score ?? "",
    };
  } catch (err) {
    error.value = extractError(err);
  } finally {
    loading.value = false;
  }
}

async function submitScore() {
  loading.value = true;
  clearMessages();

  try {
    await instance_api.patch(`/matches/${matchId}/submit-score/`, {
      team1_score: Number(scoreForm.value.team1_score),
      team2_score: Number(scoreForm.value.team2_score),
    });

    success.value = "Score saved successfully.";

    await fetchMatch();
  } catch (err) {
    error.value = extractError(err);
  } finally {
    loading.value = false;
  }
}

onMounted(fetchMatch);
</script>

<template>
  <main class="min-h-screen bg-gray-100 p-6">
    <div class="mx-auto max-w-5xl space-y-6">
      <header class="rounded-2xl bg-white p-6 shadow">
        <RouterLink
          :to="{ name: 'tournaments' }"
          class="text-sm font-semibold text-blue-700 hover:text-blue-900"
        >
          ← Back to tournaments
        </RouterLink>

        <div v-if="match" class="mt-4 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">
              {{ teamLabel("team1") }} vs {{ teamLabel("team2") }}
            </h1>

            <p class="mt-2 text-gray-600">
              Match details, score information, and basic statistics.
            </p>
          </div>

          <span class="w-fit rounded-full bg-blue-100 px-4 py-2 text-sm font-semibold text-blue-800">
            {{ match.match_status }}
          </span>
        </div>

        <div v-else class="mt-4">
          <h1 class="text-3xl font-bold text-gray-900">
            Match
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
        <p class="text-gray-600">Loading match data...</p>
      </section>

      <template v-if="!loading && match">
        <section class="grid gap-4 md:grid-cols-4">
          <article class="rounded-2xl bg-white p-5 shadow">
            <p class="text-sm font-semibold text-gray-500">Team 1</p>
            <p class="mt-1 text-lg font-bold text-gray-900">
              {{ teamLabel("team1") }}
            </p>
          </article>

          <article class="rounded-2xl bg-white p-5 shadow">
            <p class="text-sm font-semibold text-gray-500">Team 2</p>
            <p class="mt-1 text-lg font-bold text-gray-900">
              {{ teamLabel("team2") }}
            </p>
          </article>

          <article class="rounded-2xl bg-white p-5 shadow">
            <p class="text-sm font-semibold text-gray-500">Date</p>
            <p class="mt-1 text-lg font-bold text-gray-900">
              {{ formatDateTime(match.scheduled_date) }}
            </p>
          </article>

          <article class="rounded-2xl bg-white p-5 shadow">
            <p class="text-sm font-semibold text-gray-500">Stadium</p>
            <p class="mt-1 text-lg font-bold text-gray-900">
              {{ stadiumLabel() }}
            </p>
          </article>
        </section>

        <section class="rounded-2xl bg-white p-6 shadow">
          <h2 class="text-xl font-bold text-gray-900">
            Score
          </h2>

          <div class="mt-4 rounded-xl bg-gray-100 px-6 py-8 text-center">
            <p class="text-sm font-semibold text-gray-500">
              Current Result
            </p>

            <p class="mt-2 text-5xl font-bold text-gray-900">
              {{ match.team1_score ?? "-" }}
              :
              {{ match.team2_score ?? "-" }}
            </p>

            <p class="mt-3 text-gray-600">
              {{ teamLabel("team1") }} vs {{ teamLabel("team2") }}
            </p>
          </div>
        </section>

        <section
          v-if="isReferee"
          class="rounded-2xl bg-white p-6 shadow"
        >
          <h2 class="text-xl font-bold text-gray-900">
            Referee Score Management
          </h2>

          <p class="mt-1 text-sm text-gray-600">
            Referees can add or edit final scores. Penalties, yellow cards, red cards,
            and detailed statistics can be added later.
          </p>

          <form
            class="mt-5 grid gap-4 md:grid-cols-3"
            @submit.prevent="submitScore"
          >
            <div>
              <label class="block text-sm font-medium text-gray-700">
                {{ teamLabel("team1") }} Score
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
                {{ teamLabel("team2") }} Score
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
                Save Score
              </button>
            </div>
          </form>
        </section>

        <section
          v-else
          class="rounded-2xl bg-white p-6 shadow"
        >
          <h2 class="text-xl font-bold text-gray-900">
            Match Scores and Statistics
          </h2>

          <p class="mt-1 text-sm text-gray-600">
            Visitors, team managers, and administrators can view the result and match information.
            Only referees can edit scores.
          </p>

          <div class="mt-5 grid gap-4 md:grid-cols-3">
            <article class="rounded-xl border border-gray-200 p-4">
              <p class="text-sm font-semibold text-gray-500">Status</p>
              <p class="mt-1 text-lg font-bold text-gray-900">
                {{ match.match_status }}
              </p>
            </article>

            <article class="rounded-xl border border-gray-200 p-4">
              <p class="text-sm font-semibold text-gray-500">Yellow Cards</p>
              <p class="mt-1 text-lg font-bold text-gray-900">
                Not recorded yet
              </p>
            </article>

            <article class="rounded-xl border border-gray-200 p-4">
              <p class="text-sm font-semibold text-gray-500">Red Cards</p>
              <p class="mt-1 text-lg font-bold text-gray-900">
                Not recorded yet
              </p>
            </article>
          </div>
        </section>
      </template>
    </div>
  </main>
</template>