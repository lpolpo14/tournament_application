<template>
  <main class="bg-gray-50">
    <section class="mx-auto flex min-h-[70vh] max-w-7xl flex-col items-center justify-center px-6 py-20 text-center">
      <h1 class="text-5xl font-bold tracking-tight text-gray-900 md:text-6xl">
        Organize sports tournaments with ease.
      </h1>

      <p class="mt-6 max-w-2xl text-lg leading-8 text-gray-600">
        Unipi Sports helps teams, referees, and organizers manage tournaments,
        matches, players, and results in one simple platform.
      </p>

      <div class="mt-10">
        <RouterLink
          to="/login"
          class="rounded-xl bg-green-700 px-8 py-3 text-base font-semibold text-white shadow-sm hover:bg-green-800"
        >
          Begin
        </RouterLink>
      </div>
    </section>
  </main>
</template>