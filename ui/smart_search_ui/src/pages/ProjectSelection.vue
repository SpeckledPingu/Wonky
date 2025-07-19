<template>
  <div class="min-h-screen bg-gray-100 p-8">
    <div class="max-w-6xl mx-auto">
      <div class="flex justify-between items-center mb-8 pb-4 border-b">
        <h1 class="text-3xl font-bold text-gray-800">Your Projects</h1>
        <button @click="authStore.logout()" class="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600">Logout</button>
      </div>

      <div v-if="projectStore.isLoading" class="text-center text-gray-500">
        Loading projects...
      </div>

      <div v-else-if="projectStore.availableProjects.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- Project Cards -->
        <div
          v-for="project in projectStore.availableProjects"
          :key="project.id"
          @click="launchProject(project.id)"
          class="bg-white p-6 rounded-lg shadow-md hover:shadow-xl hover:ring-2 hover:ring-indigo-500 transition-all cursor-pointer"
        >
          <h2 class="text-xl font-semibold text-gray-900 mb-2">{{ project.name }}</h2>
          <p class="text-gray-600 text-sm">{{ project.description || 'No description provided.' }}</p>
        </div>
        <!-- New Project Card -->
        <div @click="showCreateModal = true" class="bg-gray-50 border-2 border-dashed p-6 rounded-lg flex items-center justify-center text-gray-500 hover:text-indigo-600 hover:border-indigo-500 transition-colors cursor-pointer">
          <p class="font-semibold">+ Create New Project</p>
        </div>
      </div>

      <div v-else class="text-center text-gray-500 mt-16">
        <h2 class="text-2xl font-semibold">No Projects Found</h2>
        <p class="mt-2">Get started by creating your first project.</p>
        <button @click="showCreateModal = true" class="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">Create Project</button>
      </div>
    </div>
    <!-- --- NEW: Create Project Modal --- -->
    <CreateProjectModal v-if="showCreateModal" @close="showCreateModal = false" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../stores/authStore';
import { useProjectStore } from '../stores/projectStore';
import CreateProjectModal from '../components/common/CreateProjectModal.vue'; // <-- IMPORTED

const authStore = useAuthStore();
const projectStore = useProjectStore();
const showCreateModal = ref(false); // <-- ADDED

const launchProject = (projectId) => {
  projectStore.setActiveProject(projectId);
};

onMounted(() => {
    projectStore.fetchProjects();
});
</script>
