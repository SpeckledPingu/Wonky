<template>
  <div class="p-4 space-y-6">
    <!-- Component Title -->
    <h2 class="text-xl font-semibold text-gray-800 border-b pb-2">Document Content Search</h2>

    <!-- Guided Summary Section -->
    <GuidedSummary />

    <!-- Search Input Section -->
    <div class="space-y-3">
      <h3 class="font-semibold text-lg text-gray-700">Document Search</h3>
      <div class="flex gap-2">
        <input
          type="search"
          v-model="searchQuery"
          placeholder="Search all document content..."
          @keyup.enter="performSearch"
          class="flex-grow px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
        />
        <button @click="performSearch" class="px-6 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors shadow flex items-center justify-center" :disabled="isLoading">
           <svg v-if="isLoading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ isLoading ? 'Searching...' : 'Search' }}
        </button>
      </div>
      <div class="mt-2">
        <label for="search-mode" class="text-sm font-medium text-gray-600 mr-2">Search Mode:</label>
        <select id="search-mode" v-model="searchMode" class="px-3 py-1 border border-gray-300 rounded-md text-sm">
          <option value="semantic">Semantic</option>
          <option value="keyword">Keyword</option>
          <option value="hybrid">Hybrid</option>
        </select>
      </div>
    </div>

    <!-- Search Results Section -->
    <div>
      <h3 class="font-semibold text-lg text-gray-700 mb-3">Results</h3>
      <SearchResults :results="searchResults" @result-click="handleResultClick" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import GuidedSummary from './GuidedSummary.vue';
import SearchResults from './SearchResults.vue';
import { useDocumentStore } from '../../stores/documentStore';
import { useNotificationStore } from '../../stores/notificationStore';
import { useSearchStore } from '../../stores/searchStore';
import { useProjectStore } from '../../stores/projectStore';
import { searchService } from '../../services/api';

const documentStore = useDocumentStore();
const notificationStore = useNotificationStore();
const searchStore = useSearchStore();
const projectStore = useProjectStore();

const searchQuery = ref('data');
const searchMode = ref('semantic');
const searchResults = ref([]);
const isLoading = ref(false);

async function performSearch() {
  const projectId = projectStore.activeProjectId;
  if (!projectId) {
    notificationStore.addNotification({ message: 'No active project. Please select a project first.', type: 'warning' });
    return;
  }
  if (!searchQuery.value.trim()) {
    notificationStore.addNotification({ message: 'Please enter a search query.', type: 'warning' });
    return;
  }
  isLoading.value = true;
  searchResults.value = [];
  try {
    const response = await searchService.searchDocuments(
        projectId,
        searchQuery.value,
        searchMode.value,
        searchStore.guidingPrompt
    );

    response.results.forEach(doc => documentStore.upsertDocument(doc));
    searchResults.value = response.results;

    notificationStore.addNotification({ message: `Found ${response.results.length} results.`, type: 'success' });

    searchStore.startSummaryPolling(response.searchId);

  } catch (error) {
    // Handled by api service
  } finally {
    isLoading.value = false;
  }
};

const handleResultClick = (docId) => {
  // --- FIX: Pass the activeProjectId to the viewDocument action ---
  documentStore.viewDocument(projectStore.activeProjectId, docId);
};
</script>
