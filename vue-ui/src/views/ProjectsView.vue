<template>
  <div class="min-h-screen bg-gray-50 p-4 sm:p-8">
    <header class="mb-10">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center">
        <Rocket class="h-8 w-8 text-blue-600 mr-3" />
        <h1 class="text-3xl font-bold text-gray-800">Research Workspace</h1>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <section class="mb-12">
        <div class="bg-white p-6 sm:p-8 rounded-xl shadow-lg border border-gray-200">
          <h2 class="text-xl font-semibold text-gray-700 mb-6 flex items-center">
            <PlusCircle class="h-6 w-6 text-blue-500 mr-2" />
            Create a New Research Project
          </h2>
          <form @submit.prevent="createProject" class="space-y-6">
            <div>
              <label for="projectName" class="block text-sm font-medium text-gray-600 mb-1">Project Name</label>
              <input type="text" id="projectName" v-model="newProject.name" required
                     class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 transition duration-150"
                     placeholder="e.g., AI in Healthcare">
            </div>
            <div>
              <label for="projectGoal" class="block text-sm font-medium text-gray-600 mb-1">Project Goal</label>
              <textarea id="projectGoal" v-model="newProject.goal" rows="3" required
                        class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 transition duration-150"
                        placeholder="e.g., Analyze the impact of AI on diagnostic accuracy"></textarea>
            </div>
            <div>
              <label for="projectDescription" class="block text-sm font-medium text-gray-600 mb-1">Project Description (Optional)</label>
              <textarea id="projectDescription" v-model="newProject.description" rows="3"
                        class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 transition duration-150"
                        placeholder="e.g., A comprehensive study focusing on..."></textarea>
            </div>
            <button type="submit"
                    class="w-full sm:w-auto flex items-center justify-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-150">
              <Plus class="h-5 w-5 mr-2" />
              CREATE PROJECT
            </button>
          </form>
        </div>
      </section>

      <section>
        <h2 class="text-2xl font-semibold text-gray-700 mb-8 flex items-center">
          <FolderKanban class="h-7 w-7 text-blue-600 mr-3" />
          My Projects
        </h2>
        <div v-if="projects.length === 0" class="text-center text-gray-500 py-10">
          <p class="text-lg">No projects yet. Create one above to get started!</p>
        </div>
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          <ProjectCard v-for="project in projects" :key="project.id" :project="project" />
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import ProjectCard from '../components/ProjectCard.vue';
import { PlusCircle, Plus, FolderKanban, Rocket } from 'lucide-vue-next';

const router = useRouter();

const newProject = ref({
  id: '',
  name: '',
  goal: '',
  description: '',
  sources: 0,
  date: ''
});

const projects = ref([
  { id: '1', name: 'United States Universal Service Fund Overview', goal: 'Understand USF', description: 'Deep dive into USF.', sources: 6, date: 'May 31, 2025', icon: 'BarChart3' },
  { id: '2', name: "USDA's ReConnect Program", goal: 'Analyze ReConnect', description: 'Expanding broadband access.', sources: 5, date: 'May 25, 2025', icon: 'Network' },
  { id: '3', name: 'Untitled notebook', goal: 'General notes', description: '', sources: 0, date: 'May 25, 2025', icon: 'FileText' },
  { id: '4', name: 'Indiana Advance Health Directives Guide', goal: 'Health directives', description: 'Guide for Indiana.', sources: 3, date: 'May 22, 2025', icon: 'FileHeart' },
]);

const createProject = () => {
  if (newProject.value.name && newProject.value.goal) {
    const createdProject = {
      ...newProject.value,
      id: String(Date.now()), // Simple ID generation
      sources: 0,
      date: new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }),
      icon: 'FilePlus' // Default icon for new projects
    };
    projects.value.unshift(createdProject); // Add to the beginning of the list

    router.push({
        name: 'ProjectSetupView',
        params: {
            projectId: createdProject.id,
            projectName: createdProject.name
        }
    });

    newProject.value = { name: '', goal: '', description: '' };
  }
};

// Removed navigateToSetup method as it's no longer directly triggered by ProjectCard from this view.
// ProjectCard now handles its own navigation.

</script>

<style scoped>
/* Scoped styles for ProjectsView if needed */
</style>
