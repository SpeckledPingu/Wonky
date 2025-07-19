<template>
  <div class="flex h-screen w-screen bg-gray-100 text-gray-800">
    <div :style="{ width: leftPaneWidth + 'px' }" class="h-full flex-shrink-0 bg-white shadow-md">
      <LeftPane />
    </div>
    <ResizableHandle @drag="handleDrag" />
    <div class="flex-grow h-full bg-gray-50">
      <RightPane />
    </div>
    <NotificationArea />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import LeftPane from './components/LeftPane.vue';
import RightPane from './components/RightPane.vue';
import ResizableHandle from './components/ResizableHandle.vue';
import NotificationArea from './components/common/NotificationArea.vue';

const leftPaneWidth = ref(window.innerWidth * 0.35);

const handleDrag = (movementX) => {
  const newWidth = leftPaneWidth.value + movementX;
  const minWidth = 300;
  const maxWidth = window.innerWidth * 0.7;
  if (newWidth > minWidth && newWidth < maxWidth) {
    leftPaneWidth.value = newWidth;
  }
};
</script>
