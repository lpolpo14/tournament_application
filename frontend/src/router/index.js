import {createRouter, createWebHistory} from "vue-router";

import HomeView from '@/views/HomeView.vue'
import TeamsView from "@/views/TeamsView.vue";
import PlayersView from "@/views/PlayersView.vue";
import MatchView from "@/views/MatchView.vue";

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
    }
]

const router = createRouter({
 history: createWebHistory(), // Change here
 routes,
})

export default router;