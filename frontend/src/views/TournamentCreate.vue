<script setup>
import { ref } from "vue";
import { useRouter, RouterLink } from "vue-router";
import instance_api from "@/services/api.js";

const router = useRouter();

const loading = ref(false);
const error = ref("");

const form = ref({
  name: "",
  sport: "",
  location: "",
  start_date: "",
  end_date: "",
  status: "Scheduled",
});

function extractError(err) {
  if (err.response?.data) {
    return JSON.stringify(err.response.data, null, 2);
  }

  return err.message || "Something went wrong.";
}

function toApiDateTime(datetimeLocalValue) {
  if (!datetimeLocalValue) {
    return null;
  }

  return new Date(datetimeLocalValue).toISOString();
}

async function createTournament() {
  loading.value = true;
  error.value = "";

  try {
    const payload = {
      name: form.value.name,
      sport: form.value.sport,
      location: form.value.location,
      start_date: toApiDateTime(form.value.start_date),
      end_date: toApiDateTime(form.value.end_date),
      status: form.value.status,
    };

    const response = await instance_api.post("/tournaments/", payload);

    const createdTournamentId = response.data.id;

    if (createdTournamentId) {
      router.push({
        name: "tournament",
        params: { id: createdTournamentId },
      });
    } else {
      router.push({ name: "tournaments" });
    }
  } catch (err) {
    error.value = extractError(err);
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <main class="min-h-screen bg-gray-100 p-6">
    <div class="mx-auto max-w-3xl space-y-6">
      <header class="rounded-2xl bg-white p-6 shadow">
        <RouterLink
          :to="{ name: 'tournaments' }"
          class="text-sm font-semibold text-blue-700 hover:text-blue-900"
        >
          ← Back to tournaments
        </RouterLink>

        <h1 class="mt-4 text-3xl font-bold text-gray-900">
          Create Tournament
        </h1>

        <p class="mt-2 text-gray-600">
          Fill in the basic tournament information.
        </p>
      </header>

      <section v-if="error" class="rounded-lg bg-red-100 p-4">
        <h2 class="font-semibold text-red-900">Error</h2>
        <pre class="mt-2 whitespace-pre-wrap text-sm text-red-800">{{ error }}</pre>
      </section>

      <section class="rounded-2xl bg-white p-6 shadow">
        <form class="space-y-5" @submit.prevent="createTournament">
          <div>
            <label class="block text-sm font-medium text-gray-700">
              Tournament Name
            </label>

            <input
              v-model="form.name"
              type="text"
              class="mt-1 w-full rounded-lg border border-gray-300 p-3 focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
              placeholder="Example: Unipi Football Cup"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">
              Sport
            </label>

            <input
              v-model="form.sport"
              type="text"
              class="mt-1 w-full rounded-lg border border-gray-300 p-3 focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
              placeholder="Example: Football"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">
              Location
            </label>

            <input
              v-model="form.location"
              type="text"
              class="mt-1 w-full rounded-lg border border-gray-300 p-3 focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
              placeholder="Example: Piraeus"
              required
            />
          </div>

          <div class="grid gap-5 md:grid-cols-2">
            <div>
              <label class="block text-sm font-medium text-gray-700">
                Start Date
              </label>

              <input
                v-model="form.start_date"
                type="datetime-local"
                class="mt-1 w-full rounded-lg border border-gray-300 p-3 focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
                required
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">
                End Date
              </label>

              <input
                v-model="form.end_date"
                type="datetime-local"
                class="mt-1 w-full rounded-lg border border-gray-300 p-3 focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
                required
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">
              Status
            </label>

            <select
              v-model="form.status"
              class="mt-1 w-full rounded-lg border border-gray-300 p-3 focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
            >
              <option value="Scheduled">Scheduled</option>
              <option value="Ongoing">Ongoing</option>
              <option value="Completed">Completed</option>
              <option value="Cancelled">Cancelled</option>
            </select>
          </div>

          <div class="flex flex-col gap-3 pt-4 sm:flex-row">
            <button
              type="submit"
              class="rounded-lg bg-green-600 px-5 py-3 font-semibold text-white hover:bg-green-700 disabled:opacity-50"
              :disabled="loading"
            >
              {{ loading ? "Creating..." : "Create Tournament" }}
            </button>

            <RouterLink
              :to="{ name: 'tournaments' }"
              class="rounded-lg bg-gray-200 px-5 py-3 text-center font-semibold text-gray-800 hover:bg-gray-300"
            >
              Cancel
            </RouterLink>
          </div>
        </form>
      </section>
    </div>
  </main>
</template>