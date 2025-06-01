<template>
  <div class="bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 overflow-hidden border border-gray-200 flex flex-col justify-between cursor-pointer"
       @click="navigateToResearch"> <div class="p-6">
      <div class="flex justify-between items-start mb-4">
        <div class="p-3 bg-blue-100 rounded-lg">
          <component :is="project.icon || 'FileText'" class="h-8 w-8 text-blue-600" />
        </div>
        <button @click.stop="showOptions" class="text-gray-400 hover:text-gray-600 p-1">
          <MoreVertical class="h-5 w-5" />
        </button>
      </div>
      <h3 class="text-lg font-semibold text-gray-800 mb-2 truncate" :title="project.name">{{ project.name }}</h3>
      <p class="text-xs text-gray-500 mb-1">{{ project.date }}</p>
      <p class="text-xs text-gray-500">{{ project.sources }} source{{ project.sources !== 1 ? 's' : '' }}</p>
    </div>
    <div class="bg-gray-50 px-6 py-3 border-t border-gray-200">
       <a @click.stop="navigateToStreams" class="text-sm text-blue-600 font-medium hover:underline cursor-pointer">
         View Streams
       </a>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue';
import { useRouter } from 'vue-router';
import { MoreVertical, FileText, BarChart3, Network, FileHeart, FilePlus } from 'lucide-vue-next';

const props = defineProps({
  project: {
    type: Object,
    required: true
  }
});

const router = useRouter();

const navigateToResearch = () => {
  router.push({
    name: 'ResearchView',
    params: {
      projectId: props.project.id,
      projectName: props.project.name
    }
  });
};

const navigateToStreams = () => {
  router.push({
    name: 'ProjectSetupView',
    params: {
      projectId: props.project.id,
      projectName: props.project.name
    }
  });
};

const showOptions = () => {
  // Placeholder for options like edit, delete
  console.log('Show options for project:', props.project.name);
  alert(`Options for ${props.project.name}`);
};

// Making icons available in the template
const icons = { FileText, BarChart3, Network, FileHeart, FilePlus };
</script>

<style scoped>
.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
