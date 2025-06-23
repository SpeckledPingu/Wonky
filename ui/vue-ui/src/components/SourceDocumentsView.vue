<template>
  <div class="p-4 h-full flex flex-col bg-gray-50">
    <div class="flex justify-between items-center mb-3">
      <h3 class="text-base font-semibold text-gray-700">
        {{ currentHierarchyRootId ? 'Related Documents' : 'All Project Documents' }}
      </h3>
      <button v-if="currentHierarchyRootId" @click="resetView"
              class="text-xs text-blue-600 hover:text-blue-800 flex items-center">
        <ArrowLeft class="h-3 w-3 mr-1"/> View All Documents
      </button>
    </div>
    <div class="flex-1 overflow-y-auto space-y-2">
      <div v-if="isLoading" class="text-center text-gray-500 py-10">
        <p>Loading related documents...</p>
      </div>
      <div v-else>
        <!-- Hierarchical, categorized view -->
        <div v-if="currentHierarchyRootId && categorizedDocuments">
          <template v-if="categorizedDocuments.parents.length > 0">
            <h4 class="text-xs font-bold uppercase text-gray-400 tracking-wider mt-4 mb-1 px-2">Parents</h4>
            <DocumentItem v-for="doc in categorizedDocuments.parents" :key="doc.id" :document="doc" :is-highlighted="highlightedDocumentIds.includes(doc.id)" @click="emitDocumentClick(doc)" />
          </template>
          <template v-if="categorizedDocuments.selected.length > 0">
             <h4 class="text-xs font-bold uppercase text-gray-400 tracking-wider mt-4 mb-1 px-2">Selected Document</h4>
            <DocumentItem v-for="doc in categorizedDocuments.selected" :key="doc.id" :document="doc" :is-highlighted="highlightedDocumentIds.includes(doc.id)" @click="emitDocumentClick(doc)" />
          </template>
          <template v-if="categorizedDocuments.children.length > 0">
            <h4 class="text-xs font-bold uppercase text-gray-400 tracking-wider mt-4 mb-1 px-2">Child Documents</h4>
            <DocumentItem v-for="doc in categorizedDocuments.children" :key="doc.id" :document="doc" :is-highlighted="highlightedDocumentIds.includes(doc.id)" @click="emitDocumentClick(doc)" />
          </template>
          <template v-if="categorizedDocuments.linked.length > 0">
            <h4 class="text-xs font-bold uppercase text-gray-400 tracking-wider mt-4 mb-1 px-2">Linked Documents</h4>
            <DocumentItem v-for="doc in categorizedDocuments.linked" :key="doc.id" :document="doc" :is-highlighted="highlightedDocumentIds.includes(doc.id)" @click="emitDocumentClick(doc)" />
          </template>
        </div>
        <!-- Flat list view for "All Documents" -->
        <div v-else>
          <DocumentItem
            v-for="doc in displayedDocuments"
            :key="doc.id"
            :document="doc"
            :is-highlighted="highlightedDocumentIds.includes(doc.id)"
            @click="emitDocumentClick(doc)"
          />
        </div>
        <p v-if="!displayedDocuments || displayedDocuments.length === 0" class="text-center text-gray-500 py-10">
          <FileText class="h-10 w-10 mx-auto text-gray-400 mb-2"/>
          No documents available to display.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, computed, ref, watch } from 'vue';
import DocumentItem from './DocumentItem.vue';
import { FileText, ArrowLeft } from 'lucide-vue-next';

const props = defineProps({
  documents: { // This will be allProjectDocuments from ResearchView
    type: Array,
    required: true,
    default: () => []
  },
  highlightedDocumentIds: {
    type: Array,
    default: () => []
  },
  initialSelectedDocumentId: {
    type: String,
    default: null
  },
  projectId: { // New prop to get the project context
    type: String,
    required: true,
  }
});

const emit = defineEmits(['document-click']);

const API_BASE_URL = 'http://localhost:8000';
const currentHierarchyRootId = ref(props.initialSelectedDocumentId);
const displayedDocuments = ref([]);
const isLoading = ref(false);

// Watch for the initial ID from the parent to change
watch(() => props.initialSelectedDocumentId, (newId) => {
  currentHierarchyRootId.value = newId;
});

const fetchHierarchy = async (docId) => {
  if (!props.projectId || !docId) return;
  isLoading.value = true;
  try {
    const response = await fetch(`${API_BASE_URL}/api/projects/${props.projectId}/documents/${docId}/hierarchy`);
    if (!response.ok) throw new Error(`API error: ${response.status}`);
    displayedDocuments.value = await response.json();
  } catch (error) {
    console.error('Failed to fetch document hierarchy:', error);
    displayedDocuments.value = props.documents; // Fallback to all docs
  } finally {
    isLoading.value = false;
  }
};

// Main watcher that reacts to changes in the selected document
watch(currentHierarchyRootId, (newRootId) => {
  if (newRootId) {
    fetchHierarchy(newRootId);
  } else {
    // When resetting, show all documents passed via props
    displayedDocuments.value = props.documents;
  }
}, { immediate: true });

// Computed property to categorize documents for the hierarchical view
const categorizedDocuments = computed(() => {
  if (!currentHierarchyRootId.value || displayedDocuments.value.length === 0) {
    return null;
  }

  const rootDoc = displayedDocuments.value.find(d => d.id === currentHierarchyRootId.value);
  if (!rootDoc) return null;

  const parents = [];
  let current = rootDoc;
  // Re-create parent chain client-side from the flat list from API
  while (current && current.parentId) {
    const parent = displayedDocuments.value.find(d => d.id === current.parentId);
    if (parent) {
      parents.unshift(parent);
      current = parent;
    } else {
      break;
    }
  }

  const children = displayedDocuments.value.filter(d => d.parentId === currentHierarchyRootId.value);

  const linked = displayedDocuments.value.filter(d => {
    // Exclude self, parents, and children from the "linked" category
    if (d.id === currentHierarchyRootId.value) return false;
    if (parents.some(p => p.id === d.id)) return false;
    if (children.some(c => c.id === d.id)) return false;
    return true;
  });

  return {
    parents,
    selected: [rootDoc],
    children,
    linked
  };
});

const resetView = () => {
  currentHierarchyRootId.value = null;
};

const emitDocumentClick = (doc) => {
  // When a document is clicked, update the root of the hierarchy
  // and also emit to the parent (ResearchView) to open in MarkdownViewer.
  currentHierarchyRootId.value = doc.id;
  emit('document-click', doc);
};
</script>

<style scoped>
/* Add any specific styles for SourceDocumentsView here if needed */
</style>