//import { defineStore } from 'pinia';
//import { ref } from 'vue';
//
//export const useProjectStore = defineStore('project', () => {
//    // State
//    // In a real app, you'd fetch a list of projects for the user.
//    // For now, we'll hardcode them based on the seed data.
//    const availableProjects = ref([
//        { id: 101, name: 'AI Research Project' },
//        { id: 102, name: 'Climate Policy Analysis' },
//    ]);
//
//    // Default to the first project
//    const activeProjectId = ref(availableProjects.value[0]?.id || null);
//
//    // Actions
//    function setActiveProject(projectId) {
//        if (availableProjects.value.some(p => p.id === projectId)) {
//            activeProjectId.value = projectId;
//            // In a real app, you would now trigger a refresh of all project-specific data.
//            // For simplicity, we will handle this in the components for now.
//            window.location.reload(); // Simple way to force a full data refresh
//        }
//    }
//
//    return {
//        availableProjects,
//        activeProjectId,
//        setActiveProject,
//    };
//});


import { defineStore } from 'pinia';
import { ref } from 'vue';
import { projectService } from '../services/api';

export const useProjectStore = defineStore('project', () => {
    // State
    const availableProjects = ref([]);
    const activeProjectId = ref(null);
    const isLoading = ref(false);

    // Actions
    async function fetchProjects() {
        isLoading.value = true;
        try {
            const projects = await projectService.getProjects();
            availableProjects.value = projects;
            // If there's no active project or the old one is gone, default to the first one
            if (!activeProjectId.value || !projects.some(p => p.id === activeProjectId.value)) {
                activeProjectId.value = projects[0]?.id || null;
            }
        } catch (error) {
            console.error("Failed to fetch projects:", error);
            availableProjects.value = [];
            activeProjectId.value = null;
        } finally {
            isLoading.value = false;
        }
    }

    function setActiveProject(projectId) {
        if (availableProjects.value.some(p => p.id === projectId)) {
            activeProjectId.value = projectId;
            // A full reload is a simple way to ensure all data stores refresh
            // with the new project context.
            window.location.reload();
        }
    }

    // Initial fetch when the store is created
    fetchProjects();

    return {
        availableProjects,
        activeProjectId,
        isLoading,
        fetchProjects,
        setActiveProject,
    };
});
