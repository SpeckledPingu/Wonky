<template>
  <div class="flex flex-col h-screen overflow-hidden bg-gray-100">
    <header class="bg-white shadow-sm border-b border-gray-200 flex-shrink-0">
      <div class="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center">
            <LibraryBig class="h-8 w-8 text-indigo-600 mr-3" />
            <h1 class="text-2xl sm:text-3xl font-bold text-gray-800">Prompt Library & Composer</h1>
          </div>
          <button @click="goBackToProjects" class="btn btn-secondary text-sm">
            <ArrowLeft class="h-4 w-4 mr-1.5 inline-block" />
            Back to Projects
          </button>
        </div>
      </div>
    </header>

    <div class="flex flex-1 overflow-hidden" ref="mainContentAreaRef">
      <aside
        :style="{ flexBasis: `${leftPanelWidthPercent}%` }"
        class="bg-white border-r border-gray-200 flex flex-col overflow-y-auto p-4 flex-shrink-0"
        ref="leftPanelRef"
      >
        <h2 class="text-xl font-semibold text-gray-700 mb-4 sticky top-0 bg-white py-2 z-10 border-b">
            <Blocks class="h-5 w-5 text-teal-500 mr-2 inline-block"/> Component Library
        </h2>
        <div class="space-y-5">
          <div v-for="group in componentGroups" :key="group.type" class="p-3 border rounded-lg bg-gray-50 shadow-sm">
            <h3 class="text-md font-medium text-gray-600 mb-2.5 flex items-center">
              <component :is="group.icon" class="h-5 w-5 mr-2" :class="group.iconColor" />
              {{ group.name }}
            </h3>
            <div v-if="group.components.length === 0" class="text-xs text-gray-400 italic">No {{ group.type }} components.</div>
            <div v-else class="space-y-1.5 max-h-72 overflow-y-auto pr-1">
              <div v-for="component in group.components" :key="component.id" class="p-2.5 border rounded-md bg-white hover:border-teal-400 transition-colors">
                <h4 class="font-semibold text-xs text-teal-700 mb-1">{{ component.name }}</h4>
                <div class="text-xs text-gray-500 bg-gray-100 p-1.5 rounded max-h-20 overflow-y-auto border mb-1.5">
                  <pre class="whitespace-pre-wrap break-words">{{ component.content }}</pre>
                </div>
                <button @click="addComponentToComposer(component)" class="btn btn-secondary btn-sm text-xs bg-teal-500 hover:bg-teal-600 text-white !py-1 !px-2">
                  <PlusCircle class="h-3.5 w-3.5 mr-1 inline"/> Add to Composer
                </button>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <div
        class="w-1.5 bg-gray-300 hover:bg-indigo-500 cursor-col-resize flex-shrink-0 transition-colors select-none"
        @mousedown="startResize($event, 'left')"
      ></div>

      <main
        :style="{ flexBasis: `${centerPanelWidthPercent}%` }"
        class="bg-gray-50 flex flex-col overflow-y-auto p-4 flex-shrink-0"
      >
        <h2 class="text-xl font-semibold text-gray-700 mb-4 sticky top-0 bg-gray-50 py-2 z-10 border-b">
            <Wand2 class="h-5 w-5 text-purple-500 mr-2 inline-block"/> Prompt Composer
        </h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-600 mb-1">Save Destination <span class="text-red-500">*</span></label>
            <div class="flex space-x-4">
                <label v-for="dest in saveDestinations" :key="dest.value" class="flex items-center">
                    <input type="radio" :value="dest.value" v-model="currentComposingPrompt.saveTarget" class="form-radio h-4 w-4 text-indigo-600 border-gray-300 focus:ring-indigo-500">
                    <span class="ml-2 text-sm text-gray-700">{{ dest.label }}</span>
                </label>
            </div>
          </div>

          <div>
            <label for="composedPromptName" class="block text-sm font-medium text-gray-600 mb-1">Prompt Name <span class="text-red-500">*</span></label>
            <input type="text" id="composedPromptName" v-model="currentComposingPrompt.name" placeholder="e.g., Healthcare Policy Initial Analysis" class="input-base" />
          </div>

          <div>
            <label for="composedPromptType" class="block text-sm font-medium text-gray-600 mb-1">
              {{ currentComposingPrompt.saveTarget === 'component' ? 'Component Type' : 'Library Prompt Type' }} <span class="text-red-500">*</span>
            </label>
            <select id="composedPromptType" v-model="currentComposingPrompt.type" class="input-base">
              <option disabled value="">Select a type</option>
              <option v-for="option in currentPromptTypeOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
            </select>
          </div>

           <div v-if="currentComposingPrompt.saveTarget === 'libraryPrompt' && (currentComposingPrompt.type === 'studioAction' || currentComposingPrompt.type === 'streamAnalysis')">
            <label for="composedPromptPolicyType" class="block text-sm font-medium text-gray-600 mb-1">Target Policy Type (Optional)</label>
            <input type="text" id="composedPromptPolicyType" v-model="currentComposingPrompt.policyType" placeholder="e.g., Healthcare, Environment" class="input-base" />
          </div>

          <div>
            <label for="promptText" class="block text-sm font-medium text-gray-600 mb-1">Prompt Content <span class="text-red-500">*</span></label>
            <textarea id="promptText" v-model="currentComposingPrompt.content" rows="10" class="input-base text-sm" placeholder="Combine components or write your custom prompt..."></textarea>
          </div>
          <div class="text-xs text-gray-500">
            <p>Components Used: {{ currentComposingPrompt.componentsUsed.join(', ') || 'None' }}</p>
          </div>
          <div class="flex space-x-3">
            <button v-if="!editingPromptId" @click="saveComposedPrompt" class="btn btn-primary bg-purple-600 hover:bg-purple-700 text-sm">
              <Save class="h-4 w-4 mr-1.5 inline"/> Save New Prompt
            </button>
            <button v-if="editingPromptId" @click="updateSavedPrompt" class="btn btn-primary bg-green-600 hover:bg-green-700 text-sm">
              <CheckCircle class="h-4 w-4 mr-1.5 inline"/> Update Prompt
            </button>
            <button @click="clearComposer" class="btn btn-secondary text-sm">
              <RotateCcw class="h-4 w-4 mr-1.5 inline"/> Clear Composer
            </button>
          </div>
        </div>
      </main>

      <div
        class="w-1.5 bg-gray-300 hover:bg-indigo-500 cursor-col-resize flex-shrink-0 transition-colors select-none"
        @mousedown="startResize($event, 'right')"
      ></div>

      <aside
        :style="{ flexBasis: `${rightPanelWidthPercent}%` }"
        class="bg-white border-l border-gray-200 flex flex-col overflow-y-auto p-4 flex-shrink-0"
        ref="rightPanelRef"
      >
        <h2 class="text-xl font-semibold text-gray-700 mb-4 sticky top-0 bg-white py-2 z-10 border-b">
            <Archive class="h-5 w-5 text-indigo-500 mr-2 inline-block"/> Saved Prompts Library
        </h2>
        <div v-if="groupedSavedLibraryPrompts.length === 0" class="card text-center text-gray-500">
          <p>No library prompts saved yet. Use the composer to create some!</p>
        </div>
        <div v-else class="space-y-5">
            <div v-for="group in groupedSavedLibraryPrompts" :key="group.type">
                <h3 class="text-md font-semibold text-indigo-700 mb-2 mt-3 border-b pb-1">
                    {{ getLibraryPromptTypeLabel(group.type) }} ({{ group.prompts.length }})
                </h3>
                <div class="space-y-2 max-h-96 overflow-y-auto pr-1">
                    <div v-for="prompt in group.prompts" :key="prompt.id"
                         class="p-3 border rounded-lg hover:shadow-md transition-shadow cursor-pointer bg-gray-50 hover:border-indigo-300"
                         @click="loadPromptIntoComposer(prompt, 'libraryPrompt')">
                        <div class="flex justify-between items-start">
                            <h4 class="font-medium text-sm text-gray-800 mb-1">{{ prompt.name }}</h4>
                            <span class="text-xs bg-indigo-100 text-indigo-600 px-1.5 py-0.5 rounded-full">{{ getLibraryPromptTypeLabel(prompt.type, true) }}</span>
                        </div>
                        <p v-if="prompt.policyType" class="text-xs text-gray-500 mb-1.5">Policy Type: {{ prompt.policyType }}</p>
                        <div class="text-xs text-gray-600 bg-white p-2 rounded max-h-24 overflow-y-auto border mb-2">
                            <pre class="whitespace-pre-wrap break-words">{{ prompt.content.substring(0, 150) }}{{ prompt.content.length > 150 ? '...' : '' }}</pre>
                        </div>
                        <div class="flex space-x-2 justify-end">
                            <button @click.stop="loadPromptIntoComposer(prompt, 'libraryPrompt')" class="btn btn-primary btn-sm text-xs !py-1 !px-2">Edit</button>
                            <button @click.stop="deleteSavedPrompt(prompt.id)" class="btn btn-danger btn-sm text-xs !py-1 !px-2">Delete</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue';
