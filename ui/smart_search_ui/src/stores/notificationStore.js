import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useNotificationStore = defineStore('notifications', () => {
    // State
    const notifications = ref([]);
    let nextId = 0;

    // Actions
    /**
     * Adds a new notification to the list.
     * @param {object} notification - The notification object.
     * @param {string} notification.message - The message to display.
     * @param {string} [notification.type='info'] - The type ('success', 'error', 'warning', 'info').
     * @param {number} [notification.duration=4000] - Duration in ms before auto-closing.
     */
    function addNotification({ message, type = 'info', duration = 4000 }) {
        const id = nextId++;
        notifications.value.push({ id, message, type });

        setTimeout(() => {
            removeNotification(id);
        }, duration);
    }

    /**
     * Removes a notification by its ID.
     * @param {number} id - The ID of the notification to remove.
     */
    function removeNotification(id) {
        const index = notifications.value.findIndex(n => n.id === id);
        if (index > -1) {
            notifications.value.splice(index, 1);
        }
    }

    return {
        notifications,
        addNotification,
        removeNotification,
    };
});
