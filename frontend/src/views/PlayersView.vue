<script setup>
import {onMounted, ref} from "vue";
import instance_api from "@/services/api.js";

const players = ref([])
const loading = ref(false)
const error = ref("")
const success_add = ref("")


const player_form = ref({
  name: "",
  surname: "",
  main_shirt_number: 1,
  position: "UN",
});

const positions = [
  { value: "UN", label: "Unknown" },
  { value: "GK", label: "Goalkeeper" },
  { value: "DF", label: "Defender" },
  { value: "MF", label: "Midfielder" },
  { value: "FW", label: "Forward" },
];

async function createPlayer(){
  error.value = ""
  success_add.value = ""
  try{
    await instance_api.post("/players/", player_form.value)

    // It is genuinely so nice how reactive this all is...
    player_form.value ={
    name: "",
    surname: "",
    main_shirt_number: 1,
    position: "UN",
    };

    success_add.value = "Player added successfully!"
    await loadPlayers();
  }
  catch (err){
    error.value = "Could not add player";
    /*
    Add reasoning from the back end in the future!
     */
  }
}

async function loadPlayers() {
  loading.value = true;
  error.value = "";

  try {
    const response = await instance_api.get("/players/");
    players.value = response.data;
  } catch (err) {
    error.value = "Could not load players.";
  } finally {
    loading.value = false;
  }
}

onMounted(loadPlayers)

</script>

<template>
<main>
  <section>
          <div class="grid gap-8">
        <form @submit.prevent="createPlayer" class="rounded-2xl p-6 shadow-sm">
          <h2 class="text-xl">Create Player</h2>
          <label class="mt-5 block">
          <span class="text-sm font-medium text-gray-700">Player Name</span>
          <input
            v-model="player_form.name"
            required
            type="text"
            class="mt-1 w-full rounded-xl border border-gray-300 px-4 py-2 outline-none focus:border-green-600"
            placeholder="Michael"
          />
        </label>

        <label class="mt-4 block">
          <span class="text-sm font-medium text-gray-700">Player's Surname</span>
          <input
            v-model="player_form.surname"
            required
            type="text"
            class="mt-1 w-full rounded-xl border border-gray-300 px-4 py-2 outline-none focus:border-green-600"
            placeholder="Favvas"
          />
        </label>

          <label class="mt-4 block">
          <span class="text-sm font-medium text-gray-700">Player's Shirt Number</span>
          <input
            v-model="player_form.main_shirt_number"
            required
            type="number"
            min="1"
            max="999"
            class="mt-1 w-full rounded-xl border border-gray-300 px-4 py-2 outline-none focus:border-green-600"
            placeholder="53"
          />
        </label>

          <label class="mt-4 block">
          <span class="text-sm font-medium text-gray-700">Player's Position</span>
          <select v-model="player_form.position"
          class="w-full rounded-xl focus:border-green-600">
            <option
            v-for="position in positions"
            :key="position.value"
            :value="position.value">
              {{position.label}}
            </option>

          </select>
        </label>

          <button type=submit class="mt-6 rounded-xl bg-blue-500 px-4 py-2 font-bold hover:bg-blue-700">
            Create Player
          </button>

          <p v-if="success_add" class="mt-4 rounded-xl bg-green-50 p-3 text-sm text-green-700">
          {{ success_add }}
        </p>

        <p v-if="error" class="mt-4 rounded-xl bg-red-50 p-3 text-sm text-red-700">
          {{ error }}
        </p>
        </form>
      </div>
  </section>
  <section>
    <p v-if="loading" class="text-gray-600">Loading players..</p>

    <p v-else-if="players.length === 0" class="text-gray-600">No players are available.</p>

    <div v-else class="grid gap-2">
      <article v-for="player in players"
      :key="player.id">
      <h3 class="text-lg font-bold">{{ player.full_name }}</h3>
            <p class="text-sm text-gray-600">
              Shirt number: #{{ player.main_shirt_number }}
            </p>
            <p class="text-sm text-gray-600">
              Position: {{ player.position }}
            </p>
      </article>
    </div>
  </section>
</main>
</template>

<style scoped>

</style>