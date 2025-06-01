<template>
  <div class="flex flex-col h-full bg-white border-r border-gray-200 shadow-lg z-20">
    <header class="p-4 border-b border-gray-200 flex justify-between items-center bg-gray-50">
      <h3 class="text-md font-semibold text-gray-700 truncate" :title="document.name">
        <component :is="iconComponent" class="h-5 w-5 inline-block mr-2 text-gray-600" />
        {{ document.name }}
      </h3>
      <button @click="closeViewer" class="text-gray-500 hover:text-gray-700 p-1 rounded-full hover:bg-gray-200">
        <X class="h-5 w-5" />
      </button>
    </header>
    <div class="flex-1 p-5 overflow-y-auto prose prose-sm max-w-none">
      <pre class="whitespace-pre-wrap break-words text-xs">{{ document.content }}</pre>
      <!--
        Example with a library (install `marked` first: npm install marked):
        <div v-html="renderedMarkdown"></div>
      -->
    </div>
    <footer class="p-3 border-t border-gray-200 bg-gray-50 text-xs text-gray-500 text-center">
      End of document preview.
    </footer>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, computed } from 'vue';
import { X, FileText, FileType, FileImage, FileArchive, FileAudio, FileVideo, FileSpreadsheet, FileJson } from 'lucide-vue-next';
// import { marked } from 'marked'; // Uncomment if using marked

const props = defineProps({
  document: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['close']);

const closeViewer = () => {
  emit('close');
};

/* // Uncomment if using marked
const renderedMarkdown = computed(() => {
  if (props.document && props.document.content) {
    // Basic check if content looks like markdown (e.g., starts with #, *, etc.)
    // You might want a more robust check or rely on file type.
    const isMarkdown = /^(#|\*|-|>|\[|`)/m.test(props.document.content.substring(0, 500));
    if (isMarkdown || props.document.name.toLowerCase().endsWith('.md')) {
        return marked(props.document.content);
    }
    return `<pre class="whitespace-pre-wrap break-words text-xs">${props.document.content}</pre>`; // Fallback for non-markdown
  }
  return '';
});
*/

const iconComponent = computed(() => {
  if (!props.document || !props.document.name) return FileText;
  const name = props.document.name.toLowerCase();
  if (name.endsWith('.pdf')) return FileType;
  if (name.endsWith('.doc') || name.endsWith('.docx')) return FileText;
  if (name.endsWith('.xls') || name.endsWith('.xlsx')) return FileSpreadsheet;
  if (name.endsWith('.jpg') || name.endsWith('.jpeg') || name.endsWith('.png')) return FileImage;
  if (name.endsWith('.zip') || name.endsWith('.rar')) return FileArchive;
  if (name.endsWith('.mp3') || name.endsWith('.wav')) return FileAudio;
  if (name.endsWith('.mp4') || name.endsWith('.mov')) return FileVideo;
  if (name.endsWith('.json')) return FileJson;
  return FileText;
});
</script>

<style scoped>
/* For Tailwind Typography plugin (prose) styling */
/* If you install @tailwindcss/typography, add it to your tailwind.config.js plugins */
/* Example:
   @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
   .prose { font-family: 'Inter', sans-serif; }
*/
.prose pre {
  background-color: #f3f4f6; /* gray-100 */
  padding: 1em;
  border-radius: 0.375rem; /* rounded-md */
  overflow-x: auto;
}
</style>