import { useRouter } from 'vue-router';
import { LibraryBig, Archive, Blocks, Settings2, ShieldCheck, Brain, Wand2, PlusCircle, Save, RotateCcw, ArrowLeft, CheckCircle } from 'lucide-vue-next';

const router = useRouter();

// --- Refs for DOM elements and resizing ---
const mainContentAreaRef = ref(null);
const leftPanelRef = ref(null);
const rightPanelRef = ref(null);

const leftPanelWidthPercent = ref(25);
const centerPanelWidthPercent = ref(40);
const rightPanelWidthPercent = computed(() => 100 - leftPanelWidthPercent.value - centerPanelWidthPercent.value);

const isResizing = ref(false);
const activeResizer = ref(null);
const dragStartX = ref(0);
const initialLeftWidthPx = ref(0);
const initialCenterWidthPx = ref(0);
const minPanelPercent = 15;

// --- Prompt Data and State ---
const saveDestinations = ref([
    { value: 'libraryPrompt', label: 'Library Prompt (for Research Pane)' },
    { value: 'component', label: 'Prompt Component (Reusable Part)' }
]);

const libraryPromptTypeOptions = ref([
    { value: 'streamAnalysis', label: 'Research Stream Analysis' },
    { value: 'studioAction', label: 'Studio Action Button' },
    { value: 'guidedChatPersona', label: 'Guided Chat: Persona' },
    { value: 'guidedChatTangent', label: 'Guided Chat: Tangent' },
    { value: 'generalPurpose', label: 'General Purpose Prompt' },
]);

