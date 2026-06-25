<script setup>
import Header from "@/components/layouts/Header.vue";
import Footer from "@/components/layouts/Footer.vue";
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