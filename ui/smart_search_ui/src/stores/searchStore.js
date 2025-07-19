import { defineStore } from 'pinia';
import { ref, watch } from 'vue';
import { searchService } from '../services/api';
import { useNotificationStore } from './notificationStore';
import { useProjectStore } from './projectStore';

export const useSearchStore = defineStore('search', () => {
    // State
    const guidingPrompt = ref('');
    const currentSearchId = ref(null);
    const summaryItems = ref([]);
    const isPolling = ref(false);
    let pollInterval = null;

    // Actions
    function setGuidingPrompt(prompt) {
        guidingPrompt.value = prompt;
    }

    function clearSearchState() {
        guidingPrompt.value = '';
        currentSearchId.value = null;
        summaryItems.value = [];
        isPolling.value = false;
        if (pollInterval) {
            clearInterval(pollInterval);
            pollInterval = null;
        }
    }

    async function startSummaryPolling(searchId) {
        const notificationStore = useNotificationStore();
        if (!searchId) return;

        // Clear previous polling state before starting a new one
        if (pollInterval) {
            clearInterval(pollInterval);
        }

        currentSearchId.value = searchId;
        summaryItems.value = []; // Clear previous summaries
        isPolling.value = true;

        let attempts = 0;
        const maxAttempts = 20; // Poll for a maximum of 30 seconds (20 * 1.5s)

        pollInterval = setInterval(async () => {
            if (attempts >= maxAttempts) {
                clearInterval(pollInterval);
                isPolling.value = false;
                notificationStore.addNotification({ message: 'Summary generation timed out.', type: 'warning' });
                return;
            }

            try {
                const update = await searchService.getSummaryUpdate(searchId);

                // --- FIX ---
                // The backend sends a nested object: { status: '...', summary: { docId: '...', summary: '...' } }
                // We need to check for the nested 'summary' object and its properties.
                if (update && update.summary && update.summary.docId) {
                    const newSummaryItem = update.summary;
                    // Add new summary item if it's not already there
                    if (!summaryItems.value.some(item => item.docId === newSummaryItem.docId)) {
                        // Push the actual summary item, not the whole response object.
                        summaryItems.value.push(newSummaryItem);
                    }
                } else if (update && update.status === 'complete') {
                    // Stop polling if the backend signals completion
                    clearInterval(pollInterval);
                    isPolling.value = false;
                    notificationStore.addNotification({ message: 'Guided summary complete.', type: 'success' });
                }
            } catch (error) {
                // API service will handle notification
                clearInterval(pollInterval);
                isPolling.value = false;
            }
            attempts++;
        }, 1500); // Poll every 1.5 seconds
    }
    const projectStore = useProjectStore();
        watch(() => projectStore.activeProjectId, () => {
            clearSearchState();
        });

    return {
        guidingPrompt,
        currentSearchId,
        summaryItems,
        isPolling,
        setGuidingPrompt,
        clearSearchState,
        startSummaryPolling,
    };
});
