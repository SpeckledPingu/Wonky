import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';
import { reportsService } from '../services/api';
import { useDocumentStore } from './documentStore';
import { useProjectStore } from './projectStore';

export const useReportsStore = defineStore('reports', () => {
    // State
    const reports = ref([]);
    const filterTerm = ref('');

    // Getters
    const filteredReports = computed(() => {
        if (!filterTerm.value) {
            return reports.value;
        }
        return reports.value.filter(report =>
            report.title.toLowerCase().includes(filterTerm.value.toLowerCase()) ||
            report.content.toLowerCase().includes(filterTerm.value.toLowerCase())
        );
    });

    // Actions
    async function fetchReports(projectId) {
        if (!projectId) {
            reports.value = [];
            return;
        }
        try {
            const documentStore = useDocumentStore();
            const fetchedReports = await reportsService.fetchReports(projectId);
            reports.value = fetchedReports.sort((a, b) => new Date(b.generated_at) - new Date(a.generated_at));

            reports.value.forEach(report => {
                documentStore.upsertDocument({
                    ...report,
                    tags: [{id: -1, name: 'report'}, {id: -2, name: report.analysis_type}],
                    color: 'purple',
                });
            });
        } catch (error) {
            // Handled by api service
        }
    }

    function setFilter(term) {
        filterTerm.value = term;
    }

    // --- NEW FUNCTION ---
    function clearState() {
        reports.value = [];
        filterTerm.value = '';
    }

    const projectStore = useProjectStore();
    watch(() => projectStore.activeProjectId, (newProjectId) => {
        if (newProjectId) {
            fetchReports(newProjectId);
        } else {
            clearState(); // Use the new clear function
        }
    }, { immediate: true });

    return {
        reports,
        filterTerm,
        filteredReports,
        fetchReports,
        setFilter,
        clearState, // Expose the new function
    };
});
