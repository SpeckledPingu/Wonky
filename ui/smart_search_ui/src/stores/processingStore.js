import { defineStore } from 'pinia';
import { ref, watch } from 'vue';
import { useDocumentStore } from './documentStore';
import { useNotificationStore } from './notificationStore';
import { useProjectStore } from './projectStore';
import { processingService, documentService } from '../services/api';

export const useProcessingStore = defineStore('processing', () => {
    // State
    const processingQueue = ref([]);

    // Actions
    async function fetchBucket(projectId) {
        if (!projectId) {
            processingQueue.value = [];
            return;
        }
        const documentStore = useDocumentStore();
        try {
            const docIds = await processingService.getBucket(projectId);
            processingQueue.value = docIds;

            for (const docId of docIds) {
                const doc = await documentService.getDocumentById(projectId, docId);
                documentStore.upsertDocument(doc);
            }

        } catch (error) {
            // Handled by api service
        }
    }

    async function addToQueue(docId) {
        const projectStore = useProjectStore();
        const documentStore = useDocumentStore();
        const notificationStore = useNotificationStore();
        const projectId = projectStore.activeProjectId;

        if (!projectId || !docId) return;

        if (processingQueue.value.includes(docId)) {
            notificationStore.addNotification({ message: `Document is already in the queue.`, type: 'info' });
            return;
        }

        try {
            await processingService.addToBucket(projectId, docId);
            const freshDoc = await documentService.getDocumentById(projectId, docId);
            documentStore.upsertDocument(freshDoc);
            processingQueue.value.push(docId);
            notificationStore.addNotification({ message: `"${freshDoc.title}" added to queue.`, type: 'success' });
        } catch (error) {
            // Handled by api service
        }
    }

    async function removeItemsFromQueue(docIds) {
        const projectStore = useProjectStore();
        const notificationStore = useNotificationStore();
        const projectId = projectStore.activeProjectId;

        if (!projectId || !docIds || !docIds.length) return;

        try {
            const response = await processingService.removeFromBucket(projectId, docIds);
            const idsToRemove = new Set(docIds);
            processingQueue.value = processingQueue.value.filter(id => !idsToRemove.has(id));
            notificationStore.addNotification({ message: response.message, type: 'success' });
        } catch(error) {
            // Handled by api service
        }
    }

    // --- NEW FUNCTION ---
    function clearState() {
        processingQueue.value = [];
    }

    const projectStore = useProjectStore();
    watch(() => projectStore.activeProjectId, (newProjectId) => {
        if (newProjectId) {
            fetchBucket(newProjectId);
        } else {
            clearState(); // Use the new clear function
        }
    }, { immediate: true });

    return {
        processingQueue,
        fetchBucket,
        addToQueue,
        removeItemsFromQueue,
        clearState, // Expose the new function
    };
});
