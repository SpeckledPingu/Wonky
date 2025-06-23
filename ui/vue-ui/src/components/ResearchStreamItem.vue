<template>
  <div class="bg-gray-50 rounded-lg p-3 shadow-sm border border-gray-200">
    <div class="flex justify-between items-center cursor-pointer mb-2" @click="toggleExpandLocal">
      <h3 class="text-sm font-semibold text-gray-700 flex items-center">
        <ChevronRight class="h-4 w-4 mr-1 transition-transform duration-200" :class="{'rotate-90': isExpandedLocal}" />
        {{ stream.subject }}
      </h3>
      <input type="checkbox"
             :checked="allDocumentsSelected"
             @change="toggleSelectAll"
             @click.stop
             class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 cursor-pointer"
             title="Select/Deselect all in this stream" />
    </div>
    <div v-if="isExpandedLocal" class="pl-4 space-y-1 border-l-2 border-blue-200 ml-2">
      <div v-if="stream.documents && stream.documents.length > 0">
        <DocumentItem
          v-for="doc in stream.documents"
          :key="doc.id"
          :document="doc"
          :is-selected="localSelectedDocuments.includes(doc.id)"
          :is-highlighted="highlightedDocumentIds.includes(doc.id)" @click="emitDocumentClick(doc)"
          @toggle-select="toggleDocumentSelection(doc.id)"
        />
      </div>
      <p v-else class="text-xs text-gray-500 italic py-1">No documents in this stream.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits, computed, watch } from 'vue';
import DocumentItem from './DocumentItem.vue';
import { ChevronRight } from 'lucide-vue-next';

const props = defineProps({
  stream: {
    type: Object,
    required: true
  },
  isExpanded: Boolean,
  selectedDocuments: { // This is the v-model prop from the parent
    type: Array,
    default: () => []
  },
  highlightedDocumentIds: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['toggle-expand', 'document-click', 'update:selectedDocuments']);

const isExpandedLocal = ref(props.isExpanded);
const localSelectedDocuments = ref([...props.selectedDocuments]);

watch(() => props.isExpanded, (newVal) => {
  isExpandedLocal.value = newVal;
});

watch(() => props.selectedDocuments, (newVal) => {
  if (JSON.stringify(newVal) !== JSON.stringify(localSelectedDocuments.value)) {
    localSelectedDocuments.value = [...newVal];
  }
}, { deep: true });


const toggleExpandLocal = () => {
  isExpandedLocal.value = !isExpandedLocal.value;
  emit('toggle-expand', props.stream.id);
};

const emitDocumentClick = (doc) => {
  emit('document-click', doc);
};

const toggleDocumentSelection = (docId) => {
  const index = localSelectedDocuments.value.indexOf(docId);
  if (index > -1) {
    localSelectedDocuments.value.splice(index, 1);
  } else {
    localSelectedDocuments.value.push(docId);
  }
  emit('update:selectedDocuments', [...localSelectedDocuments.value]);
};

const allDocumentsSelected = computed(() => {
  if (!props.stream.documents || props.stream.documents.length === 0) {
    return false;
  }
  return props.stream.documents.every(doc => localSelectedDocuments.value.includes(doc.id));
});

const toggleSelectAll = (event) => {
    const shouldSelectAll = event.target.checked;
    const newSelection = shouldSelectAll ? props.stream.documents.map(doc => doc.id) : [];
    localSelectedDocuments.value = newSelection;
    emit('update:selectedDocuments', newSelection);
};

</script>

<style scoped>
.rotate-90 {
  transform: rotate(90deg);
}
</style>