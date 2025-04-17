<script setup>
import { ref, computed, onUnmounted } from 'vue'; // Added computed
import FileExplorer from './components/FileExplorer.vue';
import ChatInterface from './components/ChatInterface.vue';
import ActionsPanel from './components/ActionsPanel.vue';

// --- State ---
// Changed from selectedDocument (single object) to selectedDocuments (array)
const selectedDocuments = ref([]); // Initialize as an empty array

// --- Computed Property for Chat Context ---
// Provides a single document to the chat interface only if exactly one is selected.
const chatContextDocument = computed(() => {
  return selectedDocuments.value.length === 1 ? selectedDocuments.value[0] : null;
});

// --- Panel Resizing State (Unchanged) ---
const panelWidths = ref({ left: 25, middle: 50, right: 25 });
const minPanelWidth = 15;
const isDragging = ref(false);
const activeDivider = ref(null);
const startX = ref(0);
const startLeftWidth = ref(0);
const startMiddleWidth = ref(0);
const startRightWidth = ref(0);
const leftPanelRef = ref(null);
const middlePanelRef = ref(null);
const rightPanelRef = ref(null);


// --- Methods ---

/**
 * Handles the 'selection-changed' event emitted by FileExplorer.
 * Updates the selectedDocuments state with the array of selected file objects.
 * @param {Array<object>} files - The array of file objects currently selected.
 */
function handleSelectionChange(files) {
  console.log('Selection changed in App.vue:', files.map(f => f.name));
  selectedDocuments.value = files; // Update state with the received array
}

/**
 * Handles actions triggered from the ActionsPanel.
 * Now acknowledges that actions might apply to multiple documents.
 * @param {string} actionName - The name of the action triggered.
 */
function handleAction(actionName) {
    const docNames = selectedDocuments.value.map(doc => doc.name).join(', ');
    const message = selectedDocuments.value.length > 0
        ? `Action "${actionName}" triggered for document(s): ${docNames}.`
        : `Action "${actionName}" triggered (no documents selected).`;

    console.log('Action triggered:', actionName, 'Selected Docs:', selectedDocuments.value);
    // TODO: Implement logic based on the action (e.g., call backend with selectedDocuments array)
    alert(`${message} Implement backend call here.`);
}


// --- Panel Resizing Methods (Unchanged) ---

function startDrag(event, divider) {
  isDragging.value = true;
  activeDivider.value = divider;
  startX.value = event.clientX;
  startLeftWidth.value = panelWidths.value.left;
  startMiddleWidth.value = panelWidths.value.middle;
  startRightWidth.value = panelWidths.value.right;
  window.addEventListener('mousemove', doDrag);
  window.addEventListener('mouseup', stopDrag);
  document.body.style.userSelect = 'none';
  document.body.style.cursor = 'col-resize';
}

