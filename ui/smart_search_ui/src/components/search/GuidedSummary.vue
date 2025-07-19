<template>
  <div class="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
    <h3 class="font-semibold text-lg text-gray-700 mb-3">Guided Summary</h3>
    <div class="space-y-3">
        <div>
            <label for="interest-input" class="block text-sm font-medium text-gray-600 mb-1">
                Guiding Prompt
            </label>
            <input
                type="text"
                id="interest-input"
                :value="searchStore.guidingPrompt"
                @input="searchStore.setGuidingPrompt($event.target.value)"
                placeholder="e.g., focus on policy implications..."
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            />
            <p class="text-xs text-gray-500 mt-1">
                This prompt will guide the search and summary generation.
            </p>
        </div>
        <div>
            <label class="block text-sm font-medium text-gray-600 mb-1">
                Summary List
            </label>
            <div class="min-h-[8rem] bg-gray-50 p-3 rounded-md border text-sm custom-scrollbar overflow-y-auto">
                <p v-if="searchStore.isPolling && searchStore.summaryItems.length === 0" class="text-gray-500 animate-pulse">Generating summaries...</p>
                <ul v-else-if="searchStore.summaryItems.length > 0" class="list-disc list-inside space-y-2">
                    <li v-for="item in searchStore.summaryItems" :key="item.docId">
                        {{ item.summary }}
                        <button @click="viewDocument(item.docId)" class="text-blue-600 hover:underline ml-1 font-semibold">(view doc)</button>
                    </li>
                     <li v-if="searchStore.isPolling" class="text-gray-500 animate-pulse list-none">... more summaries generating</li>
                </ul>
                <p v-else class="text-gray-500">Summaries of relevant results will appear here asynchronously.</p>
            </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { useSearchStore } from '../../stores/searchStore';
import { useDocumentStore } from '../../stores/documentStore';

const searchStore = useSearchStore();
const documentStore = useDocumentStore();

const viewDocument = (docId) => {
  documentStore.viewDocument(docId);
};
</script>
