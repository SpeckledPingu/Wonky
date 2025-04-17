<script setup>
import { ref, computed, watch } from 'vue';

// --- Vue Flow Imports ---
import { VueFlow, useVueFlow } from '@vue-flow/core';
import { Controls } from '@vue-flow/controls';
import { MiniMap } from '@vue-flow/minimap';
// Import Vue Flow styles
import '@vue-flow/core/dist/style.css';
import '@vue-flow/core/dist/theme-default.css';
import '@vue-flow/controls/dist/style.css';
import '@vue-flow/minimap/dist/style.css';

// --- Component Emits & State ---
const emit = defineEmits(['selection-changed']);
const viewMode = ref('list');

// Placeholder data
const projectFiles = ref([
  { id: 1, name: 'Advancing Circularity with Bioplastics.pdf', type: 'file', path: '/docs/advancing_circ.pdf' },
  { id: 2, name: 'Bioplastics Production Properties.docx', type: 'file', path: '/docs/prod_props.docx' },
  { id: 3, name: 'Research Data', type: 'folder', children: [
    { id: 31, name: 'Agro-food Waste Analysis.csv', type: 'file', path: '/data/agro_waste.csv' },
    { id: 32, name: 'Wikipedia Scrape.json', type: 'file', path: '/data/wiki.json' },
    { id: 33, name: 'Sub Analysis', type: 'folder', children: [
        { id: 331, name: 'Toxicity Report.pdf', type: 'file', path: '/data/sub/toxicity.pdf' }
      ], isExpanded: false }
    ], isExpanded: true },
  { id: 4, name: 'Characterization BioPlastic.md', type: 'file', path: '/notes/char_bio.md' },
  { id: 5, name: 'Challenges & Strategies.txt', type: 'file', path: '/notes/challenges.txt' },
  { id: 6, name: 'Archived Docs', type: 'folder', children: [], isExpanded: false },
]);

// --- Shared Selection State ---
const selectedFileIds = ref(new Set());

// --- Vue Flow State & Logic ---
const { fitView } = useVueFlow();
const flowNodes = ref([]);
const flowEdges = ref([]);
const expandedGraphNodes = ref(new Set());

// --- Helper Functions ---

/** Recursively finds a node by ID */
function findNodeById(id, nodes = projectFiles.value) {
    for (const node of nodes) {
        if (node.id === id) return node;
        if (node.type === 'folder' && node.children) {
            const found = findNodeById(id, node.children);
            if (found) return found;
        }
    }
    return null;
}

/** Recursively gets all file IDs from the data structure */
function getAllFileIds(nodes = projectFiles.value) {
    let ids = [];
    nodes.forEach(node => {
        if (node.type === 'file') {
            ids.push(node.id);
        } else if (node.type === 'folder' && node.children) {
            ids = ids.concat(getAllFileIds(node.children));
        }
    });
    return ids;
}

/** Emits the selection change event */
function emitSelectionChange() {
    const selectedFiles = [];
    selectedFileIds.value.forEach(id => {
        const fileNode = findNodeById(id);
        if (fileNode && fileNode.type === 'file') {
            selectedFiles.push(fileNode);
        }
    });
    console.log('Selection changed:', selectedFiles.map(f => f.name));
    emit('selection-changed', selectedFiles);
}

/** Toggles selection for a single file ID */
function toggleFileSelection(fileId) {
    if (selectedFileIds.value.has(fileId)) {
        selectedFileIds.value.delete(fileId);
    } else {
        selectedFileIds.value.add(fileId);
    }
    emitSelectionChange();
}

// --- Select All / Deselect All ---

/** Selects all files */
function selectAllFiles() {
    const allIds = getAllFileIds();
    selectedFileIds.value = new Set(allIds); // Replace the set with a new one containing all IDs
    emitSelectionChange();
    // Update graph view if active
    if (viewMode.value === 'graph') {
        transformDataForFlow();
    }
}

/** Deselects all files */
function deselectAllFiles() {
    if (selectedFileIds.value.size > 0) { // Only act if there's something selected
        selectedFileIds.value.clear(); // Clear the existing set
        // Or: selectedFileIds.value = new Set();
        emitSelectionChange();
        // Update graph view if active
        if (viewMode.value === 'graph') {
            transformDataForFlow();
        }
    }
}


// --- Vue Flow Methods ---

