<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center" @click.self="$emit('close')">
    <div class="relative mx-auto p-8 border w-full max-w-lg shadow-lg rounded-md bg-white">
      <h3 class="text-2xl font-semibold mb-6">Select a Project</h3>
      <div v-if="projectStore.isLoading" class="text-center">Loading...</div>
      <div v-else class="space-y-4">
        <div
          v-for="project in projectStore.availableProjects"
          :key="project.id"
          @click="$emit('select-project', project.id)"
          class="p-4 border rounded-md hover:bg-gray-100 cursor-pointer"
        >
          <p class="font-medium">{{ project.name }}</p>
        </div>
        <div v-if="projectStore.availableProjects.length === 0" class="text-gray-500">
          No projects found for this user.
        </div>
      </div>
      <button @click="$emit('close')" class="absolute top-4 right-4 text-gray-500 hover:text-gray-800">&times;</button>
    </div>
  </div>
</template>

<script setup>
import { defineEmits } from 'vue';
import { useProjectStore } from '../../stores/projectStore';

defineEmits(['close', 'select-project']);
const projectStore = useProjectStore();
</script>
