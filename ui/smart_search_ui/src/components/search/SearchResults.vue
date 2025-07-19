<template>
  <div>
    <div v-if="results.length > 0" class="space-y-3">
      <div
        v-for="result in results"
        :key="result.id"
        @click="onResultClick(result)"
        class="bg-white p-4 rounded-lg shadow-sm border border-transparent hover:border-blue-500 hover:shadow-md cursor-pointer transition-all"
      >
        <h4 class="font-bold text-blue-700">{{ result.title }}</h4>
        <p class="text-sm text-gray-600 mt-1">
          {{ (result.content || result.snippet || '').substring(0, 150) }}...
        </p>
      </div>
    </div>
    <div v-else class="text-center py-8 px-4 bg-gray-50 rounded-lg">
      <p class="text-gray-500">No search results.</p>
    </div>

    <!-- Pagination Controls -->
    <div v-if="results.length > 0" class="mt-6 flex justify-center items-center space-x-2">
        <button class="px-4 py-2 text-sm bg-white border rounded-md hover:bg-gray-100">&laquo; Prev</button>
        <span class="text-sm text-gray-700">Page 1 of 1</span>
        <button class="px-4 py-2 text-sm bg-white border rounded-md hover:bg-gray-100">Next &raquo;</button>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  results: {
    type: Array,
    required: true,
    default: () => []
  }
});

const emit = defineEmits(['result-click']);

// Emit the entire result object on click
const onResultClick = (result) => {
  // For documents, result.id is the docId. For extractions, we pass the whole object.
  emit('result-click', result.sourceDocId ? result : result.id);
};
</script>
