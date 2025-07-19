<template>
  <div
    class="w-1.5 cursor-col-resize bg-gray-300 hover:bg-blue-500 transition-colors duration-200 ease-in-out flex-shrink-0"
    @mousedown="startDrag"
  ></div>
</template>

<script setup>
import { defineEmits } from 'vue';

const emit = defineEmits(['drag']);

// This function is called when the user clicks down on the handle
const startDrag = (event) => {
  // Prevent default browser behavior, like text selection
  event.preventDefault();

  // Function to handle mouse movement
  const doDrag = (e) => {
    // Emit the 'drag' event with the horizontal movement value
    emit('drag', e.movementX);
  };

  // Function to stop dragging when the mouse button is released
  const stopDrag = () => {
    // Remove the event listeners from the window to stop tracking mouse movement
    window.removeEventListener('mousemove', doDrag);
    window.removeEventListener('mouseup', stopDrag);
  };

  // Add event listeners to the window to track mouse movement and release
  window.addEventListener('mousemove', doDrag);
  window.addEventListener('mouseup', stopDrag);
};
</script>

<style scoped>
/* Scoped styles for the resizable handle */
.w-1\.5 {
  flex-basis: 6px;
}
</style>
