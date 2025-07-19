<template>
  <div
    @click="viewDocument"
    :class="[
      'p-4 rounded-lg shadow-md border-l-4 transition-all duration-200 cursor-pointer',
      borderColorClass,
      { 'ring-2 ring-offset-2 ring-indigo-500': isSelected }
    ]"
  >
    <div class="flex justify-between items-start">
      <!-- Content -->
      <div class="flex-grow mr-4">
        <h4
          class="font-bold text-lg text-gray-800 hover:text-indigo-600"
        >
          {{ document.title }}
        </h4>
        <p class="text-sm text-gray-600 mt-1 truncate">
          {{ (document.content || '').substring(0, 100) }}...
        </p>
        <div class="mt-3 flex items-center gap-2 flex-wrap">
          <span
            v-for="tag in document.tags"
            :key="tag.id"
            class="px-2 py-0-5 bg-gray-200 text-gray-700 text-xs font-medium rounded-full"
          >
            {{ tag.name }}
          </span>
        </div>
      </div>
      <!-- Controls -->
      <div class="flex-shrink-0 flex flex-col items-end space-y-2">
        <!-- --- FIX: Added @click.stop to explicitly stop the click event --- -->
        <input
          type="checkbox"
          :checked="isSelected"
          @change.stop="$emit('selection-changed', document.id)"
          @click.stop
          class="h-5 w-5 rounded text-indigo-600 focus:ring-indigo-500 border-gray-300"
        />
        <button
          @click.stop="processingStore.removeItemsFromQueue([document.id])"
          class="text-gray-400 hover:text-red-500 transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm4 0a1 1 0 012 0v6a1 1 0 11-2 0V8z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, defineProps, defineEmits } from 'vue';
import { useDocumentStore } from '../../stores/documentStore';
import { useProcessingStore } from '../../stores/processingStore';
import { useProjectStore } from '../../stores/projectStore';

const props = defineProps({
  document: {
    type: Object,
    required: true,
  },
  isSelected: {
    type: Boolean,
    default: false,
  },
});

defineEmits(['selection-changed']);
const documentStore = useDocumentStore();
const processingStore = useProcessingStore();
const projectStore = useProjectStore();

const viewDocument = () => {
  documentStore.viewDocument(projectStore.activeProjectId, props.document.id);
};

const colorMap = {
  blue: 'border-blue-500 bg-blue-50',
  green: 'border-green-500 bg-green-50',
  red: 'border-red-500 bg-red-50',
  yellow: 'border-yellow-500 bg-yellow-50',
  purple: 'border-purple-500 bg-purple-50',
  default: 'border-gray-300 bg-white',
};

const borderColorClass = computed(() => {
  return colorMap[props.document.color] || colorMap.default;
});
</script>
