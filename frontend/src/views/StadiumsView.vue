<script setup>
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import instance_api from "@/services/api.js";
import { useAuth } from "@/services/useAuth.js";

const { role, isAuthenticated, isLoaded, loadUser } = useAuth();

const stadiums = ref([]);
const loading = ref(false);
const error = ref("");
const success = ref("");

const form = ref({
  name: "",
  city: "",
  address: "",
});

const canManageStadiums = computed(() => {
  return isAuthenticated.value && role.value === "sports_admin";
});

function normalizeStadiums(data) {
  return Array.isArray(data) ? data : data.results || [];
}

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

async function fetchStadiums() {
  loading.value = true;
  clearMessages();

  try {
    const response = await instance_api.get("/stadiums/");
    stadiums.value = normalizeStadiums(response.data);
  } catch (err) {
    error.value = extractError(err);
  } finally {
    loading.value = false;
  }
}

async function createStadium() {
  if (!canManageStadiums.value) {
    error.value = "Only sports administrators can create stadiums.";
    return;
  }

  loading.value = true;
  clearMessages();

  try {
    const payload = {
      name: form.value.name,
      city: form.value.city,
      address: form.value.address,
    };

    await instance_api.post("/stadiums/", payload);

    success.value = "Stadium created successfully.";

    form.value = {
      name: "",
      city: "",
      address: "",
    };

    await fetchStadiums();
  } catch (err) {
    error.value = extractError(err);
  } finally {
    loading.value = false;
  }
}

async function deleteStadium(stadium) {
  if (!canManageStadiums.value) {
    error.value = "Only sports administrators can delete stadiums.";
    return;
  }

  const confirmed = window.confirm(
    `Are you sure you want to delete ${stadium.name}?`
  );

  if (!confirmed) {
    return;
  }

  loading.value = true;
  clearMessages();

  try {
    await instance_api.delete(`/stadiums/${stadium.id}/`);

    success.value = "Stadium deleted successfully.";

    await fetchStadiums();
  } catch (err) {
    error.value = extractError(err);
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  if (!isLoaded.value) {
    await loadUser();
  }

  await fetchStadiums();
});
</script>
<template>
  <main class="min-h-screen bg-gray-100 p-6">
    <div class="mx-auto max-w-6xl space-y-6">
      <header class="flex flex-col gap-4 rounded-2xl bg-white p-6 shadow md:flex-row md:items-center md:justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">
            Stadiums
          </h1>

          <p class="mt-2 text-gray-600">
            View stadiums used for tournament matches.
        </p>
        </div>

        <RouterLink
          :to="{ name: 'tournaments' }"
          class="rounded-lg bg-gray-900 px-4 py-2 text-center font-semibold text-white hover:bg-black"
        >
          Back to Tournaments
        </RouterLink>
      </header>

      <section v-if="error" class="rounded-lg bg-red-100 p-4">
        <h2 class="font-semibold text-red-900">Error</h2>
        <pre class="mt-2 whitespace-pre-wrap text-sm text-red-800">{{ error }}</pre>
      </section>

      <section v-if="success" class="rounded-lg bg-green-100 p-4 text-green-800">
        {{ success }}
      </section>

      <section
        v-if="canManageStadiums"
        class="rounded-2xl bg-white p-6 shadow"
      >
        <h2 class="text-xl font-semibold text-gray-900">
          Create Stadium
        </h2>

        <p class="mt-1 text-sm text-gray-600">
          Add a stadium that can later be assigned to matches.
        </p>

        <form class="mt-5 grid gap-5 md:grid-cols-2" @submit.prevent="createStadium">
          <div>
            <label class="block text-sm font-medium text-gray-700">
              Stadium Name
            </label>

            <input
              v-model="form.name"
              type="text"
              class="mt-1 w-full rounded-lg border border-gray-300 p-3 focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
              placeholder="Example: Peace and Friendship Stadium"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">
              City
            </label>

            <input
              v-model="form.city"
              type="text"
              class="mt-1 w-full rounded-lg border border-gray-300 p-3 focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
              placeholder="Example: Piraeus"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">
              Address
            </label>

            <input
              v-model="form.address"
              type="text"
              class="mt-1 w-full rounded-lg border border-gray-300 p-3 focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
              placeholder="Example: Neo Faliro"
            />
          </div>

          <div class="md:col-span-2">
            <button
              type="submit"
              class="rounded-lg bg-green-600 px-5 py-3 font-semibold text-white hover:bg-green-700 disabled:opacity-50"
              :disabled="loading"
            >
              {{ loading ? "Saving..." : "Create Stadium" }}
            </button>
          </div>
        </form>
      </section>

      <section class="rounded-2xl bg-white p-6 shadow">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-semibold text-gray-900">
            All Stadiums
          </h2>

          <button
            class="rounded-lg bg-gray-900 px-4 py-2 text-sm font-semibold text-white hover:bg-black disabled:opacity-50"
            :disabled="loading"
            @click="fetchStadiums"
          >
            Refresh
          </button>
        </div>

        <div v-if="loading" class="mt-6 text-gray-600">
          Loading stadiums...
        </div>

        <div
          v-else-if="stadiums.length === 0"
          class="mt-6 rounded-xl border border-dashed border-gray-300 p-8 text-center"
        >
          <p class="text-gray-600">
            No stadiums found.
          </p>
        </div>

        <div v-else class="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <article
            v-for="stadium in stadiums"
            :key="stadium.id"
            class="rounded-xl border border-gray-200 bg-white p-5 shadow-sm transition hover:-translate-y-1 hover:shadow-md"
          >
            <div>
              <h3 class="text-lg font-bold text-gray-900">
                {{ stadium.name }}
              </h3>

              <p class="mt-1 text-sm text-gray-600">
                {{ stadium.city }}
              </p>
            </div>

            <div class="mt-4 space-y-2 text-sm text-gray-700">
              <p>
                <span class="font-semibold">Address:</span>
                {{ stadium.address || "Not set" }}
              </p>
            </div>

            <div
                v-if="canManageStadiums"
                class="mt-5"
            >
              <!-- Hide this for now.
            <button
              class="w-full rounded-lg bg-red-600 px-3 py-2 text-center text-sm font-semibold text-white hover:bg-red-700 disabled:opacity-50"
              :disabled="loading"
              @click="deleteStadium(stadium)"
            >
              Delete Stadium
            </button>
            -->
          </div>
          </article>
        </div>
      </section>
    </div>
  </main>
</template>