const componentTypeOptions = ref([
    { value: 'system', label: 'System Prompt (Persona, Context)' },
    { value: 'rule', label: 'Rule Prompt (Constraint, Guideline)' },
    { value: 'analysis', label: 'Analysis Prompt (Task, Framework)' },
    { value: 'utility', label: 'Utility Snippet (Reusable Text)' },
]);

const currentPromptTypeOptions = computed(() => {
    return currentComposingPrompt.value.saveTarget === 'component' ? componentTypeOptions.value : libraryPromptTypeOptions.value;
});

const getLibraryPromptTypeLabel = (value, short = false) => {
    const option = libraryPromptTypeOptions.value.find(opt => opt.value === value);
    if (!option) return value;
    return short ? option.label.split(':')[0] : option.label;
};

const getComponentTypeLabel = (value, short = false) => {
    const option = componentTypeOptions.value.find(opt => opt.value === value);
    if (!option) return value;
    return short ? option.label.split(' ')[0] : option.label; // Basic shortening
};


const savedLibraryPrompts = ref([
  { id: 'sp1', name: 'USF Initial Analysis', type: 'studioAction', policyType: 'Telecommunications', content: 'System: You are a policy analyst. Rule: Focus on USF. Analysis: Summarize key challenges and opportunities for the Universal Service Fund.', componentsUsed: ['usf-system', 'usf-rule', 'usf-analysis-summary'] },
  { id: 'sp2', name: 'Environmental Impact Report Outline', type: 'streamAnalysis', policyType: 'Environment', content: 'System: You are an environmental scientist. Analysis: Generate an outline for an environmental impact report regarding new infrastructure project X.', componentsUsed: ['env-system', 'env-impact-outline'] },
  { id: 'sp3', name: 'Economist Persona for Chat', type: 'guidedChatPersona', policyType: '', content: 'You are an economist focusing on macro-economic impacts. Analyze the economic consequences, costs, and benefits. Begin by asking for the specific policy or document to analyze.', componentsUsed: [] },
]);

