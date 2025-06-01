<template>
  <div class="min-h-screen bg-gray-50 p-4 sm:p-8">
    <header class="mb-8">
      <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <button @click="goBack" class="flex items-center text-blue-600 hover:text-blue-800 transition-colors mb-4">
          <ArrowLeft class="h-5 w-5 mr-2" />
          Back to All Projects
        </button>
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center">
          <h1 class="text-2xl sm:text-3xl font-bold text-gray-800 mb-2 sm:mb-0">
            Setup Research for: <span class="text-blue-600">{{ projectName || 'Project Name' }}</span>
          </h1>
          <button @click="beginResearch"
                  class="flex items-center px-6 py-3 bg-green-500 text-white font-semibold rounded-lg shadow-md hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition duration-150">
            <Play class="h-5 w-5 mr-2" />
            BEGIN RESEARCH
          </button>
        </div>
      </div>
    </header>

    <main class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
      <section class="bg-white p-6 sm:p-8 rounded-xl shadow-lg border border-gray-200 mb-12">
        <h2 class="text-xl font-semibold text-gray-700 mb-6 flex items-center">
          <Lightbulb class="h-6 w-6 text-yellow-500 mr-2" />
          Define Research Streams
        </h2>
        <form @submit.prevent="addResearchStream" class="space-y-6">
          <div>
            <label for="subjectMatter" class="block text-sm font-medium text-gray-600 mb-1">Subject Matter</label>
            <input type="text" id="subjectMatter" v-model="newStream.subject" required
                   class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 transition duration-150"
                   placeholder="e.g., Universal Service Fund History">
          </div>
          <div>
            <label for="subjectMatterFocus" class="block text-sm font-medium text-gray-600 mb-1">Subject Matter Focus</label>
            <textarea id="subjectMatterFocus" v-model="newStream.focus" rows="3" required
                      class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 transition duration-150"
                      placeholder="e.g., Legislative milestones and key developments"></textarea>
          </div>
          <div>
            <label for="analysisType" class="block text-sm font-medium text-gray-600 mb-1">Analysis Type</label>
            <select id="analysisType" v-model="newStream.analysisType" required
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 transition duration-150">
              <option disabled value="">Select an analysis type</option>
              <option>Domestic Policy</option>
              <option>International Policy</option>
              <option>Impact Analysis</option>
              <option>Historical Review</option>
              <option>Technical Feasibility</option>
              <option>Market Research</option>
            </select>
          </div>
          <button type="submit"
                  class="w-full sm:w-auto flex items-center justify-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-150">
            <Plus class="h-5 w-5 mr-2" />
            ADD RESEARCH STREAM
          </button>
        </form>
      </section>

      <section>
        <h2 class="text-xl font-semibold text-gray-700 mb-6 flex items-center">
          <ListChecks class="h-6 w-6 text-green-600 mr-2" />
          Current Research Streams
        </h2>
        <div v-if="researchStreams.length === 0" class="text-center text-gray-500 py-10 bg-white rounded-lg shadow border">
          <p class="text-lg">No research streams defined yet. Add one above to begin.</p>
        </div>
        <div v-else class="space-y-4">
          <div v-for="(stream, index) in researchStreams" :key="stream.id"
               class="bg-white p-5 rounded-lg shadow-md border border-gray-200 hover:shadow-lg transition-shadow duration-150">
            <div class="flex justify-between items-start">
              <div>
                <h3 class="text-md font-semibold text-gray-800 mb-1">
                  {{ index + 1 }}. Subject: <span class="font-normal text-gray-700">{{ stream.subject }}</span>
                </h3>
                <p class="text-sm text-gray-600 mb-1">
                  Focus: <span class="font-normal">{{ stream.focus }}</span>
                </p>
                <p class="text-sm text-gray-600">
                  Analysis Type: <span class="font-normal">{{ stream.analysisType }}</span>
                </p>
              </div>
              <button @click="removeResearchStream(stream.id)"
                      class="text-red-500 hover:text-red-700 p-1 rounded-full hover:bg-red-100 transition-colors">
                <Trash2 class="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ArrowLeft, Play, Lightbulb, Plus, ListChecks, Trash2 } from 'lucide-vue-next';

const router = useRouter();
const route = useRoute();

const projectId = ref(route.params.projectId);
// This would typically be fetched based on projectId
const projectName = ref(route.params.projectName || `Project ${projectId.value}`);


const newStream = ref({
  subject: '',
  focus: '',
  analysisType: ''
});

const researchStreams = ref([]);

// Mock loading existing streams for a project
onMounted(() => {
  console.log('Project ID from route:', route.params.projectId);
  console.log('Project Name from route:', route.params.projectName);
  // In a real app, you would fetch this data based on projectId.value
  if (projectId.value === '1') { // Example: USF Project
    researchStreams.value = [
      { id: 'rs1', subject: 'USF History', focus: 'Legislative milestones', analysisType: 'Historical Review' },
      { id: 'rs2', subject: 'Rural Broadband Impact', focus: 'Case studies and statistics', analysisType: 'Impact Analysis' },
    ];
  } else {
     researchStreams.value = [
        { id: 'rs_sample1', subject: 'Subject Matter 1', focus: 'Subject Matter Focus 1', analysisType: 'Domestic Policy' },
        { id: 'rs_sample2', subject: 'Subject Matter 2', focus: 'Subject Matter Focus 2', analysisType: 'International Policy' },
        { id: 'rs_sample3', subject: 'Subject Matter 3', focus: 'Subject Matter Focus 3', analysisType: 'Impact Analysis' },
    ];
  }
});


const addResearchStream = () => {
  if (newStream.value.subject && newStream.value.focus && newStream.value.analysisType) {
    researchStreams.value.push({
      id: String(Date.now()), // Simple ID
      ...newStream.value
    });
    newStream.value = { subject: '', focus: '', analysisType: '' }; // Reset form
  }
};

const removeResearchStream = (streamId) => {
  researchStreams.value = researchStreams.value.filter(stream => stream.id !== streamId);
};

const goBack = () => {
  router.push({ name: 'ProjectsView' });
};

const beginResearch = () => {
  // Here you would typically save the researchStreams to your backend
  // associated with projectId.value
  console.log('Beginning research for project:', projectId.value, 'with streams:', researchStreams.value);
  router.push({ name: 'ResearchView', params: { projectId: projectId.value, projectName: projectName.value } });
};
</script>

<style scoped>
/* Scoped styles for ProjectSetupView if needed */
</style>
