<template>
  <div id="main-app-container">
    <Login v-if="!authStore.isAuthenticated" />
    <!-- If logged in but no project is selected, show the project selection page -->
    <ProjectSelection v-else-if="!projectStore.activeProjectId" />
    <!-- Once a project is selected, show the main research app -->
    <ResearchApp v-else />
  </div>
</template>

<script setup>
import { useAuthStore } from './stores/authStore';
import { useProjectStore } from './stores/projectStore';
import Login from './pages/Login.vue';
import ProjectSelection from './pages/ProjectSelection.vue'; // <-- NEW
import ResearchApp from './ResearchApp.vue';

const authStore = useAuthStore();
const projectStore = useProjectStore();
</script>