const promptComponents = ref([
  { id: 'compSys1', name: 'Policy Analyst Persona', type: 'system', content: 'You are an expert policy analyst with 20 years of experience in [specific policy area]. Your goal is to provide concise, actionable insights.' },
  { id: 'compRule1', name: 'Focus on Specific Legislation', type: 'rule', content: 'Strictly adhere to the provisions and intent of [Legislation Name, Year]. Do not infer outside of this scope unless specified.' },
  { id: 'compAnalysis1', name: 'SWOT Analysis', type: 'analysis', content: 'Conduct a SWOT analysis (Strengths, Weaknesses, Opportunities, Threats) for the proposed policy.' },
  { id: 'compUtil1', name: 'Standard Disclaimer', type: 'utility', content: 'The information provided is for analytical purposes only and does not constitute legal advice.'}
]);

const componentGroups = computed(() => [
  { name: 'System Prompts', type: 'system', components: promptComponents.value.filter(c => c.type === 'system'), icon: Settings2, iconColor: 'text-blue-500' },
  { name: 'Rule Prompts', type: 'rule', components: promptComponents.value.filter(c => c.type === 'rule'), icon: ShieldCheck, iconColor: 'text-red-500' },
  { name: 'Analysis Prompts', type: 'analysis', components: promptComponents.value.filter(c => c.type === 'analysis'), icon: Brain, iconColor: 'text-green-500' },
  { name: 'Utility Snippets', type: 'utility', components: promptComponents.value.filter(c => c.type === 'utility'), icon: Wand2, iconColor: 'text-purple-500'}
]);

const defaultComposingPrompt = () => ({
  id: null, name: '', type: '', policyType: '', content: '', componentsUsed: [], saveTarget: 'libraryPrompt' // Default to saving as library prompt
});

const currentComposingPrompt = ref(defaultComposingPrompt());
const editingPromptId = ref(null); // Stores ID of prompt being edited, regardless of type

watch(() => currentComposingPrompt.value.saveTarget, (newTarget) => {
    // Reset type when saveTarget changes to avoid invalid type selection
    currentComposingPrompt.value.type = '';
    currentComposingPrompt.value.policyType = ''; // Also reset policy type
});


const groupedSavedLibraryPrompts = computed(() => {
    const groups = {};
    libraryPromptTypeOptions.value.forEach(option => {
        groups[option.value] = { type: option.value, label: option.label, prompts: [] };
    });

    savedLibraryPrompts.value.forEach(prompt => {
        if (groups[prompt.type]) {
            groups[prompt.type].prompts.push(prompt);
        } else {
            if (!groups['generalPurpose']) groups['generalPurpose'] = { type: 'generalPurpose', label: 'General Purpose Prompts', prompts: [] };
            groups['generalPurpose'].prompts.push(prompt); // Fallback to general if type unknown
        }
    });
    return Object.values(groups).filter(group => group.prompts.length > 0);
});