function doDrag(event) {
  if (!isDragging.value) return;
  const currentX = event.clientX;
  const deltaX = currentX - startX.value;
  const deltaPercent = (deltaX / window.innerWidth) * 100;

  let newLeftWidth = startLeftWidth.value;
  let newMiddleWidth = startMiddleWidth.value;
  let newRightWidth = startRightWidth.value;

  if (activeDivider.value === 'left') {
    newLeftWidth = startLeftWidth.value + deltaPercent;
    newMiddleWidth = startMiddleWidth.value - deltaPercent;
    if (newLeftWidth < minPanelWidth) { newMiddleWidth -= (minPanelWidth - newLeftWidth); newLeftWidth = minPanelWidth; }
    if (newMiddleWidth < minPanelWidth) { newLeftWidth -= (minPanelWidth - newMiddleWidth); newMiddleWidth = minPanelWidth; }
  } else if (activeDivider.value === 'right') {
    newMiddleWidth = startMiddleWidth.value + deltaPercent;
    newRightWidth = startRightWidth.value - deltaPercent;
    if (newMiddleWidth < minPanelWidth) { newRightWidth -= (minPanelWidth - newMiddleWidth); newMiddleWidth = minPanelWidth; }
    if (newRightWidth < minPanelWidth) { newMiddleWidth -= (minPanelWidth - newRightWidth); newRightWidth = minPanelWidth; }
  }

  const totalWidth = newLeftWidth + newMiddleWidth + newRightWidth;
  if (Math.abs(totalWidth - 100) > 0.1) {
      if (activeDivider.value === 'left') newRightWidth = 100 - newLeftWidth - newMiddleWidth;
      else newLeftWidth = 100 - newMiddleWidth - newRightWidth;
  }
   if (newLeftWidth < minPanelWidth) newLeftWidth = minPanelWidth;
   if (newMiddleWidth < minPanelWidth) newMiddleWidth = minPanelWidth;
   if (newRightWidth < minPanelWidth) newRightWidth = minPanelWidth;
   const finalTotal = newLeftWidth + newMiddleWidth + newRightWidth;
   if (Math.abs(finalTotal - 100) > 0.1) {
       if (activeDivider.value === 'left') newMiddleWidth = 100 - newLeftWidth - newRightWidth;
       else newMiddleWidth = 100 - newLeftWidth - newRightWidth;
       if (newMiddleWidth < minPanelWidth) newMiddleWidth = minPanelWidth;
       if (activeDivider.value === 'left') newLeftWidth = 100 - newMiddleWidth - newRightWidth;
       else newRightWidth = 100 - newLeftWidth - newMiddleWidth;
   }

  panelWidths.value = {
    left: Math.max(minPanelWidth, newLeftWidth),
    middle: Math.max(minPanelWidth, newMiddleWidth),
    right: Math.max(minPanelWidth, newRightWidth),
  };
}

function stopDrag() {
  if (isDragging.value) {
    isDragging.value = false;
    activeDivider.value = null;
    window.removeEventListener('mousemove', doDrag);
    window.removeEventListener('mouseup', stopDrag);
    document.body.style.userSelect = '';
    document.body.style.cursor = '';
  }
}

// --- Lifecycle Hooks ---
onUnmounted(() => {
  stopDrag();
});

</script>

<template>
  <div class="app-container">

    <div
      ref="leftPanelRef"
      class="panel file-explorer-panel"
      :style="{ flexBasis: panelWidths.left + '%' }"
    >
      <FileExplorer @selection-changed="handleSelectionChange" />
    </div>

    <div
      class="divider"
      @mousedown="startDrag($event, 'left')"
    ></div>

    <div
      ref="middlePanelRef"
      class="panel chat-panel"
      :style="{ flexBasis: panelWidths.middle + '%' }"
    >
      <ChatInterface :selected-document="chatContextDocument" />
    </div>

    <div
      class="divider"
      @mousedown="startDrag($event, 'right')"
    ></div>

    <div
      ref="rightPanelRef"
      class="panel actions-panel"
      :style="{ flexBasis: panelWidths.right + '%' }"
    >
      <ActionsPanel @action-triggered="handleAction" />
    </div>

  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  background-color: #f8f9fa;
  font-family: sans-serif;
  overflow: hidden;
}

.panel {
  height: 100%;
  overflow-y: auto;
  background-color: #ffffff;
  box-sizing: border-box;
  flex-grow: 0;
  flex-shrink: 0;
   min-width: 50px;
   position: relative;
}

.file-explorer-panel { }
.chat-panel { display: flex; flex-direction: column; }
.actions-panel { }

.divider {
  width: 6px;
  background-color: #dee2e6;
  cursor: col-resize;
  flex-shrink: 0;
  position: relative;
  z-index: 10;
  transition: background-color 0.2s ease;
}
.divider:hover { background-color: #adb5bd; }

h1, h2, h3 { margin-top: 0; padding: 15px; border-bottom: 1px solid #eee; }
</style>
