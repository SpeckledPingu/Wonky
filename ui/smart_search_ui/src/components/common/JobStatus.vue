<template>
  <div v-if="jobStatusStore.activeJobId" class="fixed bottom-4 left-4 z-50">
    <div class="p-4 rounded-lg shadow-lg bg-gray-800 text-white flex items-center gap-4">
      <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <div>
        <p class="font-semibold">Processing Report...</p>
        <p class="text-sm text-gray-300">{{ jobStatusStore.jobMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useJobStatusStore } from '../../stores/jobStatusStore';

const jobStatusStore = useJobStatusStore();
</script>
