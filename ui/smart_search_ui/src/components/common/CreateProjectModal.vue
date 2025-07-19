<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center" @click.self="$emit('close')">
    <div class="relative mx-auto p-8 border w-full max-w-lg shadow-lg rounded-md bg-white">
      <h3 class="text-2xl font-semibold mb-6">Create New Project</h3>
      <form @submit.prevent="handleCreateProject" class="space-y-4">
        <div>
          <label for="project-name" class="block text-sm font-medium text-gray-700">Project Name</label>
          <input v-model="form.name" type="text" id="project-name" required class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
        </div>
        <div>
          <label for="project-description" class="block text-sm font-medium text-gray-700">Description (Optional)</label>
          <textarea v-model="form.description" id="project-description" rows="3" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"></textarea>
        </div>
        <div v-if="error" class="text-red-500 text-sm">
            {{ error }}
        </div>
        <div class="pt-4 flex justify-end space-x-3">
          <button type="button" @click="$emit('close')" class="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300">
            Cancel
          </button>
          <button type="submit" class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">
            Create Project
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, defineEmits } from 'vue';
import { useProjectStore } from '../../stores/projectStore';

const emit = defineEmits(['close']);
const projectStore = useProjectStore();
const form = ref({ name: '', description: '' });
const error = ref('');

async function handleCreateProject() {
    error.value = '';
    const success = await projectStore.createProject(form.value);
    if (success) {
        emit('close'); // Close the modal on success
    } else {
        error.value = 'Failed to create project. Please try again.';
    }
}
</script>
