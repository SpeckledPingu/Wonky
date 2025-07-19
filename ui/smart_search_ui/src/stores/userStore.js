import { defineStore } from 'pinia';
import { ref } from 'vue';

// Define the store for user-related data
export const useUserStore = defineStore('user', () => {
  // State
  const userId = ref(null); // To be populated on app load, e.g., from a token
  const isLoggedIn = ref(false);

  // Actions
  /**
   * Simulates fetching and setting the user ID.
   * In a real app, this would involve an API call and authentication.
   * @param {string} id - The user's unique identifier.
   */
  function setUser(id) {
    userId.value = id;
    isLoggedIn.value = !!id;
    console.log(`User session started for ID: ${id}`);
  }

  /**
   * Simulates user logout.
   */
  function clearUser() {
    userId.value = null;
    isLoggedIn.value = false;
    console.log('User session cleared.');
  }

  // Initialize with a mock user for demonstration
  // In a production app, you would likely have an initialization action
  // that checks for a session token.
  setUser('testuser');

  return {
    userId,
    isLoggedIn,
    setUser,
    clearUser,
  };
});
