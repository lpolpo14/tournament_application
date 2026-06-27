<script setup>
defineProps({
  standings: {
    type: Array,
    required: true,
  },

  highlightTeamId: {
    type: Number,
    default: null,
  },
});
</script>

<template>
  <div class="overflow-x-auto rounded-xl border border-gray-200 bg-white">
    <table class="min-w-full text-sm">
      <thead class="bg-gray-100 text-gray-700">
        <tr>
          <th class="px-4 py-3 text-left">#</th>
          <th class="px-4 py-3 text-left">Team</th>
          <th class="px-4 py-3 text-center">P</th>
          <th class="px-4 py-3 text-center">W</th>
          <th class="px-4 py-3 text-center">D</th>
          <th class="px-4 py-3 text-center">L</th>
          <th class="px-4 py-3 text-center">GS</th>
          <th class="px-4 py-3 text-center">GC</th>
          <th class="px-4 py-3 text-center">GD</th>
          <th class="px-4 py-3 text-center">Pts</th>
        </tr>
      </thead>

      <tbody>
        <tr
          v-for="team in standings"
          :key="team.team_id"
          class="border-t border-gray-200 hover:bg-gray-50"
          :class="{
            'bg-green-50': highlightTeamId && team.team_id === highlightTeamId
          }"
        >
          <td class="px-4 py-3 font-semibold">
            {{ team.position }}
          </td>

          <td class="px-4 py-3 font-semibold text-gray-900">
            {{ team.team_name }}
          </td>

          <td class="px-4 py-3 text-center">
            {{ team.played_games }}
          </td>

          <td class="px-4 py-3 text-center">
            {{ team.wins }}
          </td>

          <td class="px-4 py-3 text-center">
            {{ team.draws }}
          </td>

          <td class="px-4 py-3 text-center">
            {{ team.losses }}
          </td>

          <td class="px-4 py-3 text-center">
            {{ team.goals_scored }}
          </td>

          <td class="px-4 py-3 text-center">
            {{ team.goals_conceded }}
          </td>

          <td
            class="px-4 py-3 text-center font-semibold"
            :class="{
              'text-green-700': team.goals_scored - team.goals_conceded > 0,
              'text-red-700': team.goals_scored - team.goals_conceded < 0,
              'text-gray-700': team.goals_scored - team.goals_conceded === 0
            }"
          >
            {{ team.goals_scored - team.goals_conceded }}
          </td>

          <td class="px-4 py-3 text-center font-bold text-gray-900">
            {{ team.points }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>