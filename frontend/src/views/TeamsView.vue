<script setup>
import {onMounted, ref} from "vue";
import instance_api from "@/services/api.js";

const teams = ref([])
const loading = ref(false)
const error = ref("")
const successful_add = ref("")

const team_form = ref({
  team_name: "",
  sport_name: ""
})

async function loadTeams() {
  loading.value = true;
  error.value = "";
  try{
    const response = await instance_api.get("/teams/")
    teams.value = response.data
  }
  catch (err){
    error.value = "Could not load teams."
  }
  finally{
    loading.value = false;
  }
}


async function createTeam(){
  error.value = ""
  successful_add.value = ""
  try{
    await instance_api.post("/teams/", team_form.value)
    successful_add.value = "Team added successfully!"
    await loadTeams() // Good practice:)
  }
  catch (err){
    error.value = "Could not add team.";
    /*
    Important! Add a validation method for API response. Backend could send reasoning why team
    could not be created.
     */
  }
}



onMounted(loadTeams)
</script>

<template>
  <main class="bg-white flex flex-box min-h-full">
    <section>
      <div class="grid gap-8">
        <form @submit.prevent="createTeam" class="rounded-2xl p-6 shadow-sm">
          <h2 class="text-xl">Create Team</h2>
          <label class="mt-5 block">
          <span class="text-sm font-medium text-gray-700">Team name</span>
          <input
            v-model="team_form.team_name"
            required
            type="text"
            class="mt-1 w-full rounded-xl border border-gray-300 px-4 py-2 outline-none focus:border-green-600"
            placeholder="Panthers"
          />
        </label>

        <label class="mt-4 block">
          <span class="text-sm font-medium text-gray-700">Sport</span>
          <input
            v-model="team_form.sport_name"
            required
            type="text"
            class="mt-1 w-full rounded-xl border border-gray-300 px-4 py-2 outline-none focus:border-green-600"
            placeholder="Football"
          />
        </label>

          <button type=submit class="mt-6 rounded-xl bg-blue-500 px-4 py-2 font-bold">
            Create Team
          </button>

          <p v-if="success" class="mt-4 rounded-xl bg-green-50 p-3 text-sm text-green-700">
          {{ success }}
        </p>

        <p v-if="error" class="mt-4 rounded-xl bg-red-50 p-3 text-sm text-red-700">
          {{ error }}
        </p>
        </form>
      </div>
    </section>

    <section>
      <p v-if="loading" class="text-gray-600">Teams are loading</p>
      <p v-else-if="teams.length === 0" class="text-gray-600">No teams are available.</p>

      <div v-else class="grid gap-4 md:grid-cols-3">
          <RouterLink
            v-for="team in teams"
            :key="team.id"
            :to="{ name: 'team', params: { id: team.id } }"
            class="rounded-xl border border-gray-200 p-4 hover:border-green-600 hover:bg-green-50"
          >
            <h3 class="text-lg font-bold">{{ team.team_name }}</h3>
            <p class="text-sm text-gray-600">{{ team.sport_name }}</p>
            <p class="mt-3 text-sm">
              Players:
              <span class="font-semibold">{{ team.player_count }}</span>
            </p>
          </RouterLink>
        </div>
    </section>
  </main>
</template>