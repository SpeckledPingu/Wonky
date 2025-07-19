<template>
  <div class="flex flex-col h-full">
    <!-- --- NEW: Project Selector --- -->
    <ProjectSelector />

    <!-- Header/Tabs for the Left Pane -->
    <div class="flex-shrink-0 border-b border-gray-200">
      <nav class="flex space-x-2 p-2 bg-gray-50">
        <button
          @click="activeTab = 'documentSearch'"
          :class="tabClass('documentSearch')"
        >
          Document Search
        </button>
        <button
          @click="activeTab = 'extractionSearch'"
          :class="tabClass('extractionSearch')"
        >
          Extraction Search
        </button>
      </nav>
    </div>

    <!-- Content Area for the Left Pane -->
    <div class="flex-grow overflow-y-auto custom-scrollbar">
      <keep-alive>
        <component :is="activeComponent" />
      </keep-alive>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import DocumentSearch from './search/DocumentSearch.vue';
import ExtractionSearch from './search/ExtractionSearch.vue';
import ProjectSelector from './common/ProjectSelector.vue'; // <-- IMPORTED

const activeTab = ref('documentSearch');

const components = {
  documentSearch: DocumentSearch,
  extractionSearch: ExtractionSearch,
};

const activeComponent = computed(() => components[activeTab.value]);

const tabClass = (tabName) => {
  return [
    'px-4 py-2 text-sm font-medium rounded-md transition-colors w-full text-center',
    activeTab.value === tabName
      ? 'bg-blue-500 text-white shadow'
      : 'text-gray-600 hover:bg-gray-200',
  ];
};
</script>
