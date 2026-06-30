<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()

const selectedLocale = computed({
  get() {
    return locale.value
  },
  set(value) {
    locale.value = value
    localStorage.setItem('locale', value)
  },
})
</script>

<template>
  <footer class="border-t border-gray-200 bg-white">
    <div class="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-6 text-sm text-gray-600 md:flex-row md:items-center md:justify-between">
      <p>
        © 2026 {{ t('common.appName') }}. {{ t('common.allRightsReserved') }}
      </p>

      <div class="flex items-center gap-2">
        <label for="language" class="font-medium">
          {{ t('common.language') }}
        </label>

        <select
          id="language"
          v-model="selectedLocale"
          class="rounded-md border border-gray-300 bg-white px-3 py-1 text-sm focus:border-green-700 focus:outline-none"
        >
          <option value="en">
            {{ t('common.english') }}
          </option>
          <option value="el">
            {{ t('common.greek') }}
          </option>
        </select>
      </div>
    </div>
  </footer>
</template>