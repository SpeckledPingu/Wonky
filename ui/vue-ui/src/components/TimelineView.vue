<template>
  <div class="p-4 h-full flex flex-col bg-gray-50 overflow-y-auto">
    <h3 class="text-base font-semibold text-gray-700 mb-4 sticky top-0 bg-gray-50 py-2 z-10">Project Timeline (Vertical)</h3>
    <div v-if="!sortedDocuments || sortedDocuments.length === 0" class="text-center text-gray-500 py-10 flex flex-col items-center justify-center h-full">
      <Clock class="h-12 w-12 text-gray-400 mb-3"/>
      <p class="text-sm">No documents with date information to display on the timeline.</p>
    </div>
    <div v-else class="relative pl-6 pr-4 pb-4">
      <div class="absolute top-0 bottom-0 left-3 w-0.5 bg-indigo-200"></div>

      <div class="space-y-8">
        <div v-for="(doc, index) in sortedDocuments" :key="doc.id" class="relative timeline-item">
          <div
            class="absolute -left-[22px] top-1.5 w-4 h-4 rounded-full border-2 border-white"
            :class="[highlightedDocumentIds.includes(doc.id) ? 'bg-yellow-400 ring-2 ring-yellow-300' : 'bg-indigo-500']"
          ></div>

          <div
            @click="emitDocumentClick(doc)"
            class="ml-4 p-3 rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer border"
            :class="[
              highlightedDocumentIds.includes(doc.id) ? 'bg-yellow-50 border-yellow-300' : 'bg-white border-gray-200',
              doc.type === 'pdf' ? 'border-l-4 border-l-red-400' :
              doc.type === 'docx' ? 'border-l-4 border-l-blue-400' :
              doc.type === 'md' ? 'border-l-4 border-l-green-400' : 'border-l-4 border-l-gray-400'
            ]"
          >
            <div class="flex justify-between items-start mb-1">
              <h4
                class="text-sm font-semibold"
                :class="highlightedDocumentIds.includes(doc.id) ? 'text-yellow-700' : 'text-indigo-700'"
              >
                {{ doc.name }}
              </h4>
              <span
                class="text-xs px-2 py-0.5 rounded-full"
                :class="highlightedDocumentIds.includes(doc.id) ? 'bg-yellow-200 text-yellow-800' : 'bg-gray-100 text-gray-600'"
              >
                {{ formatDate(doc.publicationDate) }}
              </span>
            </div>
            <p class="text-xs text-gray-500 mb-1">Stream: {{ doc.streamName }}</p>
            <div v-if="doc.subjects && doc.subjects.length" class="mt-1">
                <span v-for="subject in doc.subjects.slice(0,3)" :key="subject"
                    class="inline-block bg-indigo-100 text-indigo-700 text-xs px-1.5 py-0.5 rounded-full mr-1 mb-1">
                    {{ subject }}
                </span>
                <span v-if="doc.subjects.length > 3" class="text-xs text-indigo-500 italic ml-1">
                    +{{ doc.subjects.length - 3 }} more
                </span>
            </div>
             <p v-if="doc.keyPlayers && doc.keyPlayers.length" class="text-xs text-gray-500 mt-1">
                Key Players: {{ doc.keyPlayers.join(', ') }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, defineProps, defineEmits } from 'vue';
import { Clock } from 'lucide-vue-next';

const props = defineProps({
  documents: {
    type: Array,
    required: true,
    default: () => []
  },
  highlightedDocumentIds: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['document-click']);

const sortedDocuments = computed(() => {
  return [...props.documents]
    .filter(doc => doc.publicationDate)
    .sort((a, b) => new Date(a.publicationDate) - new Date(b.publicationDate));
});

const emitDocumentClick = (doc) => {
  emit('document-click', doc);
};

const formatDate = (dateString) => {
  if (!dateString) return 'No Date';
  const options = { year: 'numeric', month: 'short', day: 'numeric' };
  try {
    return new Date(dateString).toLocaleDateString(undefined, options);
  } catch (e) {
    return dateString; // Fallback if date is invalid
  }
};
</script>

<style scoped>
/* Ensure the container scrolls, not the whole page if content is too long */
.h-full.flex.flex-col.bg-gray-50.overflow-y-auto {
  max-height: calc(100vh - 8rem); /* Adjust based on header and other fixed heights */
}

.timeline-item:last-child .absolute.top-0.bottom-0.left-3 {
  /* Optionally hide the line after the last item's dot if desired,
     but typically it extends to the bottom of the container.
     This might need JS to calculate height if you want it to stop exactly at the last dot.
     For simplicity, the line currently extends fully.
  */
}
</style>
