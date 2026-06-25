<script setup>
const currentYear = new Date().getFullYear()
</script>

<template>
  <footer class="border-t border-gray-200 bg-white">
    <div class="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-6 text-sm text-gray-600 md:flex-row md:items-center md:justify-between">
      <p>
        © {{ currentYear }} Unipi Sports. All rights reserved.
      </p>

      <div class="flex items-center gap-2">
        <label for="language" class="font-medium">
          Language
        </label>

        <select
          id="language"
          class="rounded-md border border-gray-300 bg-white px-3 py-1 text-sm focus:border-green-700 focus:outline-none"
        >
          <option value="en">English</option>
          <option value="el">Greek</option>
        </select>
      </div>
    </div>
  </footer>
</template>