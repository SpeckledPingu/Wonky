<template>
  <div v-if="documentStore.isLoading" class="text-center p-10">
    <p class="animate-pulse text-lg font-semibold text-gray-500">Loading Document...</p>
  </div>
  <div v-else-if="document" class="space-y-4">
    <div class="flex justify-between items-start gap-4">
      <h2 class="text-2xl font-bold text-gray-800">{{ document.title }}</h2>
      <div class="flex-shrink-0 flex items-center gap-2">
        <button @click="saveChanges" class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors shadow">
            Save Changes
        </button>
        <button
            v-if="!isReport"
            @click="saveAndAddToProcessing"
            class="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors shadow">
          Add to Processing
        </button>
      </div>
    </div>

    <div class="bg-gray-100 p-3 rounded-md border space-y-3">
        <div class="flex items-center gap-2 flex-wrap">
            <span class="font-medium text-sm">Tags:</span>
            <span v-for="tag in localTags" :key="tag" class="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full flex items-center gap-2">
              {{ tag }}
              <button @click="removeTag(tag)" class="text-blue-500 hover:text-blue-800 font-bold">&times;</button>
            </span>
            <input v-if="!isReport" type="text" placeholder="+ Add tag" @keyup.enter="addTag" class="px-2 py-1 border rounded-md text-sm">
        </div>
        <div v-if="!isReport" class="flex items-center gap-2">
            <span class="font-medium text-sm">Color Code:</span>
            <button v-for="color in availableColors" :key="color"
                    @click="localColor = color"
                    :class="['h-6 w-6 rounded-full border-2 shadow', color === 'default' ? 'bg-white' : `bg-${color}-500`, localColor === color ? 'ring-2 ring-offset-1 ring-black' : 'border-white']">
            </button>
        </div>
    </div>

    <div
      class="prose max-w-none bg-white p-6 rounded-lg shadow-inner"
      v-html="documentHtml"
    ></div>
  </div>
  <div v-else class="text-center text-gray-500 mt-10">
    <p>No document selected.</p>
    <p class="text-sm">Click on an item from any list to view it here.</p>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue';
import { useDocumentStore } from '../../stores/documentStore';
import { useProcessingStore } from '../../stores/processingStore';
import { useNotificationStore } from '../../stores/notificationStore';
import { useProjectStore } from '../../stores/projectStore';
import { documentService } from '../../services/api';

const documentStore = useDocumentStore();
const processingStore = useProcessingStore();
const notificationStore = useNotificationStore();
const projectStore = useProjectStore();

const document = computed(() => documentStore.activeDocument);
const documentHtml = computed(() => documentStore.activeDocumentHtml);
const isReport = computed(() => document.value?.tags.some(tag => tag.name === 'report'));

const availableColors = ['blue', 'green', 'red', 'yellow', 'purple', 'default'];

const localTags = ref([]);
const localColor = ref('default');

watch(document, (newDoc) => {
    if (newDoc) {
        localTags.value = newDoc.tags.map(tag => tag.name);
        localColor.value = newDoc.color || 'default';
    } else {
        localTags.value = [];
        localColor.value = 'default';
    }
}, { immediate: true });

const addTag = (event) => {
  const newTag = event.target.value.trim();
  if (newTag && !localTags.value.includes(newTag)) {
    localTags.value.push(newTag);
    event.target.value = '';
  }
};

const removeTag = (tagToRemove) => {
    localTags.value = localTags.value.filter(tag => tag !== tagToRemove);
};

async function saveChanges() {
    const projectId = projectStore.activeProjectId;
    if (!document.value || !projectId || isReport.value) {
        notificationStore.addNotification({ message: 'Cannot save changes to a report or without an active project.', type: 'warning' });
        return;
    };
    try {
        const updates = {
            tags: localTags.value,
            color: localColor.value,
        };
        const updatedDoc = await documentService.updateDocument(projectId, document.value.id, updates);
        documentStore.upsertDocument(updatedDoc);
        notificationStore.addNotification({ message: 'Changes saved successfully!', type: 'success' });
    } catch (error) {
        // Error is handled by the api service
    }
}

async function saveAndAddToProcessing() {
    if (!document.value) return;
    await saveChanges();
    processingStore.addToQueue(document.value.id);
}
</script>
