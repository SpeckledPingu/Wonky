<template>
  <div class="min-h-screen bg-gray-50 p-4 sm:p-8">
    <header class="mb-10">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between">
        <div class="flex items-center">
          <button @click="goBackToProjects" class="flex items-center text-sm text-blue-600 hover:text-blue-800 mr-4">
            <ArrowLeft class="h-4 w-4 mr-1" />
            Back to Projects
          </button>
          <h1 class="text-3xl font-bold text-gray-800 truncate" :title="projectName">
            Setup: {{ projectName }}
          </h1>
          <!-- NEW BUTTON: Open Entire Project -->
          <button @click="navigateToFullProjectResearch"
                  class="ml-4 px-4 py-2 bg-blue-500 text-white font-semibold rounded-lg shadow-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-150 flex items-center text-sm">
            <FolderOpen class="h-4 w-4 mr-2" />
            Open Entire Project
          </button>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Section for adding new research stream -->
      <section class="mb-12">
        <div class="bg-white p-6 sm:p-8 rounded-xl shadow-lg border border-gray-200">
          <h2 class="text-xl font-semibold text-gray-700 mb-6 flex items-center">
            <PlusCircle class="h-6 w-6 text-blue-500 mr-2" />
            Add New Research Stream
          </h2>

          <form @submit.prevent="createResearchStream" class="space-y-4">
            <div>
              <label for="streamSubject" class="block text-sm font-medium text-gray-600 mb-1">Subject</label>
              <input type="text" id="streamSubject" v-model="newStream.subject" required
                     class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 transition duration-150"
                     placeholder="e.g., Telecommunications Act of 1996">
            </div>
            <div>
              <label for="streamFocus" class="block text-sm font-medium text-gray-600 mb-1">Focus</label>
              <input type="text" id="streamFocus" v-model="newStream.focus" required
                     class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 transition duration-150"
                     placeholder="e.g., Key provisions and amendments">
            </div>
            <div>
              <label for="streamAnalysisType" class="block text-sm font-medium text-gray-600 mb-1">Analysis Type</label>
              <input type="text" id="streamAnalysisType" v-model="newStream.analysisType" required
                     class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 transition duration-150"
                     placeholder="e.g., Legal Review, Historical Analysis">
            </div>
            <button type="submit"
                    class="w-full sm:w-auto flex items-center justify-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-150">
              <Plus class="h-5 w-5 mr-2" />
              ADD STREAM
            </button>
          </form>
        </div>
      </section>

      <!-- Section for existing research streams -->
      <section>
        <h2 class="text-2xl font-semibold text-gray-700 mb-8 flex items-center">
          <ListTree class="h-7 w-7 text-blue-600 mr-3" />
          Existing Research Streams
        </h2>
        <div v-if="researchStreams.length === 0" class="text-center text-gray-500 py-10">
          <p class="text-lg">No research streams defined for this project yet. Add one above!</p>
        </div>
        <div v-else class="space-y-4">
          <div v-for="stream in researchStreams" :key="stream.id"
               class="bg-white p-4 rounded-lg shadow-sm border border-gray-200 flex justify-between items-center">
            <!-- Stream Info -->
            <div>
              <h3 class="text-base font-semibold text-gray-800">{{ stream.subject }}</h3>
              <p class="text-sm text-gray-600">Focus: {{ stream.focus }}</p>
              <p class="text-xs text-gray-500">Type: {{ stream.analysisType }}</p>
              <p class="text-xs text-gray-500">{{ stream.documents.length }} document{{ stream.documents.length !== 1 ? 's' : '' }}</p>
            </div>
            <!-- Action Buttons -->
            <div class="flex items-center space-x-2 flex-shrink-0">
              <button @click="navigateToResearch(stream.id)"
                      :class="[
                          'flex items-center px-3 py-1.5 text-xs font-medium rounded-md shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2',
                          stream.documents.length > 0
                              ? 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500'
                              : 'bg-green-500 text-white hover:bg-green-600 focus:ring-green-500'
                      ]">
                  <component :is="stream.documents.length > 0 ? 'FolderOpen' : 'Rocket'" class="h-4 w-4 mr-1.5" />
                  <span>{{ stream.documents.length > 0 ? 'Open Stream' : 'Research Stream' }}</span>
              </button>
              <button @click="deleteResearchStream(stream.id)"
                      class="p-2 text-red-500 hover:text-red-700 rounded-full hover:bg-red-50 transition-colors"
                      title="Delete Stream">
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
import { ref, onMounted, defineProps } from 'vue';
import { useRouter } from 'vue-router';
import { ArrowLeft, PlusCircle, Plus, ListTree, Trash2, Rocket, FolderOpen } from 'lucide-vue-next';

