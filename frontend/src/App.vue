<script setup>
import Header from "@/components/layouts/Header.vue";
import Footer from "@/components/layouts/Footer.vue";
import {useAuth} from "@/services/useAuth.js";
import {onMounted} from "vue";

const {loadUser} = useAuth()

onMounted(async() => {
  await loadUser()
})
</script>

<template>
  <div class="flex min-h-screen flex-col bg-gray-50">
    <Header />

    <div class="flex-1">
      <RouterView />
    </div>

    <Footer />
  </div>
</template>