function transformDataForFlow() {
    // (Implementation unchanged from previous version - reads selectedFileIds)
    const newNodes = [];
    const newEdges = [];
    let yOffset = 0;

    function processNode(node, level = 0, parentId = null) {
        const nodeId = String(node.id);
        const isGraphExpanded = node.type === 'folder' && expandedGraphNodes.value.has(nodeId);
        const isSelected = node.type === 'file' && selectedFileIds.value.has(node.id); // Read from shared state
        const xPos = level * 250;

        newNodes.push({
            id: nodeId,
            label: node.type === 'folder'
                   ? `${node.name} ${node.children?.length > 0 ? (isGraphExpanded ? '[-]' : '[+]') : ''}`
                   : node.name,
            position: { x: xPos, y: yOffset },
            type: 'default',
            data: {
                originalId: node.id, type: node.type, path: node.path,
                isFolder: node.type === 'folder', hasChildren: node.children && node.children.length > 0,
            },
            class: `${node.type === 'folder' ? 'flow-folder-node' : 'flow-file-node'} ${isSelected ? 'selected-graph-node' : ''}`, // Apply selection class
            style: node.type === 'folder' ? { backgroundColor: '#e9ecef', borderColor: '#adb5bd', width: 'auto', minWidth: '180px' } : {width: 'auto', minWidth: '180px'}
        });
        yOffset += 80;

        if (parentId !== null) {
            newEdges.push({ id: `e-${parentId}-${nodeId}`, source: String(parentId), target: nodeId, type: 'smoothstep' });
        }

        if (node.type === 'folder' && node.children?.length > 0 && isGraphExpanded) {
            yOffset += 20;
            node.children.forEach(child => processNode(child, level + 1, node.id));
            yOffset += 20;
        }
    }

    projectFiles.value.forEach(rootNode => { processNode(rootNode); yOffset += 40; });
    flowNodes.value = newNodes;
    flowEdges.value = newEdges;
    setTimeout(() => { if (viewMode.value === 'graph') fitView({ duration: 300, padding: 0.1 }); }, 100);
}

function onNodeClick(eventData) {
    // (Implementation unchanged - calls toggleFileSelection or handles folder expansion)
    const node = eventData.node;
    const originalId = node.data?.originalId;
    if (!originalId) return;
    if (node.data && !node.data.isFolder) {
        toggleFileSelection(originalId);
        transformDataForFlow(); // Update graph style immediately
    } else if (node.data && node.data.isFolder && node.data.hasChildren) {
        const nodeIdStr = node.id;
        if (expandedGraphNodes.value.has(nodeIdStr)) expandedGraphNodes.value.delete(nodeIdStr);
        else expandedGraphNodes.value.add(nodeIdStr);
        transformDataForFlow(); // Update graph structure
    }
}


// --- List View Methods ---

function handleListItemClick(node, isCheckboxClick = false) {
    // (Implementation unchanged - calls toggleFileSelection or toggleListFolderExpansion)
     if (node.type === 'file') {
      toggleFileSelection(node.id);
    } else if (node.type === 'folder' && !isCheckboxClick) {
      toggleListFolderExpansion(node);
    }
}

function toggleListFolderExpansion(folder) { // List view specific
  folder.isExpanded = !folder.isExpanded;
}

function renderNodeForList(node, level = 0) { // List view specific
  const indentStyle = { paddingLeft: `${level * 20}px` };
  const isSelected = node.type === 'file' && selectedFileIds.value.has(node.id); // Read from shared state
  return { node, indentStyle, level, isSelected };
}

function getRenderableNodesForList(nodes, level = 0, parentIsExpanded = true) { // List view specific
    // (Implementation unchanged - uses renderNodeForList)
    let result = [];
    if (!parentIsExpanded) return result;
    nodes.forEach(node => {
        result.push(renderNodeForList(node, level));
        if (node.type === 'folder' && node.children && node.children.length > 0) {
            result = result.concat(getRenderableNodesForList(node.children, level + 1, node.isExpanded));
        }
    });
    return result;
}

// --- Watchers ---
watch(viewMode, (newMode) => { if (newMode === 'graph') transformDataForFlow(); }, { immediate: true });
watch(selectedFileIds, () => { if (viewMode.value === 'graph') transformDataForFlow(); }, { deep: true });

</script>

