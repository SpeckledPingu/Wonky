<template>
  <div class="min-h-screen bg-gray-50 p-4 sm:p-8">
    <header class="mb-10">
      <!-- ... header content ... -->
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- ... create project form ... -->
      <!-- Display creation error if any -->
      <div v-if="creationError" class="mt-4 p-4 bg-red-100 border border-red-300 text-red-800 rounded-lg">
        <p><strong>Error creating project:</strong> {{ creationError }}</p>
      </div>

      <section class="mt-12">
        <h2 class="text-2xl font-semibold text-gray-700 mb-8 flex items-center">
          <FolderKanban class="h-7 w-7 text-blue-600 mr-3" />
          My Projects
        </h2>
        <!-- Loading State -->
        <div v-if="isLoading" class="text-center text-gray-500 py-10">
          <p class="text-lg">Loading projects...</p>
        </div>
        <!-- Error State -->
        <div v-else-if="fetchError" class="text-center text-red-500 bg-red-100 p-4 rounded-lg">
          <p>{{ fetchError }}</p>
        </div>
        <!-- Empty State -->
        <div v-else-if="projects.length === 0" class="text-center text-gray-500 py-10">
          <p class="text-lg">No projects found. Create one above to get started!</p>
        </div>
        <!-- Content -->
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          <ProjectCard v-for="project in projects" :key="project.id" :project="project" />
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import ProjectCard from '../components/ProjectCard.vue';
import { PlusCircle, Plus, FolderKanban, Rocket } from 'lucide-vue-next';

const router = useRouter();
const API_BASE_URL = 'http://localhost:8000';

const newProject = ref({
  name: '',
  goal: '',
  description: '',
});

const projects = ref([]);
// Add reactive state for loading and errors
const isLoading = ref(true);
const fetchError = ref(null);
const creationError = ref(null);

const fetchProjects = async () => {
  isLoading.value = true;
  fetchError.value = null;
  try {
    const response = await fetch(`${API_BASE_URL}/api/projects`);
    if (!response.ok) {
      throw new Error(`The server responded with status: ${response.status}`);
    }
    projects.value = await response.json();
  } catch (error) {
    console.error("Failed to fetch projects:", error);
    fetchError.value = "Could not load projects. Please ensure the backend is running and try again.";
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchProjects();
});

const createProject = async () => {
  if (newProject.value.name && newProject.value.goal) {
    creationError.value = null; // Reset previous errors
    try {
      const response = await fetch(`${API_BASE_URL}/api/projects`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: newProject.value.name,
          goal: newProject.value.goal,
          description: newProject.value.description || null,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'An unknown error occurred.' }));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const createdProject = await response.json();

      router.push({
        name: 'ProjectSetupView',
        params: {
          projectId: createdProject.id,
          projectName: createdProject.name,
        },
      });

      newProject.value = { name: '', goal: '', description: '' };
      // No need to fetch projects here, as we are navigating away.
      // The list will be re-fetched when the user navigates back.

    } catch (error) {
      console.error("Error creating project:", error);
      creationError.value = error.message;
    }
  }
};
</script>

<style scoped>
/* Scoped styles for ProjectsView if needed */
</style>