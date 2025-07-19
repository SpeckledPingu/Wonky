<template>
  <div class="min-h-screen bg-gray-100 p-8">
    <div class="max-w-4xl mx-auto">
      <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold text-gray-800">Your Dashboard</h1>
        <button @click="authStore.logout()" class="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600">Logout</button>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- Research App Card -->
        <div @click="openProjectModal" class="bg-white p-6 rounded-lg shadow-md hover:shadow-xl transition-shadow cursor-pointer">
          <h2 class="text-xl font-semibold text-gray-900 mb-2">Research Analytics Platform</h2>
          <p class="text-gray-600">The advanced tool for searching, processing, and analyzing your research documents.</p>
        </div>
        <!-- Placeholder for future apps -->
        <div class="bg-white p-6 rounded-lg shadow-md opacity-50">
          <h2 class="text-xl font-semibold text-gray-900 mb-2">Future App 1</h2>
          <p class="text-gray-600">Description for another tool will go here.</p>
        </div>
      </div>
    </div>
    <ProjectModal v-if="showModal" @close="showModal = false" @select-project="launchApp" />
  </div>
</template>

<script setup>
import { ref, defineEmits } from 'vue';
import { useAuthStore } from '../stores/authStore';
import ProjectModal from '../components/common/ProjectModal.vue';

const emit = defineEmits(['launch-app']);
const authStore = useAuthStore();
const showModal = ref(false);

const openProjectModal = () => {
  showModal.value = true;
};

const launchApp = (projectId) => {
  showModal.value = false;
  emit('launch-app', projectId);
};
</script>
