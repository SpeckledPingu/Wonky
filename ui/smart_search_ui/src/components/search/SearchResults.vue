<template>
  <div>
    <div v-if="results.length > 0" class="space-y-3">
      <div
        v-for="result in results"
        :key="result.id"
        @click="$emit('result-click', result)"
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

defineEmits(['result-click']);
</script>
