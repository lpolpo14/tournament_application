import {createRouter, createWebHistory} from "vue-router";

import HomeView from '@/views/HomeView.vue'
import TeamsView from "@/views/TeamsView.vue";
import TeamView from "@/views/TeamView.vue";
import PlayersView from "@/views/PlayersView.vue";
import TournamentCreate from "@/views/TournamentCreate.vue";
import TournamentsView from "@/views/TournamentsView.vue";
import TournamentView from "@/views/TournamentView.vue";
import LoginView from "@/views/LoginView.vue";

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
        component: TeamView
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
    {
        path: "/tournament/:id",
        name: "tournament",
        component: TournamentView
    },
    {
        path: "/login",
        name: "login",
        component: LoginView
    }
]

const router = createRouter({
 history: createWebHistory(), // Change here
 routes,
})

export default router;