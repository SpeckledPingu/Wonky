<template>
  <div class="flex h-screen w-screen bg-gray-100 text-gray-800">
    <!-- Left Pane -->
    <div
      :style="{ width: leftPaneWidth + 'px' }"
      class="h-full flex-shrink-0 bg-white shadow-md"
    >
      <LeftPane />
    </div>

    <!-- Resizable Handle -->
    <ResizableHandle @drag="handleDrag" />

    <!-- Right Pane -->
    <div class="flex-grow h-full bg-gray-50">
      <RightPane />
    </div>

    <!-- Notification Area -->
    <NotificationArea />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'; // <-- IMPORTED onMounted
import LeftPane from './components/LeftPane.vue';
import RightPane from './components/RightPane.vue';
import ResizableHandle from './components/ResizableHandle.vue';
import NotificationArea from './components/common/NotificationArea.vue';
import { useProjectStore } from './stores/projectStore'; // <-- IMPORTED project store

const leftPaneWidth = ref(window.innerWidth * 0.35);

const handleDrag = (movementX) => {
  const newWidth = leftPaneWidth.value + movementX;
  const minWidth = 300;
  const maxWidth = window.innerWidth * 0.7;

  if (newWidth > minWidth && newWidth < maxWidth) {
    leftPaneWidth.value = newWidth;
  }
};

// --- FIX ---
// This ensures that the project list is fetched as soon as the application is mounted.
// This is the most reliable way to trigger the initial data load.
onMounted(() => {
  const projectStore = useProjectStore();
  projectStore.fetchProjects();
});
</script>
