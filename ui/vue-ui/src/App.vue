<template>
  <div id="app-container" class="flex flex-col min-h-screen bg-gray-100">
    <GlobalHeader />
    <main class="flex-1">
      <router-view />
    </main>
    <GlobalFooter /> </div>
</template>

<script setup>
import GlobalHeader from './components/GlobalHeader.vue';
import GlobalFooter from './components/GlobalFooter.vue'; // Optional
// No specific script needed for App.vue in this basic setup
</script>

<style>
/* You can add global styles here or in style.css */
body {
  margin: 0;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f3f4f6; /* Tailwind gray-100, ensures consistency */
}

#app-container {
  display: flex;
  flex-direction: column;
}

main {
  flex-grow: 1; /* Ensures main content takes up available space */
}
</style>
