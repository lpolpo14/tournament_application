import {createRouter, createWebHistory} from "vue-router";

import HomeView from '@/views/HomeView.vue'
import TeamsView from "@/views/TeamsView.vue";
import PlayersView from "@/views/PlayersView.vue";
import TournamentCreate from "@/views/TournamentCreate.vue";
import TournamentsView from "@/views/TournamentsView.vue";

// Based on https://github.com/fussionlab/VueJs-Django
const routes = [
    {
        path: '/',
        name: 'home',
        component: HomeView
    },
    {
        path: '/teams',
        name: 'teams',
        component: TeamsView
    },
    {
        path: '/players',
        name: 'players',
        component: PlayersView
    },
    {
        path: '/teams/:id',
        name: 'team',
        component: TeamsView
    },
    {
        path: "/tournaments",
        name: "tournaments",
        component: TournamentsView
     },
    {
        path: "/tournaments/create",
        name: "tournament-create",
        component: TournamentCreate
    },
]

const router = createRouter({
 history: createWebHistory(), // Change here
 routes,
})

export default router;