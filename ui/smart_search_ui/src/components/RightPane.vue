<template>
  <div class="flex flex-col h-full bg-gray-50">
    <!-- Header/Tabs for the Right Pane -->
    <div class="flex-shrink-0 border-b border-gray-200">
      <nav class="flex space-x-2 p-2 bg-white">
        <button @click="activeTab = 'viewer'" :class="tabClass('viewer')">Document Viewer</button>
        <button @click="activeTab = 'saved'" :class="tabClass('saved')">Saved Results ({{ savedResultsStore.savedResults.length }})</button>
        <button @click="activeTab = 'reports'" :class="tabClass('reports')">Reports ({{ reportsStore.reports.length }})</button>
        <button @click="activeTab = 'processing'" :class="tabClass('processing')">Processing ({{ processingStore.processingQueue.length }})</button>
      </nav>
    </div>

    <!-- Content Area for the Right Pane -->
    <div class="flex-grow p-4 overflow-y-auto custom-scrollbar">
      <div v-show="activeTab === 'viewer'"><DocumentViewer /></div>
      <div v-show="activeTab === 'saved'"><SavedResultsTab /></div>
      <div v-show="activeTab === 'reports'"><ReportsTab /></div>
      <div v-show="activeTab === 'processing'"><ProcessingBucket /></div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useProcessingStore } from '../stores/processingStore';
import { useReportsStore } from '../stores/reportsStore';
import { useDocumentStore } from '../stores/documentStore';
import { useSavedResultsStore } from '../stores/savedResultsStore'; // <-- IMPORTED
import ProcessingBucket from './processing/ProcessingBucket.vue';
import ReportsTab from './reports/ReportsTab.vue';
import DocumentViewer from './viewer/DocumentViewer.vue';

import SavedResultsTab from './saved_results/SavedResultsTab.vue'; // <-- IMPORTED

const processingStore = useProcessingStore();
const reportsStore = useReportsStore();
const documentStore = useDocumentStore();

// For future work
const savedResultsStore = useSavedResultsStore(); // <-- INITIALIZED

const activeTab = ref('viewer');

watch(() => documentStore.activeDocumentId, (newId) => {
    if (newId) {
        activeTab.value = 'viewer';
    }
});

const tabClass = (tabName) => {
  return [
    'px-4 py-2 text-sm font-medium rounded-md transition-colors',
    activeTab.value === tabName
      ? 'bg-indigo-500 text-white shadow'
      : 'text-gray-600 hover:bg-gray-200',
  ];
};
</script>
