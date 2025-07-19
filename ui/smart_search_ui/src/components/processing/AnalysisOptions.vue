<template>
  <div class="bg-gray-100 p-4 rounded-lg border border-gray-200">
    <h3 class="font-semibold text-lg text-gray-800 mb-4">Analysis Configuration</h3>
    <div class="space-y-4">
      <!-- Predefined Analysis Dropdown -->
      <div>
        <label for="analysis-type" class="block text-sm font-medium text-gray-700 mb-1">
          Predefined Analysis
        </label>
        <select
          id="analysis-type"
          v-model="selectedAnalysis"
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
        >
          <option value="none">None (Custom Prompt Only)</option>
          <option value="summarize">Summarize Key Findings</option>
          <option value="extract_themes">Extract Common Themes</option>
          <option value="compare_contrast">Compare and Contrast</option>
        </select>
      </div>

      <!-- Custom Prompt Textarea -->
      <div>
        <label for="custom-prompt" class="block text-sm font-medium text-gray-700 mb-1">
          Custom Prompt (optional)
        </label>
        <textarea
          id="custom-prompt"
          rows="4"
          v-model="customPrompt"
          placeholder="e.g., 'Identify all policy recommendations related to renewable energy and group them by country.'"
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
        ></textarea>
      </div>

      <!-- Submission Button -->
      <div>
        <button
          @click="submitForProcessing"
          class="w-full px-6 py-3 bg-green-600 text-white font-semibold rounded-md hover:bg-green-700 transition-colors shadow-md disabled:bg-gray-400 disabled:cursor-not-allowed"
          :disabled="isSubmitDisabled"
        >
          Process Selected Documents
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, defineEmits } from 'vue';

const emit = defineEmits(['submit-analysis']);

const selectedAnalysis = ref('none');
const customPrompt = ref('');

// The submit button should be disabled if no analysis or custom prompt is provided.
const isSubmitDisabled = computed(() => {
  return selectedAnalysis.value === 'none' && customPrompt.value.trim() === '';
});

const submitForProcessing = () => {
  if (!isSubmitDisabled.value) {
    console.log('Submitting for analysis with:', {
      analysis: selectedAnalysis.value,
      prompt: customPrompt.value,
    });
    emit('submit-analysis', {
      analysisType: selectedAnalysis.value,
      prompt: customPrompt.value,
    });
  }
};
</script>

<style scoped>
/* Scoped styles for AnalysisOptions component */
</style>
