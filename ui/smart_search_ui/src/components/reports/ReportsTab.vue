<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-800">Generated Reports</h2>
      <div class="flex items-center gap-4">
        <input
            type="text"
            :value="reportsStore.filterTerm"
            @input="reportsStore.setFilter($event.target.value)"
            placeholder="Filter reports..."
            class="px-3 py-2 border border-gray-300 rounded-md shadow-sm w-64"
        />
        <button @click="reportsStore.fetchReports(projectStore.activeProjectId)" class="px-4 py-2 text-sm bg-white border rounded-md hover:bg-gray-100 flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h5M20 20v-5h-5M4 4l16 16" />
          </svg>
          Refresh
        </button>
      </div>
    </div>

    <div v-if="reportsStore.filteredReports.length > 0" class="space-y-4">
      <div
        v-for="report in reportsStore.filteredReports"
        :key="report.id"
        class="bg-white p-4 rounded-lg shadow-sm border border-transparent hover:border-indigo-500 cursor-pointer"
        @click="viewReport(report)"
      >
        <h3 class="font-bold text-indigo-700 text-lg">{{ report.title }}</h3>
        <p class="text-xs text-gray-500 mt-1">
          Generated on: {{ new Date(report.generated_at).toLocaleString() }}
        </p>
        <p class="text-sm text-gray-600 mt-2 truncate">
          {{ report.content.split('\n')[2] || report.content }}...
        </p>
      </div>
    </div>
    <div v-else class="text-center py-16 px-4 bg-gray-50 rounded-lg">
      <h3 class="text-lg font-medium text-gray-800">No reports found for this project.</h3>
    </div>
  </div>
</template>

<script setup>
import { useReportsStore } from '../../stores/reportsStore';
import { useDocumentStore } from '../../stores/documentStore';
import { useProjectStore } from '../../stores/projectStore';

const reportsStore = useReportsStore();
const documentStore = useDocumentStore();
const projectStore = useProjectStore();

const viewReport = (report) => {
  documentStore.viewDocument(projectStore.activeProjectId, report.id);
};
</script>
