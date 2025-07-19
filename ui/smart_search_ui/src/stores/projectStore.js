import { defineStore } from 'pinia';
import { ref, watch } from 'vue';
import { projectService } from '../services/api';
import { useAuthStore } from './authStore';
import { useNotificationStore } from './notificationStore';

export const useProjectStore = defineStore('project', () => {
    // State
    const availableProjects = ref([]);
    const activeProjectId = ref(null);
    const isLoading = ref(false);

    // Actions
    async function fetchProjects() {
        const authStore = useAuthStore();
        if (!authStore.isAuthenticated) return;

        isLoading.value = true;
        try {
            const projects = await projectService.getProjects();
            availableProjects.value = projects;
        } catch (error) {
            console.error("Failed to fetch projects:", error);
        } finally {
            isLoading.value = false;
        }
    }

    // --- NEW FUNCTION ---
    async function createProject(projectData) {
        const notificationStore = useNotificationStore();
        try {
            const newProject = await projectService.createProject(projectData);
            // Refresh the project list to include the new one
            await fetchProjects();
            notificationStore.addNotification({ message: `Project "${newProject.name}" created!`, type: 'success' });
            return true;
        } catch (error) {
            return false;
        }
    }

    function setActiveProject(projectId) {
        if (availableProjects.value.some(p => p.id === projectId)) {
            activeProjectId.value = projectId;
        }
    }

    function clearProjectState() {
        availableProjects.value = [];
        activeProjectId.value = null;
    }

    const authStore = useAuthStore();
    watch(() => authStore.isAuthenticated, (isAuth) => {
        if (isAuth) {
            fetchProjects();
        } else {
            clearProjectState();
        }
    }, { immediate: true });

    return {
        availableProjects,
        activeProjectId,
        isLoading,
        fetchProjects,
        createProject, // Expose the new function
        setActiveProject,
        clearProjectState,
    };
});
