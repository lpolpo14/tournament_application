import {createRouter, createWebHistory} from "vue-router";

import HomeView from '@/views/HomeView.vue'
import TeamsView from "@/views/TeamsView.vue";

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
    }
]

const router = createRouter({
 history: createWebHistory(), // Change here
 routes,
})

export default router;