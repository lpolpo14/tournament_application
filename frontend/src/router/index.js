import {createRouter, createWebHistory} from "vue-router";

import HomeView from '@/views/HomeView.vue'
import TeamsView from "@/views/TeamsView.vue";
import TeamView from "@/views/TeamView.vue";
import PlayersView from "@/views/PlayersView.vue";
import TournamentCreate from "@/views/TournamentCreate.vue";
import TournamentsView from "@/views/TournamentsView.vue";
import TournamentView from "@/views/TournamentView.vue";
import LoginView from "@/views/LoginView.vue";
import StadiumsView from "@/views/StadiumsView.vue";
import MatchComponent from "@/views/MatchComponent.vue";
import PlayerView from "@/views/PlayerView.vue";
import RegisterView from "@/views/RegisterView.vue";
import RefereeView from "@/views/RefereeView.vue";

// Based on https://github.com/fussionlab/VueJs-Django
const routes = [
    {
        path: '/',
        name: 'home',
        component: HomeView
    },
    {
        path: '/login',
        name: 'login',
        component: LoginView
    },
    {
        path: '/register',
        name: 'register',
        component: RegisterView
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
    },
    {
        path: "/stadiums",
        name: "stadiums",
        component: StadiumsView,
    },
    {
        path: "/matches/:id",
        name: "match",
        component: MatchComponent,
    },
    {
        path: '/players/:id',
        name: 'player',
        component: PlayerView,
    },
    {
        path: '/referee',
        name: 'referee',
        component: RefereeView,
    },
]

const router = createRouter({
 history: createWebHistory(),
 routes,
})

export default router;