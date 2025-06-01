<template>
  <div>
    <h3 class="text-sm font-semibold text-gray-600 mb-3 flex items-center">
      <Tags class="h-4 w-4 mr-2 text-purple-600"/> Important Subjects
    </h3>
    <div class="mb-4">
        <input
            type="text"
            v-model="searchTerm"
            placeholder="Filter or add new subject..."
            class="w-full text-xs p-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500"
        />
        <button
            v-if="searchTerm && !uniqueSubjects.includes(searchTerm)"
            @click="addSubject(searchTerm)"
            class="mt-2 w-full btn btn-secondary btn-sm text-xs py-1.5 bg-purple-500 hover:bg-purple-600">
            Add "{{ searchTerm }}" as new subject
        </button>
    </div>
    <div v-if="filteredSubjects.length === 0 && !searchTerm" class="text-xs text-gray-500 text-center py-4">
        No subjects identified yet. AI can suggest some, or you can add them manually.
    </div>
    <div v-else-if="filteredSubjects.length === 0 && searchTerm" class="text-xs text-gray-500 text-center py-4">
        No subjects match "{{ searchTerm }}".
    </div>
    <div v-else class="max-h-96 overflow-y-auto space-y-1 pr-1">
      <button
        v-for="subject in filteredSubjects"
        :key="subject"
        @click="toggleSubjectSelection(subject)"
        :class="['w-full text-left text-xs p-2 rounded-md transition-colors flex justify-between items-center',
                 selectedSubject === subject ? 'bg-purple-600 text-white' : 'bg-gray-100 hover:bg-purple-100 text-gray-700 border border-gray-200']"
      >
        <span>{{ subject }}</span>
        <CheckCircle v-if="selectedSubject === subject" class="h-4 w-4 text-white"/>
      </button>
    </div>

    <button
        v-if="selectedSubject"
        @click="clearSelection"
        class="mt-3 w-full btn btn-secondary btn-sm text-xs py-1.5 bg-gray-500 hover:bg-gray-600">
        Clear Selection
    </button>

    <button @click="suggestSubjects" class="mt-4 w-full btn btn-secondary btn-sm text-xs py-1.5">
        <SparklesIcon class="h-4 w-4 mr-1.5 inline"/> AI Suggest Subjects
    </button>
  </div>
</template>

<script setup>
import { ref, computed, defineProps, defineEmits, onMounted } from 'vue';
import { Tags, CheckCircle, Sparkles as SparklesIcon } from 'lucide-vue-next';

const props = defineProps({
  documents: {
    type: Array,
    required: true,
    default: () => []
  }
});

const emit = defineEmits(['subjects-selected']);

const allKnownSubjects = ref([]); // This will hold all unique subjects from documents + user-added
const selectedSubject = ref(null);
const searchTerm = ref('');

const extractInitialSubjects = () => {
    const subjects = new Set();
    props.documents.forEach(doc => {
        (doc.subjects || []).forEach(s => subjects.add(s));
        (doc.keyPlayers || []).forEach(kp => subjects.add(kp)); // Treating key players as subjects too
    });
    allKnownSubjects.value = Array.from(subjects).sort();
};

onMounted(() => {
    extractInitialSubjects();
});

const uniqueSubjects = computed(() => {
    // Re-calculate if documents prop changes, though allKnownSubjects should be the primary source after init
    const subjects = new Set(allKnownSubjects.value);
    props.documents.forEach(doc => {
        (doc.subjects || []).forEach(s => subjects.add(s));
        (doc.keyPlayers || []).forEach(kp => subjects.add(kp));
    });
    return Array.from(subjects).sort();
});

const filteredSubjects = computed(() => {
    if (!searchTerm.value) {
        return uniqueSubjects.value;
    }
    return uniqueSubjects.value.filter(s => s.toLowerCase().includes(searchTerm.value.toLowerCase()));
});

const toggleSubjectSelection = (subject) => {
  if (selectedSubject.value === subject) {
    selectedSubject.value = null; // Deselect
    emit('subjects-selected', null);
  } else {
    selectedSubject.value = subject;
    emit('subjects-selected', subject);
  }
};

const addSubject = (subjectName) => {
    if (subjectName && !allKnownSubjects.value.includes(subjectName)) {
        allKnownSubjects.value.push(subjectName);
        allKnownSubjects.value.sort(); // Keep it sorted
        // Optionally select the newly added subject
        toggleSubjectSelection(subjectName);
        searchTerm.value = ''; // Clear search
    }
};

const clearSelection = () => {
    selectedSubject.value = null;
    emit('subjects-selected', null);
};

const suggestSubjects = () => {
    // Placeholder for AI subject suggestion logic
    alert("AI Subject Suggestion feature coming soon! This would analyze documents and suggest common themes or entities.");
    // Example:
    // const suggested = ['New Policy Idea', 'Economic Impact', 'Public Opinion'];
    // suggested.forEach(s => addSubject(s));
};

</script>

<style scoped>
.max-h-96::-webkit-scrollbar { width: 5px; }
.max-h-96::-webkit-scrollbar-thumb { background-color: #d1d5db; border-radius: 10px; }
.max-h-96::-webkit-scrollbar-track { background-color: #f3f4f6; }
</style>
