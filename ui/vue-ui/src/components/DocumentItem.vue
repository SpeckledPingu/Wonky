<template>
  <div
    :class="['flex items-center justify-between py-1.5 px-2 rounded-md group transition-all duration-150',
             isHighlighted ? 'bg-yellow-100 border-yellow-300 border-l-4' : 'hover:bg-blue-50']"
  >
    <div class="flex items-center overflow-hidden cursor-pointer flex-1 min-w-0" @click.stop="emitClick">
      <input
        type="checkbox"
        :checked="isSelected"
        @change.stop="toggleSelect"
        @click.stop
        class="form-checkbox h-3.5 w-3.5 text-blue-600 border-gray-300 rounded focus:ring-blue-500 mr-2 flex-shrink-0"
      />
      <component :is="iconComponent" :class="['h-4 w-4 mr-1.5 flex-shrink-0 group-hover:text-blue-600', isHighlighted ? 'text-yellow-600' : 'text-gray-500']" />
      <span
        :class="['text-xs group-hover:text-blue-700 truncate', isHighlighted ? 'text-yellow-700 font-medium' : 'text-gray-700']"
        :title="document.name"
      >
        {{ document.name }}
      </span>
    </div>
    </div>
</template>

<script setup>
import { defineProps, defineEmits, computed } from 'vue';
import { FileText, FileType, FileImage, FileArchive, FileAudio, FileVideo, FileSpreadsheet, FileJson } from 'lucide-vue-next';

const props = defineProps({
  document: {
    type: Object,
    required: true
  },
  isSelected: Boolean,
  isHighlighted: Boolean // New prop
});

const emit = defineEmits(['click', 'toggle-select']);

const emitClick = () => {
  emit('click', props.document);
};

const toggleSelect = () => {
  emit('toggle-select', props.document.id);
};

const iconComponent = computed(() => {
  const name = props.document.name.toLowerCase();
  if (name.endsWith('.pdf')) return FileType;
  if (name.endsWith('.doc') || name.endsWith('.docx')) return FileText;
  if (name.endsWith('.xls') || name.endsWith('.xlsx')) return FileSpreadsheet;
  if (name.endsWith('.jpg') || name.endsWith('.jpeg') || name.endsWith('.png')) return FileImage;
  if (name.endsWith('.zip') || name.endsWith('.rar')) return FileArchive;
  if (name.endsWith('.mp3') || name.endsWith('.wav')) return FileAudio;
  if (name.endsWith('.mp4') || name.endsWith('.mov')) return FileVideo;
  if (name.endsWith('.json')) return FileJson;
  return FileText; // Default icon
});
</script>

<style scoped>
.form-checkbox:checked {
  background-color: #3b82f6; /* blue-500 */
  border-color: #3b82f6;
}
.truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
/* Highlighting style example */
.bg-yellow-100 { background-color: #fef9c3; } /* Tailwind yellow-100 */
.border-yellow-300 { border-color: #fcd34d; } /* Tailwind yellow-300 */
.text-yellow-700 { color: #b45309; } /* Tailwind yellow-700 */
.text-yellow-600 { color: #ca8a04; } /* Tailwind yellow-600 */
</style>