// --- Methods ---
const addComponentToComposer = (component) => {
  if (currentComposingPrompt.value.content) {
    currentComposingPrompt.value.content += '\n\n';
  }
  currentComposingPrompt.value.content += component.content;
  if (!currentComposingPrompt.value.componentsUsed.includes(component.name)) {
    currentComposingPrompt.value.componentsUsed.push(component.name);
  }
};

const saveComposedPrompt = () => {
  if (!currentComposingPrompt.value.name.trim() || !currentComposingPrompt.value.content.trim() || !currentComposingPrompt.value.type) {
    alert('Please provide a name, type, and content for the prompt.');
    return;
  }

  const newPromptData = {
    name: currentComposingPrompt.value.name,
    type: currentComposingPrompt.value.type,
    content: currentComposingPrompt.value.content,
    componentsUsed: [...currentComposingPrompt.value.componentsUsed],
    policyType: currentComposingPrompt.value.saveTarget === 'libraryPrompt' ? currentComposingPrompt.value.policyType : undefined, // Only for library prompts
  };

  if (currentComposingPrompt.value.saveTarget === 'component') {
    const newComponent = { ...newPromptData, id: `comp${Date.now()}` };
    promptComponents.value.unshift(newComponent);
    alert(`Component "${newComponent.name}" saved!`);
  } else { // libraryPrompt
    const newLibraryPrompt = { ...newPromptData, id: `sp${Date.now()}` };
    savedLibraryPrompts.value.unshift(newLibraryPrompt);
    alert(`Library Prompt "${newLibraryPrompt.name}" saved!`);
  }
  clearComposer();
};

const updateSavedPrompt = () => {
    if (!editingPromptId.value) return;

    const updatedData = {
        name: currentComposingPrompt.value.name,
        type: currentComposingPrompt.value.type,
        content: currentComposingPrompt.value.content,
        componentsUsed: [...currentComposingPrompt.value.componentsUsed],
        policyType: currentComposingPrompt.value.saveTarget === 'libraryPrompt' ? currentComposingPrompt.value.policyType : undefined,
    };

    if (currentComposingPrompt.value.saveTarget === 'component') {
        const index = promptComponents.value.findIndex(p => p.id === editingPromptId.value);
        if (index !== -1) {
            promptComponents.value[index] = { ...updatedData, id: editingPromptId.value };
            alert(`Component "${updatedData.name}" updated!`);
        }
    } else { // libraryPrompt
        const index = savedLibraryPrompts.value.findIndex(p => p.id === editingPromptId.value);
        if (index !== -1) {
            savedLibraryPrompts.value[index] = { ...updatedData, id: editingPromptId.value };
            alert(`Library Prompt "${updatedData.name}" updated!`);
        }
    }
    clearComposer();
};

const loadPromptIntoComposer = (prompt, saveTarget) => { // saveTarget indicates if it's from library or components
    currentComposingPrompt.value = {
        ...prompt,
        componentsUsed: [...(prompt.componentsUsed || [])],
        saveTarget: saveTarget // Set the save target based on where it was loaded from
    };
    editingPromptId.value = prompt.id;
};

const clearComposer = () => {
  currentComposingPrompt.value = defaultComposingPrompt();
  editingPromptId.value = null;
};

const deleteSavedPrompt = (promptId) => { // This will delete from savedLibraryPrompts
    if (confirm('Are you sure you want to delete this saved library prompt?')) {
        savedLibraryPrompts.value = savedLibraryPrompts.value.filter(p => p.id !== promptId);
        if (editingPromptId.value === promptId && currentComposingPrompt.value.saveTarget === 'libraryPrompt') {
            clearComposer();
        }
        alert('Library prompt deleted.');
    }
};
// You might need a separate deletePromptComponent if you allow deleting components from the left pane directly.
// For now, components are only managed through creation/editing via composer.

const goBackToProjects = () => {
  router.push({ name: 'ProjectsView' });
};

