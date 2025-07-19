<template>
  <div class="fixed top-4 right-4 z-50 w-full max-w-sm space-y-3">
    <transition-group name="list">
      <div
        v-for="notification in notificationStore.notifications"
        :key="notification.id"
        :class="['p-4 rounded-lg shadow-lg text-white flex justify-between items-center', colorClasses[notification.type]]"
      >
        <span>{{ notification.message }}</span>
        <button @click="notificationStore.removeNotification(notification.id)" class="ml-4 opacity-70 hover:opacity-100">&times;</button>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { useNotificationStore } from '../../stores/notificationStore';

const notificationStore = useNotificationStore();

const colorClasses = {
  success: 'bg-green-500',
  error: 'bg-red-500',
  warning: 'bg-yellow-500',
  info: 'bg-blue-500',
};
</script>

<style scoped>
.list-enter-active,
.list-leave-active {
  transition: all 0.5s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
