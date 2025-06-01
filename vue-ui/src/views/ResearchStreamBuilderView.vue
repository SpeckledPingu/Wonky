<template>
  <div class="flex flex-col h-screen overflow-hidden bg-gray-100">
    <header class="bg-white shadow-sm border-b border-gray-200 flex-shrink-0">
      <div class="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center">
            <Workflow class="h-8 w-8 text-teal-600 mr-3" />
            <h1 class="text-2xl sm:text-3xl font-bold text-gray-800">Research Stream Builder</h1>
          </div>
          <div class="flex items-center space-x-3">
            <input 
                type="text" 
                v-model="workflowName" 
                placeholder="Workflow Name" 
                class="input-base text-sm py-1.5 px-3 w-64"
            />
            <button @click="saveWorkflow" class="btn btn-success text-sm">
                <Save class="h-4 w-4 mr-1.5 inline-block" /> Save Workflow
            </button>
             <button @click="toggleExportModal" class="btn btn-secondary text-sm">
                <Download class="h-4 w-4 mr-1.5 inline-block" /> Export
            </button>
          </div>
        </div>
      </div>
    </header>

    <div class="flex flex-1 overflow-hidden" ref="mainContentAreaRef">
      <aside 
        :style="{ flexBasis: `${leftPanelWidthPercent}%` }"
        class="bg-white border-r border-gray-200 flex flex-col overflow-y-auto p-4 flex-shrink-0"
      >
        <h2 class="text-lg font-semibold text-gray-700 mb-4 sticky top-0 bg-white py-2 z-10 border-b">
            <Puzzle class="h-5 w-5 text-sky-500 mr-2 inline-block"/> Action Palette
        </h2>
        <div class="space-y-2">
          <div v-for="group in actionPaletteGroups" :key="group.id" class="border rounded-lg overflow-hidden">
            <button 
              @click="togglePaletteGroup(group.id)"
              class="w-full flex items-center justify-between p-3 text-left bg-gray-100 hover:bg-gray-200 focus:outline-none transition-colors"
            >
              <div class="flex items-center">
                <component :is="group.icon" class="h-5 w-5 mr-2" :class="group.iconColor || 'text-gray-700'"/>
                <span class="text-sm font-medium text-gray-800">{{ group.name }}</span>
              </div>
              <ChevronDown class="h-5 w-5 text-gray-500 transition-transform duration-200" :class="{'rotate-180': paletteGroupOpenState[group.id]}" />
            </button>
            <div v-if="paletteGroupOpenState[group.id]" class="p-3 bg-white space-y-2 border-t">
              <div v-if="group.actions.length === 0" class="text-xs text-gray-400 italic text-center py-2">
                No actions in this group.
              </div>
              <div v-for="action in group.actions" :key="action.id"
                   class="p-2.5 border rounded-md bg-gray-50 shadow-sm hover:shadow-md cursor-grab transition-all hover:border-sky-300"
                   draggable="true"
                   @dragstart="handleDragStart($event, action)">
                <div class="flex items-center">
                  <component :is="action.icon" class="h-4 w-4 mr-2 flex-shrink-0" :class="action.iconColor || 'text-gray-600'"/>
                  <span class="text-xs font-medium text-gray-700">{{ action.name }}</span>
                </div>
                <p v-if="action.description" class="text-xs text-gray-500 mt-1 truncate" :title="action.description">{{ action.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <div 
        class="w-1.5 bg-gray-300 hover:bg-teal-500 cursor-col-resize flex-shrink-0 transition-colors select-none"
        @mousedown="startResize($event, 'left')"
      ></div>

      <main 
        :style="{ flexBasis: `${centerPanelWidthPercent}%` }"
        class="bg-gray-100 flex flex-col overflow-hidden flex-shrink-0 relative"
        @dragover.prevent="handleDragOver"
        @drop="handleDrop"
      >
        <div ref="networkCanvasRef" class="w-full h-full bg-dots"></div>
        <div v-if="workflowNodes.length === 0" class="absolute inset-0 flex items-center justify-center text-gray-400 text-lg pointer-events-none">
            <p>Drag actions from the palette to build your stream.</p>
        </div>
         <div class="absolute top-2 right-2 flex items-center space-x-2 z-10">
            <span v-if="edgeModeActive" class="text-xs text-blue-600 animate-pulse font-semibold bg-white/70 backdrop-blur-sm px-2 py-1 rounded-md">Connect Mode Active</span>
            <button @click="toggleEdgeMode" :class="['p-2 rounded-md shadow hover:shadow-lg transition-all', edgeModeActive ? 'bg-blue-500 text-white' : 'bg-white text-gray-700']" title="Toggle Edge Creation Mode">
                <Link class="h-5 w-5"/>
            </button>
        </div>
      </main>

      <div 
        class="w-1.5 bg-gray-300 hover:bg-teal-500 cursor-col-resize flex-shrink-0 transition-colors select-none"
        @mousedown="startResize($event, 'right')"
      ></div>
      
      <aside
        :style="{ flexBasis: `${rightPanelWidthPercent}%` }"
        class="bg-white border-l border-gray-200 flex flex-col overflow-y-auto p-4 flex-shrink-0"
      >
        <h2 class="text-lg font-semibold text-gray-700 mb-4 sticky top-0 bg-white py-2 z-10 border-b">
            <Settings class="h-5 w-5 text-gray-500 mr-2 inline-block"/> Properties / Settings
        </h2>
        <div v-if="selectedNodeDetails">
            <h3 class="text-md font-medium text-gray-800 mb-2">Node: {{ selectedNodeDetails.label }}</h3>
            <p class="text-xs text-gray-500 mb-1">ID: {{ selectedNodeDetails.id }}</p>
            <p class="text-xs text-gray-500 mb-3">Type: {{ selectedNodeDetails.actionType }}{{ selectedNodeDetails.subType ? ` (${selectedNodeDetails.subType})` : '' }}</p>

            <label class="block text-sm font-medium text-gray-600 mb-1">Node Label:</label>
            <input type="text" v-model="editableNodeLabel" @change="updateNodeLabel" class="input-base mb-3"/>

            <div v-if="selectedNodeDetails.actionType === 'customAnalysis' && selectedNodeDetails.promptId">
                <p class="text-sm font-medium text-gray-600 mb-1">Using Prompt:</p>
                <p class="text-xs text-purple-700 bg-purple-50 p-2 rounded">{{ getPromptNameById(selectedNodeDetails.promptId) }}</p>
            </div>
             <button @click="deleteSelectedNode" class="btn btn-danger btn-sm w-full mt-4">Delete Selected Node</button>
        </div>
        <div v-else-if="selectedEdgeId">
             <h3 class="text-md font-medium text-gray-800 mb-2">Edge Selected</h3>
             <p class="text-xs text-gray-500 mb-1">ID: {{ selectedEdgeId }}</p>
             <p class="text-xs text-gray-500 mb-3">From: {{ selectedEdgeDetails?.fromNodeLabel }} <br/> To: {{ selectedEdgeDetails?.toNodeLabel }}</p>
             <button @click="deleteSelectedEdge" class="btn btn-danger btn-sm w-full mt-4">Delete Selected Edge</button>
        </div>
        <div v-else class="text-sm text-gray-500">
            Select a node or edge on the canvas to see its properties or delete it.
        </div>
      </aside>
    </div>

    <div v-if="showExportModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center z-50" @click.self="toggleExportModal">
        <div class="relative mx-auto p-5 border w-full max-w-md shadow-lg rounded-md bg-white">
            <div class="mt-3 text-center">
                <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-blue-100 mb-3">
                    <Download class="h-6 w-6 text-blue-600" />
                </div>
                <h3 class="text-lg leading-6 font-medium text-gray-900">Export Workflow</h3>
                <div class="mt-4 px-7 py-3 space-y-3">
                    <button @click="exportToMermaid" class="w-full btn btn-primary text-sm">Export as Mermaid Diagram</button>
                    <button @click="exportToJSON" class="w-full btn btn-primary text-sm">Export as JSON</button>
                </div>
                <div class="items-center px-4 py-3">
                    <button @click="toggleExportModal" class="px-4 py-2 bg-gray-200 text-gray-800 text-base font-medium rounded-md w-full shadow-sm hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-300">
                        Close
                    </button>
                </div>
            </div>
        </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
import { Network, DataSet } from 'vis-network/standalone';
import 'vis-network/styles/vis-network.min.css';
import {
    Workflow, Save, Download, Puzzle, Search, Activity, Scissors, Combine, FileText, Settings, ArrowLeft,
    AlertTriangle, ChevronDown, Link, Globe, Database, FileSearch, FileSignature, ListFilter, TextCursorInput, Edit3, Users, SigmaSquare, GitCompareArrows, Brain, Scale, Send as SendIcon, BarChart2
} from 'lucide-vue-next';

// --- Resizing State & Refs ---
const mainContentAreaRef = ref(null);
const leftPanelWidthPercent = ref(20);
const centerPanelWidthPercent = ref(55);
const rightPanelWidthPercent = computed(() => 100 - leftPanelWidthPercent.value - centerPanelWidthPercent.value);
const isResizing = ref(false);
const activeResizer = ref(null);
const dragStartX = ref(0);
const initialLeftWidthPx = ref(0);
const initialCenterWidthPx = ref(0);
const minPanelPercent = 15;

// --- Workflow State ---
const workflowName = ref('My New Research Stream');
const networkCanvasRef = ref(null);
let visNetwork = null;
const workflowNodesDataSet = new DataSet();
const workflowEdgesDataSet = new DataSet();
const workflowNodes = ref([]);
const workflowEdges = ref([]);

const draggedAction = ref(null);
const selectedNodeId = ref(null);
const selectedEdgeId = ref(null);
const editableNodeLabel = ref('');

const selectedNodeDetails = computed(() => {
    if (!selectedNodeId.value) return null;
    return workflowNodes.value.find(n => n.id === selectedNodeId.value) || null;
});

const selectedEdgeDetails = computed(() => {
    if(!selectedEdgeId.value) return null;
    const edge = workflowEdges.value.find(e => e.id === selectedEdgeId.value);
    if (edge) {
        const fromNode = workflowNodes.value.find(n => n.id === edge.from);
        const toNode = workflowNodes.value.find(n => n.id === edge.to);
        return {
            ...edge,
            fromNodeLabel: fromNode ? fromNode.label : edge.from,
            toNodeLabel: toNode ? toNode.label : edge.to,
        };
    }
    return null;
});

watch(selectedNodeDetails, (newNode) => {
    if (newNode) {
        editableNodeLabel.value = newNode.label;
        selectedEdgeId.value = null;
    } else {
        editableNodeLabel.value = '';
    }
});
watch(selectedEdgeId, (newEdgeId) => {
    if (newEdgeId) {
        selectedNodeId.value = null;
    }
});

// --- Action Palette ---
const actionPaletteDefinition = [
    { id: 'searchGroup', name: 'Search Actions', icon: Search, iconColor: 'text-blue-500', defaultOpen: true, actions: [ { id: 'webSearch', name: 'Web Search', description: 'Search online (e.g., Google Scholar).', type: 'searchAction', subType: 'web', icon: Globe, iconColor: 'text-blue-500' }, { id: 'dbSearch', name: 'Database Search', description: 'Query connected databases (e.g., JSTOR).', type: 'searchAction', subType: 'database', icon: Database, iconColor: 'text-blue-700' }, { id: 'projectDocSearch', name: 'Project Document Search', description: 'Search within existing project documents.', type: 'searchAction', subType: 'projectInternal', icon: FileSearch, iconColor: 'text-sky-600' } ] },
    { id: 'extractGroup', name: 'Extraction Actions', icon: Scissors, iconColor: 'text-orange-500', defaultOpen: true, actions: [ { id: 'extractKeywords', name: 'Extract Keywords', description: 'Identify and list key terms.', type: 'extractAction', subType: 'keywords', icon: ListFilter, iconColor: 'text-orange-500' }, { id: 'extractEntities', name: 'Extract Entities', description: 'Find people, orgs, locations.', type: 'extractAction', subType: 'entities', icon: Users, iconColor: 'text-orange-600' }, { id: 'extractSummary', name: 'Extract Summary', description: 'Generate a concise summary.', type: 'extractAction', subType: 'summary', icon: TextCursorInput, iconColor: 'text-amber-600' }, { id: 'extractDataPoints', name: 'Extract Data Points', description: 'Pull specific statistics or facts.', type: 'extractAction', subType: 'data', icon: SigmaSquare, iconColor: 'text-yellow-600' }, ] },
    { id: 'synthesizeGroup', name: 'Synthesis Actions', icon: Combine, iconColor: 'text-purple-500', defaultOpen: true, actions: [ { id: 'compareContrast', name: 'Compare & Contrast', description: 'Analyze similarities and differences.', type: 'synthesizeAction', subType: 'compare', icon: GitCompareArrows, iconColor: 'text-purple-500' }, { id: 'identifyThemes', name: 'Identify Themes', description: 'Find common patterns across texts.', type: 'synthesizeAction', subType: 'themes', icon: Brain, iconColor: 'text-purple-600' }, { id: 'buildArgument', name: 'Build Argument', description: 'Construct a reasoned argument.', type: 'synthesizeAction', subType: 'argument', icon: Scale, iconColor: 'text-violet-600' }, ] },
    { id: 'draftingGroup', name: 'Drafting Actions', icon: Edit3, iconColor: 'text-pink-500', defaultOpen: true, actions: [ { id: 'draftSection', name: 'Draft Report Section', description: 'Generate text for a report section.', type: 'draftAction', subType: 'reportSection', icon: FileSignature, iconColor: 'text-pink-500' }, { id: 'draftEmailSummary', name: 'Draft Email Summary', description: 'Compose an email summarizing findings.', type: 'draftAction', subType: 'email', icon: SendIcon, iconColor: 'text-pink-600' }, { id: 'draftPresentationOutline', name: 'Draft Presentation Outline', description: 'Create a slide outline.', type: 'draftAction', subType: 'presentation', icon: BarChart2, iconColor: 'text-rose-500' }, ] },
];
const paletteGroupOpenState = ref({});
const actionPaletteGroups = computed(() => {
    const staticGroups = actionPaletteDefinition.map(group => ({...group}));
    const customGroup = {
        id: 'customAnalysisGroup',
        name: 'User Prompts (Custom Analysis)',
        icon: FileText,
        iconColor: 'text-fuchsia-500',
        defaultOpen: true,
        actions: customAnalysisPrompts.value.map(prompt => ({
            id: `custom-${prompt.id}`,
            name: prompt.name,
            description: `Uses prompt: ${prompt.name.substring(0,25)}...`,
            type: 'customAnalysis',
            promptId: prompt.id,
            icon: AlertTriangle,
            iconColor: 'text-fuchsia-600',
            isCustom: true
        }))
    };
    return [...staticGroups, customGroup];
});
const initializePaletteGroupStates = () => { actionPaletteGroups.value.forEach(group => { if (paletteGroupOpenState.value[group.id] === undefined) { paletteGroupOpenState.value[group.id] = group.defaultOpen !== undefined ? group.defaultOpen : true; } }); };
const togglePaletteGroup = (groupId) => { if (paletteGroupOpenState.value.hasOwnProperty(groupId)) { paletteGroupOpenState.value[groupId] = !paletteGroupOpenState.value[groupId]; } else { console.warn(`Attempted to toggle uninitialized group: ${groupId}. Initializing to open.`); paletteGroupOpenState.value[groupId] = true; } };
const savedLibraryPrompts = ref([ { id: 'sp1', name: 'USF Initial Analysis', type: 'streamAnalysis', policyType: 'Telecommunications', content: 'System: You are a policy analyst...' }, { id: 'sp2', name: 'Environmental Impact Outline', type: 'streamAnalysis', policyType: 'Environment', content: 'System: You are an environmental scientist...' }, { id: 'sp3', name: 'Summarize Key Arguments', type: 'streamAnalysis', content: 'Identify and summarize the key arguments presented in the provided text regarding [topic].' }, { id: 'sp4', name: 'Identify Policy Gaps', type: 'streamAnalysis', content: 'Analyze the provided policy documents and identify potential gaps or areas for improvement.'} ]);
const customAnalysisPrompts = computed(() => savedLibraryPrompts.value.filter(p => p.type === 'streamAnalysis'));
const getPromptNameById = (promptId) => { const prompt = savedLibraryPrompts.value.find(p => p.id === promptId); return prompt ? prompt.name : 'Unknown Prompt'; };

// --- vis-network Initialization and Methods ---
const edgeModeActive = ref(false);

onMounted(() => {
  initializePaletteGroupStates();
  initializeNetwork();
  workflowNodesDataSet.on('*', () => { workflowNodes.value = workflowNodesDataSet.get(); });
  workflowEdgesDataSet.on('*', () => { workflowEdges.value = workflowEdgesDataSet.get(); });
  window.addEventListener('resize', () => { if(visNetwork) visNetwork.fit(); });
});

onBeforeUnmount(() => {
  if (visNetwork) visNetwork.destroy();
  window.removeEventListener('resize', () => { if(visNetwork) visNetwork.fit(); });
  window.removeEventListener('mousemove', handleDrag);
  window.removeEventListener('mouseup', stopDrag);
});

const generateNodeId = (action) => {
    // Sanitize action name: lowercased, spaces to hyphens, remove other special chars
    const namePart = action.name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
    // Sanitize action type
    const typePart = action.type.toLowerCase().replace(/[^a-z0-9-]/g, '');
    return `${typePart}-${namePart}-${Date.now()}`; // Appends timestamp for uniqueness
};

const initializeNetwork = () => {
  if (!networkCanvasRef.value) return;
  const data = { nodes: workflowNodesDataSet, edges: workflowEdgesDataSet };
  const options = {
    nodes: { shape: 'box', margin: 10, font: {size: 12}, widthConstraint: { minimum: 120, maximum: 200 }, color: { background: '#fff', border: '#cbd5e1', highlight: { background: '#eff6ff', border: '#60a5fa'}}},
    edges: { arrows: 'to', smooth: { type: 'cubicBezier', forceDirection: 'horizontal', roundness: 0.4 }, color: { color: '#9ca3af', highlight: '#60a5fa', hover: '#60a5fa' } },
    physics: { enabled: true, solver: 'barnesHut', barnesHut: { gravitationalConstant: -3000, centralGravity: 0.1, springLength: 150, springConstant: 0.03 }},
    interaction: { dragNodes: true, dragView: true, hover: true, zoomView: true, tooltipDelay: 200, multiselect: false },
    manipulation: {
        enabled: false,
        addEdge: addEdgeHandler,
    },
  };
  visNetwork = new Network(networkCanvasRef.value, data, options);

  visNetwork.on('click', (params) => {
    if (edgeModeActive.value) {
        console.log('Click event in edge mode. Vis-network handles edge creation. Params:', JSON.stringify(params));
        return;
    }
    if (params.nodes.length > 0) {
        selectedNodeId.value = params.nodes[0];
        selectedEdgeId.value = null;
    } else if (params.edges.length > 0) {
        selectedEdgeId.value = params.edges[0];
        selectedNodeId.value = null;
    } else {
        selectedNodeId.value = null;
        selectedEdgeId.value = null;
    }
  });
};

const addEdgeHandler = (edgeData, callback) => {
    console.log("addEdgeHandler called with edgeData:", JSON.stringify(edgeData));
    if (edgeData.from && edgeData.to) {
        if (edgeData.from !== edgeData.to) {
            const newEdge = { from: edgeData.from, to: edgeData.to, id: `edge-${Date.now()}` };
            workflowEdgesDataSet.add(newEdge);
            callback(newEdge);
            console.log("Edge added:", newEdge);
        } else {
            callback(null);
            console.log("Edge creation cancelled: Self-loop attempted. From:", edgeData.from, "To:", edgeData.to);
        }
    } else {
        callback(null);
        console.log("Edge creation cancelled: 'from' or 'to' node is missing or process was cancelled by user. From:", edgeData.from, "To:", edgeData.to);
    }
    if (visNetwork) { visNetwork.disableEditMode(); }
    edgeModeActive.value = false;
    console.log("Edge mode deactivated by addEdgeHandler.");
};


const toggleEdgeMode = () => {
    if (!visNetwork) return;
    if (edgeModeActive.value) {
        visNetwork.disableEditMode();
        edgeModeActive.value = false;
        console.log("Edge mode deactivated by toggle button.");
    } else {
        visNetwork.addEdgeMode();
        edgeModeActive.value = true;
        selectedNodeId.value = null;
        selectedEdgeId.value = null;
        console.log("Edge mode activated. Click a source node, then a target node.");
    }
};

const handleDragStart = (event, action) => {
  draggedAction.value = action;
  event.dataTransfer.effectAllowed = 'copy';
  event.dataTransfer.setData('application/json', JSON.stringify(action));
};

const handleDragOver = (event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'copy';
};

const handleDrop = (event) => {
  event.preventDefault();
  if (!draggedAction.value || !visNetwork || !networkCanvasRef.value) return;

  const canvasRect = networkCanvasRef.value.getBoundingClientRect();
  const position = visNetwork.DOMtoCanvas({
    x: event.clientX - canvasRect.left,
    y: event.clientY - canvasRect.top
  });

  const newNode = {
    id: generateNodeId(draggedAction.value),
    label: draggedAction.value.name,
    x: position.x,
    y: position.y,
    actionType: draggedAction.value.type,
    subType: draggedAction.value.subType || null,
    iconName: typeof draggedAction.value.icon === 'string' ? draggedAction.value.icon : draggedAction.value.icon?.name,
    promptId: draggedAction.value.isCustom ? draggedAction.value.promptId : null,
  };
  workflowNodesDataSet.add(newNode);
  draggedAction.value = null;
};

const updateNodeLabel = () => {
    if (selectedNodeId.value && visNetwork) {
        workflowNodesDataSet.update({ id: selectedNodeId.value, label: editableNodeLabel.value });
    }
};

const deleteSelectedNode = () => {
    if (selectedNodeId.value && visNetwork) {
        workflowNodesDataSet.remove(selectedNodeId.value);
        selectedNodeId.value = null;
    }
};

const deleteSelectedEdge = () => {
    if (selectedEdgeId.value && visNetwork) {
        workflowEdgesDataSet.remove(selectedEdgeId.value);
        selectedEdgeId.value = null;
    }
};

const saveWorkflow = () => {
    console.log('Saving workflow:', {
        name: workflowName.value,
        nodes: workflowNodesDataSet.get({ fields: ['id', 'label', 'x', 'y', 'actionType', 'subType', 'promptId', 'iconName'] }), // Added iconName
        edges: workflowEdgesDataSet.get({ fields: ['id', 'from', 'to'] })
    });
    alert(`Workflow "${workflowName.value}" saved (mock)!`);
};
const showExportModal = ref(false);
const toggleExportModal = () => showExportModal.value = !showExportModal.value;

const exportToMermaid = () => {
  let mermaidString = 'graph TD;\n';
  const nodes = workflowNodesDataSet.get(); // Get all node data
  const edges = workflowEdgesDataSet.get();

  nodes.forEach(node => {
    // Sanitize ID for Mermaid: replace hyphens and non-alphanumeric (except underscore)
    const nodeId = node.id.replace(/-/g, '_').replace(/[^a-zA-Z0-9_]/g, '');
    // Escape quotes in label
    const nodeLabel = node.label.replace(/"/g, '#quot;');
    // Include action type and subtype in the label for clarity
    const typeInfo = node.actionType + (node.subType ? `-${node.subType}` : '');
    mermaidString += `    ${nodeId}["${nodeLabel} (${typeInfo})"];\n`;
  });

  edges.forEach(edge => {
    const fromNodeId = edge.from.replace(/-/g, '_').replace(/[^a-zA-Z0-9_]/g, '');
    const toNodeId = edge.to.replace(/-/g, '_').replace(/[^a-zA-Z0-9_]/g, '');
    mermaidString += `    ${fromNodeId} --> ${toNodeId};\n`;
  });

  navigator.clipboard.writeText(mermaidString)
    .then(() => { alert('Mermaid diagram syntax copied to clipboard!'); })
    .catch(err => {
        alert('Failed to copy Mermaid syntax. See console for details.');
        console.error('Failed to copy Mermaid syntax: ', err);
    });
  toggleExportModal();
};

const exportToJSON = () => {
  const jsonData = JSON.stringify({
      name: workflowName.value,
      nodes: workflowNodesDataSet.get({fields: ['id', 'label', 'x', 'y', 'actionType', 'subType', 'promptId', 'iconName']}), // Added iconName
      edges: workflowEdgesDataSet.get({fields: ['id', 'from', 'to']})
  }, null, 2);
  const blob = new Blob([jsonData], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = `${workflowName.value.replace(/\s+/g, '_') || 'workflow'}.json`;
  document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(url);
  alert('Workflow JSON exported!'); toggleExportModal();
};

const startResize = (event, resizer) => { /* ... same as before ... */ };
const handleDrag = (event) => { /* ... same as before ... */ };
const stopDrag = () => { /* ... same as before ... */ };

</script>

<style scoped>
.input-base { @apply block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm; }
.btn { @apply py-2 px-4 rounded-md font-semibold shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors; }
.btn-success { @apply bg-green-500 text-white hover:bg-green-600 focus:ring-green-400; }
.btn-secondary { @apply bg-gray-500 text-white hover:bg-gray-600 focus:ring-gray-400; }
.btn-primary { @apply bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500; }
.btn-danger { @apply bg-red-500 text-white hover:bg-red-600 focus:ring-red-400; }
.btn-sm { @apply text-xs !py-1 !px-2; }

.max-h-72::-webkit-scrollbar, .max-h-96::-webkit-scrollbar, .max-h-60::-webkit-scrollbar { width: 6px; }
.max-h-72::-webkit-scrollbar-thumb, .max-h-96::-webkit-scrollbar-thumb, .max-h-60::-webkit-scrollbar-thumb { background-color: #cbd5e1; border-radius: 10px; }
.max-h-72::-webkit-scrollbar-track, .max-h-96::-webkit-scrollbar-track, .max-h-60::-webkit-scrollbar-track { background-color: #f1f5f9; }
.select-none { user-select: none; }
.flex-shrink-0 { flex-shrink: 0; }
.flex-1.overflow-hidden { height: calc(100vh - 4rem); }
.sticky { position: -webkit-sticky; position: sticky; }
.bg-dots { background-image: radial-gradient(circle, #e0e0e0 1px, transparent 1px); background-size: 15px 15px; }
.rotate-180 { transform: rotate(180deg); }
</style>