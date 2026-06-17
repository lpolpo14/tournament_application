<script setup>
import {onMounted, reactive, ref} from 'vue'
import {getTeams} from "@/services/api.js";

const teams = ref([]);
const loading = ref(false);
const error = ref('');

async function loadTeams(){
  loading.value = true;
  try{
    teams.value = getTeams();
  }
  catch(err){
    error.value = err.message;
  }
  finally{
    loading.value=false;
  }
}

onMounted(loadTeams)
</script>

<template>
  <main class="bg-white flex flex-box min-h-full">
    <section>
      <h2 class="font-bold text-center">Teams</h2>

      <p v-if="loading">Loading teams, please wait..</p>
      <p v-else-if="error">{{error}}</p>
      <p v-else-if="teams.length===0">No teams are registered.</p>

      <ul v-else>
        <li v-for="team in teams" :key="team.id">
          <span class="text-center">{{team.team_name}}</span>
          <span class="text-center">{{team.sport_name}}</span>
        </li>
      </ul>
    </section>
  </main>
</template>