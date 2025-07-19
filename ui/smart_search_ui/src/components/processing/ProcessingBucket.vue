<template>
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
    <!-- Left side: List of documents -->
    <div class="lg:col-span-2 flex flex-col h-full">
      <div class="flex-shrink-0 flex justify-between items-center mb-4">
        <h2 class="text-2xl font-bold text-gray-800">Processing Bucket</h2>
        <div class="flex items-center gap-2">
            <span v-if="availableColorsInBucket.length > 0" class="text-sm font-medium text-gray-600">Select by color:</span>
            <button
              v-for="color in availableColorsInBucket"
              :key="color"
              @click="selectByColor(color)"
              :class="['h-6 w-6 rounded-full border-2 border-white shadow hover:ring-2', `bg-${color}-500`, `hover:ring-${color}-400`]"
            ></button>
            <button @click="selectAll" class="text-sm text-blue-600 hover:underline ml-2">All</button>
            <button @click="clearSelection" class="text-sm text-blue-600 hover:underline">None</button>
        </div>
      </div>
      <div class="flex-shrink-0 mb-4">
          <button
            @click="removeSelected"
            :disabled="selectedDocuments.length === 0"
            class="w-full px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 transition-colors shadow disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            Remove Selected from Bucket ({{ selectedDocuments.length }})
          </button>
      </div>
      <div class="flex-grow overflow-y-auto custom-scrollbar pr-4 -mr-4">
        <div v-if="queuedDocuments.length > 0" class="space-y-4">
          <ProcessingCard
            v-for="doc in queuedDocuments"
            :key="doc.id"
            :document="doc"
            :is-selected="selectedDocuments.includes(doc.id)"
            @selection-changed="toggleSelection"
          />
        </div>
        <div v-else class="text-center py-16 px-4 bg-gray-50 rounded-lg">
          <h3 class="text-lg font-medium text-gray-800">Your processing bucket is empty.</h3>
        </div>
      </div>
    </div>

    <!-- Right side: Analysis options -->
    <div class="lg:col-span-1 h-full">
        <AnalysisOptions @submit-analysis="handleAnalysisSubmit" :is-processing="isProcessing" />
        <div v-if="lastReportId" class="mt-4 p-4 bg-green-100 text-green-800 rounded-lg text-center">
            <p class="font-semibold">Processing Complete!</p>
            <p class="text-sm">Click the "Refresh" button in the Reports tab to see your new report.</p>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useProcessingStore } from '../../stores/processingStore';
import { useDocumentStore } from '../../stores/documentStore';
import { useNotificationStore } from '../../stores/notificationStore';
import { useProjectStore } from '../../stores/projectStore';
import { processingService } from '../../services/api';
import ProcessingCard from './ProcessingCard.vue';
import AnalysisOptions from './AnalysisOptions.vue';

const processingStore = useProcessingStore();
const documentStore = useDocumentStore();
const notificationStore = useNotificationStore();
const projectStore = useProjectStore();

const selectedDocuments = ref([]);
const isProcessing = ref(false);
const lastReportId = ref(null);

const queuedDocuments = computed(() => {
  return processingStore.processingQueue
    .map(docId => documentStore.documentsCache[docId])
    .filter(doc => doc);
});

const availableColorsInBucket = computed(() => {
    const colors = queuedDocuments.value
        .map(doc => doc.color)
        .filter(color => color && color !== 'default');
    return [...new Set(colors)];
});

const toggleSelection = (docId) => {
  const index = selectedDocuments.value.indexOf(docId);
  if (index > -1) {
    selectedDocuments.value.splice(index, 1);
  } else {
    selectedDocuments.value.push(docId);
  }
};

const selectByColor = (color) => {
    selectedDocuments.value = queuedDocuments.value
        .filter(doc => doc.color === color)
        .map(doc => doc.id);
};

const selectAll = () => {
    selectedDocuments.value = queuedDocuments.value.map(doc => doc.id);
};

const clearSelection = () => {
    selectedDocuments.value = [];
};

async function removeSelected() {
    if (selectedDocuments.value.length === 0) {
        notificationStore.addNotification({ message: 'No documents selected to remove.', type: 'warning' });
        return;
    }
    await processingStore.removeItemsFromQueue(selectedDocuments.value);
    clearSelection();
}

async function handleAnalysisSubmit(options) {
  const projectId = projectStore.activeProjectId;
  if (!projectId) {
    notificationStore.addNotification({ message: 'No active project selected.', type: 'warning' });
    return;
  }
  if (selectedDocuments.value.length === 0) {
      notificationStore.addNotification({ message: 'Please select at least one document.', type: 'warning' });
      return;
  }
  isProcessing.value = true;
  lastReportId.value = null;

  try {
    const jobDetails = {
        documentIds: selectedDocuments.value,
        analysisType: options.analysisType,
        prompt: options.prompt,
    };
    const response = await processingService.submitJob(projectId, jobDetails);

    lastReportId.value = response.jobId;
    notificationStore.addNotification({ message: response.message, type: 'success' });

    clearSelection();

  } catch (error) {
    // Handled by api service
  } finally {
    isProcessing.value = false;
  }
};
</script>
