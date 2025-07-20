<template>
  <div>
    <div v-if="results.length > 0" class="space-y-3">
      <div
        v-for="result in results"
        :key="result.id"
        class="bg-white p-4 rounded-lg shadow-sm border flex justify-between items-center"
      >
        <div @click="$emit('result-click', result)" class="flex-grow cursor-pointer pr-4">
          <h4 class="font-bold text-blue-700 hover:underline">{{ result.title }}</h4>
          <p class="text-sm text-gray-600 mt-1">
            {{ (result.content || result.snippet || '').substring(0, 150) }}...
          </p>
        </div>
        <button
            @click="$emit('import-click', result)"
            class="px-4 py-2 bg-green-500 text-white text-sm font-semibold rounded-md hover:bg-green-600 transition-colors shadow flex-shrink-0"
        >
            Import
        </button>
      </div>
    </div>
    <div v-else class="text-center py-8 px-4 bg-gray-50 rounded-lg">
      <p class="text-gray-500">No search results.</p>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

defineProps({
  results: {
    type: Array,
    required: true,
    default: () => []
  }
});

defineEmits(['result-click', 'import-click']);
</script>