// --- Resizing Logic ---
const startResize = (event, resizer) => {
  event.preventDefault();
  isResizing.value = true;
  activeResizer.value = resizer;
  dragStartX.value = event.clientX;

  if (mainContentAreaRef.value) {
    const children = Array.from(mainContentAreaRef.value.children).filter(el => el.offsetParent !== null); // Get visible children
    if (children.length >= 3) { // Left, Resizer, Center, Resizer, Right
        initialLeftWidthPx.value = children[0].offsetWidth; // Left Panel
        initialCenterWidthPx.value = children[2].offsetWidth; // Center Panel
    }
  }

  document.body.style.cursor = 'col-resize';
  document.body.style.userSelect = 'none';

  window.addEventListener('mousemove', handleDrag);
  window.addEventListener('mouseup', stopDrag);
};

const handleDrag = (event) => {
  if (!isResizing.value || !mainContentAreaRef.value) return;

  const deltaX = event.clientX - dragStartX.value;
  const totalWidthPx = mainContentAreaRef.value.offsetWidth;
  if (totalWidthPx === 0) return;

  if (activeResizer.value === 'left') {
    let newLeftWidthPx = initialLeftWidthPx.value + deltaX;
    let newCenterWidthPx = initialCenterWidthPx.value - deltaX;

    const newLeftPercent = (newLeftWidthPx / totalWidthPx) * 100;
    const newCenterPercent = (newCenterWidthPx / totalWidthPx) * 100;
    const currentRightPercent = rightPanelWidthPercent.value;

    if (newLeftPercent >= minPanelPercent && newCenterPercent >= minPanelPercent && (newLeftPercent + newCenterPercent + currentRightPercent) <= 100.5 ) { // Added tolerance
      leftPanelWidthPercent.value = parseFloat(newLeftPercent.toFixed(2));
      centerPanelWidthPercent.value = parseFloat(newCenterPercent.toFixed(2));
    }
  } else if (activeResizer.value === 'right') {
    let newCenterWidthPx = initialCenterWidthPx.value + deltaX;
    // Right panel width is computed (100 - left - center)

    let newCenterPercent = (newCenterWidthPx / totalWidthPx) * 100;
    const currentLeftPercent = leftPanelWidthPercent.value;
    const newRightPercentIfAdjusted = 100 - currentLeftPercent - newCenterPercent;

    if (newCenterPercent >= minPanelPercent && newRightPercentIfAdjusted >= minPanelPercent && (currentLeftPercent + newCenterPercent + newRightPercentIfAdjusted) <= 100.5) { // Added tolerance
        centerPanelWidthPercent.value = parseFloat(newCenterPercent.toFixed(2));
    }
  }
};

const stopDrag = () => {
  isResizing.value = false;
  activeResizer.value = null;
  document.body.style.cursor = '';
  document.body.style.userSelect = '';
  window.removeEventListener('mousemove', handleDrag);
  window.removeEventListener('mouseup', stopDrag);
};

onMounted(() => {
  // Initial setup if needed
});
onBeforeUnmount(() => {
  window.removeEventListener('mousemove', handleDrag);
  window.removeEventListener('mouseup', stopDrag);
});

</script>

<style scoped>
.input-base {
  @apply block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm;
}
.max-h-72::-webkit-scrollbar, .max-h-96::-webkit-scrollbar { width: 6px; }
.max-h-72::-webkit-scrollbar-thumb, .max-h-96::-webkit-scrollbar-thumb { background-color: #cbd5e1; border-radius: 10px; }
.max-h-72::-webkit-scrollbar-track, .max-h-96::-webkit-scrollbar-track { background-color: #f1f5f9; }
.select-none { user-select: none; }
.flex-shrink-0 { flex-shrink: 0; }

.flex-1.overflow-hidden {
    height: calc(100vh - 4rem);
}
.sticky {
  position: -webkit-sticky;
  position: sticky;
}
.form-radio {
    @apply focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300;
}
</style>
