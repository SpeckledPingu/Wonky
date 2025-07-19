import { defineStore } from 'pinia';
import { ref, watch } from 'vue';
import { useProjectStore } from './projectStore';
import { useDocumentStore } from './documentStore';
import { savedResultsService } from '../services/api';
import { useNotificationStore } from './notificationStore';
import { useAuthStore } from './authStore';

export const useSavedResultsStore = defineStore('savedResults', () => {
    // State
    const savedResults = ref([]);

    // Actions
    async function fetchSavedResults(projectId) {
        const authStore = useAuthStore();
        if (!authStore.isAuthenticated) return;

        if (!projectId) {
            savedResults.value = [];
            return;
        }
        try {

            const results = await savedResultsService.getSavedResults(projectId);
            console.log(results)
            savedResults.value = results;
            // Also add them to the central document cache
            const documentStore = useDocumentStore();
            results.forEach(doc => documentStore.upsertDocument(doc));
        } catch (error) {
            // Handled by api service
        }
    }

//    async function fetchProjects() {
//        const authStore = useAuthStore();
//        if (!authStore.isAuthenticated) return;
//
//        isLoading.value = true;
//        try {
//            const projects = await projectService.getProjects();
//            availableProjects.value = projects;
//        } catch (error) {
//            console.error("Failed to fetch projects:", error);
//        } finally {
//            isLoading.value = false;
//        }
//    }

    async function saveResult(projectId, docId) {
        const notificationStore = useNotificationStore();
        try {
            await savedResultsService.saveResult(projectId, docId);
            // Refresh the list to show the newly saved item
            await fetchSavedResults(projectId);
            notificationStore.addNotification({ message: 'Result saved successfully!', type: 'success' });
        } catch (error) {
            // Handled by api service
        }
    }

    async function removeResult(projectId, docId) {
        const notificationStore = useNotificationStore();
        try {
            await savedResultsService.removeResult(projectId, docId);
            // Remove the item from the local list for immediate UI feedback
            savedResults.value = savedResults.value.filter(doc => doc.id !== docId);
            notificationStore.addNotification({ message: 'Result removed.', type: 'info' });
        } catch (error) {
            // Handled by api service
        }
    }

    function clearState() {
        savedResults.value = [];
    }
//
//    const projectStore = useProjectStore();
//    watch(() => projectStore.activeProjectId, (newProjectId) => {
//        if (newProjectId) {
//            fetchSavedResults(newProjectId);
//        } else {
//            clearState();
//        }
//    }, { immediate: true });

    const projectStore = useProjectStore();
    const authStore = useAuthStore();
    watch(() => authStore.isAuthenticated, (isAuth) => {
        if (isAuth) {

            fetchSavedResults(projectStore.activeProjectId);
        } else {
            clearState();
        }
    }, { immediate: true });

    return { savedResults, fetchSavedResults, saveResult, removeResult, clearState };
});
