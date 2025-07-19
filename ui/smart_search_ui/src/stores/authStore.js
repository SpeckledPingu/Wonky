import { defineStore } from 'pinia';
import { ref } from 'vue';
import { authService } from '../services/api';
import { useProjectStore } from './projectStore';
import { useDocumentStore } from './documentStore';
import { useProcessingStore } from './processingStore';
import { useReportsStore } from './reportsStore';
import { useSearchStore } from './searchStore';

export const useAuthStore = defineStore('auth', () => {
    // State
    const user = ref(null);
    const token = ref(localStorage.getItem('authToken') || null);
    const isAuthenticated = ref(false);

    // Actions
    async function login(email, password) {
        try {
            const response = await authService.login(email, password);
            token.value = response.access_token;
            localStorage.setItem('authToken', token.value);
            await fetchUser();
            return true;
        } catch (error) {
            console.error("Login failed:", error);
            return false;
        }
    }

    async function register(username, email, password) {
        try {
            await authService.register(username, email, password);
            return true;
        } catch (error) {
            console.error("Registration failed:", error);
            return false;
        }
    }

    async function fetchUser() {
        if (!token.value) {
            isAuthenticated.value = false;
            return;
        };
        try {
            // In a real app, this would be a '/users/me' endpoint.
            user.value = { email: 'user@example.com', id: 1 };
            isAuthenticated.value = true;
        } catch (error) {
            console.error("Failed to fetch user:", error);
            logout();
        }
    }

    function logout() {
        // --- FIX: Call the correctly named clear function for each store ---
        const projectStore = useProjectStore();
        const documentStore = useDocumentStore();
        const processingStore = useProcessingStore();
        const reportsStore = useReportsStore();
        const searchStore = useSearchStore();

        projectStore.clearProjectState();
        documentStore.clearState();
        processingStore.clearState(); // This function will be added
        reportsStore.clearState();   // This function will be added
        searchStore.clearSearchState();

        // Clear auth state last
        user.value = null;
        token.value = null;
        isAuthenticated.value = false;
        localStorage.removeItem('authToken');
    }

    fetchUser();

    return {
        user,
        token,
        isAuthenticated,
        login,
        register,
        logout,
    };
});