<template>
  <div class="file-explorer">
    <div class="panel-header">
        <h3>Sources</h3>
        <div class="view-toggle">
            <button @click="viewMode = 'list'" :class="{ active: viewMode === 'list' }">List</button>
            <button @click="viewMode = 'graph'" :class="{ active: viewMode === 'graph' }">Graph</button>
        </div>
    </div>

    <div class="action-buttons">
        <button>+ Add</button>
        <button>Discover</button>
        <button @click="selectAllFiles" title="Select All Files">Select All</button>
        <button @click="deselectAllFiles" title="Deselect All Files">Deselect All</button>
    </div>

    <div v-if="viewMode === 'list'" class="view-container list-view-container">
        <ul class="file-list">
          <li
            v-for="{ node, indentStyle, isSelected } in getRenderableNodesForList(projectFiles)"
            :key="`list-${node.id}`"
            :class="{ 'file-item': true, 'folder': node.type === 'folder', 'selected': isSelected }"
            :style="indentStyle"
            @click="handleListItemClick(node, false)"
          >
            <span v-if="node.type === 'folder'" class="icon folder-icon" @click.stop="toggleListFolderExpansion(node)">
              {{ node.isExpanded ? '📂' : '📁' }}
            </span>
            <input
                v-else
                type="checkbox"
                :checked="isSelected"
                @click.stop="handleListItemClick(node, true)"
                class="select-checkbox-list"
            />
            <span class="node-name">{{ node.name }}</span>
          </li>
        </ul>
    </div>

    <div v-else-if="viewMode === 'graph'" class="view-container graph-view-container">
        <VueFlow
            :nodes="flowNodes"
            :edges="flowEdges"
            @node-click="onNodeClick"
            :fit-view-on-init="true"
            :min-zoom="0.1" :max-zoom="2"
            class="flow-canvas"
            :nodes-draggable="true" :select-nodes-on-drag="true"
        >
            <Controls />
            <MiniMap />
        </VueFlow>
    </div>

  </div>
</template>

<style> /* Non-scoped for Vue Flow */

/* General Explorer Styles */
.file-explorer { padding: 0; height: 100%; display: flex; flex-direction: column; }
.panel-header { display: flex; justify-content: space-between; align-items: center; padding: 0 15px; border-bottom: 1px solid #eee; flex-shrink: 0; }
.panel-header h3 { margin: 0; padding: 15px 0; border-bottom: none; font-size: 1.1em; color: #333; }
.view-toggle button { padding: 5px 10px; margin-left: 5px; cursor: pointer; background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; font-size: 0.85em; }
.view-toggle button.active { background-color: #007bff; color: white; border-color: #007bff; }
.view-toggle button:not(.active):hover { background-color: #e9ecef; }
.action-buttons { padding: 10px 15px; border-bottom: 1px solid #eee; display: flex; flex-wrap: wrap; gap: 10px; flex-shrink: 0; } /* Added flex-wrap */
.action-buttons button { padding: 5px 10px; cursor: pointer; background-color: #e9ecef; border: 1px solid #ced4da; border-radius: 4px; font-size: 0.9em; }
.action-buttons button:hover { background-color: #dee2e6; }
.view-container { flex-grow: 1; overflow: hidden; position: relative; }
.list-view-container { overflow-y: auto; }

/* List View Styles */
.file-list { list-style: none; padding: 10px 0; margin: 0; }
.file-item { padding: 8px 15px; cursor: pointer; display: flex; align-items: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; border-bottom: 1px solid #f8f9fa; font-size: 0.95em; }
.file-item:hover { background-color: #e9ecef; }
.file-item.selected { background-color: #dbeafe !important; font-weight: 500; }
.icon { margin-right: 8px; display: inline-block; width: 20px; text-align: center; flex-shrink: 0; }
.folder-icon { cursor: pointer; }
.select-checkbox-list { margin-right: 8px; cursor: pointer; width: 16px; height: 16px; flex-shrink: 0; }
.node-name { flex-grow: 1; overflow: hidden; text-overflow: ellipsis; margin-right: 10px; }


/* Graph View Styles */
.graph-view-container { height: 100%; width: 100%; }
.flow-canvas { height: 100%; width: 100%; background-color: #f8f9fa; }

/* Vue Flow Node Styles */
.vue-flow__node { border-radius: 6px; font-size: 12px; border: 1px solid #adb5bd; padding: 8px 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); background-color: #fff; color: #333; transition: box-shadow 0.2s ease, border-color 0.2s ease, background-color 0.2s ease; width: auto !important; min-width: 180px; text-align: center; white-space: nowrap; cursor: default; }
.vue-flow__node:hover { box-shadow: 0 4px 8px rgba(0,0,0,0.15); }
.vue-flow__node.flow-folder-node { background-color: #e9ecef; border-color: #adb5bd; font-weight: 500; }
.vue-flow__node.flow-folder-node[data-has-children="true"] { cursor: pointer; }
.vue-flow__node.flow-file-node { background-color: #ffffff; border-color: #007bff; cursor: pointer; }
.vue-flow__node.selected-graph-node { border-color: #fd7e14; background-color: #fff3e0; box-shadow: 0 0 0 2px rgba(253, 126, 20, 0.5); }

/* Edge Styles */
.vue-flow__edge-path { stroke: #adb5bd; stroke-width: 1.5; }
.vue-flow__controls { box-shadow: 0 1px 3px rgba(0,0,0,0.2); }
.vue-flow__minimap { box-shadow: 0 1px 3px rgba(0,0,0,0.2); }

</style>
