<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-800">Saved Results</h2>
      <button
        @click="refreshResults"
        class="px-4 py-2 text-sm bg-white border rounded-md hover:bg-gray-100 flex items-center gap-2"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h5m11 2a9 9 0 11-2.236-6.132" />
        </svg>
        Refresh
      </button>
    </div>

    <div v-if="savedResultsStore.savedResults.length > 0" class="space-y-4">
      <div
        v-for="doc in savedResultsStore.savedResults"
        :key="doc.id"
        class="bg-white p-4 rounded-lg shadow-sm border flex justify-between items-center"
      >
        <div @click="viewDocument(doc.id)" class="flex-grow cursor-pointer hover:text-indigo-600">
            <h3 class="font-bold text-lg">{{ doc.title }}</h3>
            <!-- --- FIX: Removed truncate and added logic for summary/snippet --- -->
            <p class="text-sm text-gray-600 mt-1">
                {{ doc.summary || (doc.content ? doc.content.substring(0, 250) + '...' : 'No content preview available.') }}
            </p>
        </div>
        <button @click="removeResult(doc.id)" class="ml-4 text-red-500 hover:text-red-700 flex-shrink-0">
            Remove
        </button>
      </div>
    </div>
    <div v-else class="text-center py-16 px-4 bg-gray-50 rounded-lg">
      <h3 class="text-lg font-medium text-gray-800">No saved results.</h3>
      <p class="text-gray-500 mt-2">
        Click the "Save Result" button on a document to track it here.
      </p>
    </div>
  </div>
</template>

<script setup>
import { useSavedResultsStore } from '../../stores/savedResultsStore';
import { useProjectStore } from '../../stores/projectStore';
import { useDocumentStore } from '../../stores/documentStore';
import { useNotificationStore } from '../../stores/notificationStore';

const savedResultsStore = useSavedResultsStore();
const projectStore = useProjectStore();
const documentStore = useDocumentStore();
const notificationStore = useNotificationStore();

const viewDocument = (docId) => {
    documentStore.viewDocument(projectStore.activeProjectId, docId);
};

const removeResult = (docId) => {
    savedResultsStore.removeResult(projectStore.activeProjectId, docId);
};

const refreshResults = () => {
    const projectId = projectStore.activeProjectId;
    if (projectId) {
        savedResultsStore.fetchSavedResults(projectId);
        notificationStore.addNotification({ message: 'Saved results have been refreshed.', type: 'info' });
    }
};
</script>
