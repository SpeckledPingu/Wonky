<template>
  <div class="p-4 border-b border-gray-200 bg-white">
    <label for="project-select" class="block text-sm font-medium text-gray-700 mb-1">
      Current Project
    </label>
    <div v-if="projectStore.isLoading" class="text-sm text-gray-500 animate-pulse">
      Loading projects...
    </div>
    <select
      v-else
      id="project-select"
      :value="projectStore.activeProjectId"
      @change="handleProjectChange($event.target.value)"
      class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
    >
      <option v-if="projectStore.availableProjects.length === 0" disabled>
        No projects found
      </option>
      <option
        v-for="project in projectStore.availableProjects"
        :key="project.id"
        :value="project.id"
      >
        {{ project.name }}
      </option>
    </select>
  </div>
</template>

<script setup>
import { useProjectStore } from '../../stores/projectStore';

const projectStore = useProjectStore();

const handleProjectChange = (newProjectId) => {
    projectStore.setActiveProject(Number(newProjectId));
};
</script>