// Define props received from the router
const props = defineProps({
  projectId: {
    type: String,
    required: true
  },
  projectName: {
    type: String,
    required: true
  }
});

const router = useRouter();

// Base URL for your FastAPI backend
const API_BASE_URL = 'http://localhost:8000';

// Reactive state for research streams and the new stream form
const researchStreams = ref([]);
const newStream = ref({
  subject: '',
  focus: '',
  analysisType: ''
});

/**
 * Fetches all research streams for the current project from the backend.
 */
const fetchResearchStreams = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/projects/${props.projectId}/streams`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    researchStreams.value = await response.json();
  } catch (error) {
    console.error("Failed to fetch research streams:", error);
    alert("Could not load research streams. Please ensure the backend is running and accessible.");
  }
};

/**
 * Creates a new research stream by sending a POST request to the backend.
 */
const createResearchStream = async () => {
  if (newStream.value.subject && newStream.value.focus && newStream.value.analysisType) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/projects/${props.projectId}/streams`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newStream.value),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      newStream.value = { subject: '', focus: '', analysisType: '' };
      await fetchResearchStreams();
      alert('Research stream created successfully!');

    } catch (error) {
      console.error("Error creating research stream:", error);
      alert("There was an error creating the research stream. Please try again.");
    }
  } else {
    alert("Please fill in all fields for the new research stream.");
  }
};

/**
 * Deletes a research stream by sending a DELETE request to the backend.
 * @param {string} streamId - The ID of the stream to delete.
 */
const deleteResearchStream = async (streamId) => {
  if (confirm('Are you sure you want to delete this research stream? This action cannot be undone.')) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/projects/${props.projectId}/streams/${streamId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        if (response.status === 404) {
            alert("Research stream not found or already deleted.");
        } else {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
      }

      await fetchResearchStreams();
      alert('Research stream deleted successfully!');

    } catch (error) {
      console.error("Error deleting research stream:", error);
      alert("There was an error deleting the research stream. Please try again.");
    }
  }
};

/**
 * Navigates the user back to the main ProjectsView.
 */
const goBackToProjects = () => {
  router.push({ name: 'ProjectsView' });
};

/**
 * Navigates the user to the main ResearchView for this project,
 * optionally focusing on a specific stream.
 * @param {string} streamId - The ID of the stream to focus on.
 */
const navigateToResearch = (streamId) => {
  router.push({
    name: 'ResearchView',
    params: {
      projectId: props.projectId,
      projectName: props.projectName,
    },
    // Pass the streamId as a query parameter to give context to the ResearchView
    query: {
      focusStream: streamId
    }
  });
};

/**
 * Navigates the user to the main ResearchView for this project,
 * displaying all research streams.
 */
const navigateToFullProjectResearch = () => {
  router.push({
    name: 'ResearchView',
    params: {
      projectId: props.projectId,
      projectName: props.projectName,
    },
    // No query parameter for focusStream, so ResearchView will display all streams
  });
};

// Lifecycle hook: Fetch streams when the component is mounted
onMounted(() => {
  if (props.projectId) {
    fetchResearchStreams();
  } else {
    console.error("Project ID is missing. Cannot fetch research streams.");
    alert("Error: Project ID is missing. Returning to projects list.");
    router.push({ name: 'ProjectsView' });
  }
});
</script>

<style scoped>
</style>