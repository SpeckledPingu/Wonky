<template>
  <div class="p-4 space-y-6">
    <h2 class="text-xl font-semibold text-gray-800 border-b pb-2">Extraction Search</h2>
    <GuidedSummary />
    <div class="space-y-3">
        <h3 class="font-semibold text-lg text-gray-700">Extraction Search</h3>
        <div class="flex gap-2">
            <input
            type="search"
            v-model="searchQuery"
            placeholder="Search extractions (insights, policies...)"
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
    </div>
    <div class="p-4 bg-gray-50 rounded-lg border">
        <h4 class="font-semibold text-md text-gray-700 mb-3">Filters</h4>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
                <label class="block text-sm font-medium text-gray-600 mb-2">Content Types</label>
                <div class="flex flex-wrap gap-x-4 gap-y-2">
                    <label v-for="type in contentTypes" :key="type.id" class="flex items-center space-x-2 text-sm">
                        <input type="checkbox" :value="type.id" v-model="selectedContentTypes" class="rounded text-blue-500 focus:ring-blue-500">
                        <span>{{ type.label }}</span>
                    </label>
                </div>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-600 mb-2">Stance</label>
                 <div class="flex flex-wrap gap-x-4 gap-y-2">
                    <label v-for="stance in stances" :key="stance.id" class="flex items-center space-x-2 text-sm">
                        <input type="checkbox" :value="stance.id" v-model="selectedStances" class="rounded text-indigo-500 focus:ring-indigo-500">
                        <span>{{ stance.label }}</span>
                    </label>
                </div>
            </div>
        </div>
    </div>
    <div>
      <h3 class="font-semibold text-lg text-gray-700 mb-3">Results</h3>
      <SearchResults :results="formattedResults" @result-click="handleResultClick" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
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

const searchQuery = ref('');
const searchResults = ref([]);
const isLoading = ref(false);

const contentTypes = ref([
    { id: 'insight', label: 'Insights' },
    { id: 'policy', label: 'Policies' },
    { id: 'case_study', label: 'Case Studies' },
]);
const stances = ref([
    { id: 'pro', label: 'Pro' },
    { id: 'con', label: 'Con' },
]);

const selectedContentTypes = ref(['insight', 'policy', 'case_study']);
const selectedStances = ref(['pro', 'con']);

const formattedResults = computed(() => {
    return searchResults.value.map(ext => ({
        id: ext.id,
        sourceDocId: ext.source_doc_id,
        title: `[${ext.type.toUpperCase()}] from doc: ${ext.source_doc_id}`,
        content: ext.content
    }));
});

async function performSearch() {
  const projectId = projectStore.activeProjectId;
  if (!projectId) {
    notificationStore.addNotification({ message: 'No active project. Please select a project first.', type: 'warning' });
    return;
  }
  isLoading.value = true;
  searchResults.value = [];
  try {
    const response = await searchService.searchExtractions(
        projectId,
        searchQuery.value,
        selectedContentTypes.value,
        selectedStances.value,
        searchStore.guidingPrompt
    );
    searchResults.value = response.results;
    notificationStore.addNotification({ message: `Found ${response.results.length} extractions.`, type: 'success' });

    searchStore.startSummaryPolling(response.searchId);

  } catch (error) {
    // Handled by api service
  } finally {
    isLoading.value = false;
  }
};

const handleResultClick = (result) => {
  // --- FIX: Pass the activeProjectId to the viewDocument action ---
  documentStore.viewDocument(projectStore.activeProjectId, result.sourceDocId);
};
</script>
