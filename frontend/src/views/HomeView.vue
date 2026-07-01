<template>
  <main class="bg-gray-50">
    <section class="mx-auto flex min-h-[70vh] max-w-7xl flex-col items-center justify-center px-6 py-20 text-center">
      <h1 class="text-5xl font-bold tracking-tight text-gray-900 md:text-6xl">
        {{ t('home.title') }}
      </h1>

      <p class="mt-6 max-w-2xl text-lg leading-8 text-gray-600">
        {{ t('home.subtitle') }}
      </p>

      <div class="mt-10">
        <RouterLink
          to="/login"
          class="rounded-xl bg-green-700 px-8 py-3 text-base font-semibold text-white shadow-sm hover:bg-green-800"
        >
          {{ t('home.begin') }}
        </RouterLink>
      </div>
    </section>
  </main>
</template>

<script setup>
// Used for Localization.
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>