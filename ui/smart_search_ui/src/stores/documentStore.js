import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';
import { marked } from 'marked';
import { documentService } from '../services/api';
import { useNotificationStore } from './notificationStore';
import { useProjectStore } from './projectStore';

// --- FIX: Configure marked to treat single newlines as <br> tags ---
// This makes the rendering more flexible for different document formats.
marked.setOptions({
  breaks: true, // Still treat single newlines as <br>
  commonmark: true, // Use the CommonMark specification
  gfm: true, // Disable GitHub Flavored Markdown for stricter compliance
});

export const useDocumentStore = defineStore('documents', () => {
  // State
  const activeDocumentId = ref(null);
  const documentsCache = ref({});
  const isLoading = ref(false);

  // Getters
  const activeDocument = computed(() => {
    return activeDocumentId.value ? documentsCache.value[activeDocumentId.value] : null;
  });

  const activeDocumentHtml = computed(() => {
    if (activeDocument.value && activeDocument.value.content) {
      return marked(activeDocument.value.content);
    }
    return '';
  });

  // Actions
  function upsertDocument(docData) {
      if (!docData || !docData.id) return;
      documentsCache.value[docData.id] = docData;
  }

  async function viewDocument(projectId, docId) {
    if (!docId || !projectId) return;
    const notificationStore = useNotificationStore();
    isLoading.value = true;
    try {
        const freshDoc = await documentService.getDocumentById(projectId, docId);
        upsertDocument(freshDoc);
        activeDocumentId.value = docId;
    } catch (error) {
        notificationStore.addNotification({ message: `Could not load document ${docId}.`, type: 'error'});
        activeDocumentId.value = null;
    } finally {
        isLoading.value = false;
    }
  }

  function clearState() {
      activeDocumentId.value = null;
      documentsCache.value = {};
      isLoading.value = false;
  }

  const projectStore = useProjectStore();
  watch(() => projectStore.activeProjectId, () => {
      clearState(); // Clear document state when project changes
  });

  return {
    activeDocumentId,
    documentsCache,
    isLoading,
    activeDocument,
    activeDocumentHtml,
    viewDocument,
    upsertDocument,
    clearState,
  };
});
