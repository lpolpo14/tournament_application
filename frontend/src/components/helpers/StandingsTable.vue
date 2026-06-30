<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  standings: {
    type: Array,
    required: true,
  },
})

const { t } = useI18n()
</script>

<template>
  <div class="overflow-x-auto rounded-xl border border-gray-200 bg-white">
    <table class="min-w-full text-sm">
      <thead class="bg-gray-100 text-gray-700">
        <tr>
          <th class="px-4 py-3 text-left">
            {{ t('standingsTable.rank') }}
          </th>

          <th class="px-4 py-3 text-left">
            {{ t('standingsTable.team') }}
          </th>

          <th class="px-4 py-3 text-center">
            {{ t('standingsTable.played') }}
          </th>

          <th class="px-4 py-3 text-center">
            {{ t('standingsTable.wins') }}
          </th>

          <th class="px-4 py-3 text-center">
            {{ t('standingsTable.draws') }}
          </th>

          <th class="px-4 py-3 text-center">
            {{ t('standingsTable.losses') }}
          </th>

          <th class="px-4 py-3 text-center">
            {{ t('standingsTable.goalsScored') }}
          </th>

          <th class="px-4 py-3 text-center">
            {{ t('standingsTable.goalsConceded') }}
          </th>

          <th class="px-4 py-3 text-center">
            {{ t('standingsTable.goalDifference') }}
          </th>

          <th class="px-4 py-3 text-center">
            {{ t('standingsTable.points') }}
          </th>
        </tr>
      </thead>

      <tbody>
        <tr
          v-for="team in standings"
          :key="team.team_id"
          class="border-t border-gray-200 hover:bg-gray-50"
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