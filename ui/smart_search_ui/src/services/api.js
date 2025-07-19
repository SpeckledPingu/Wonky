import { useAuthStore } from '../stores/authStore';
import { useNotificationStore } from '../stores/notificationStore';

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

async function apiRequest(endpoint, options = {}) {
    const notificationStore = useNotificationStore();
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }

        if (response.status === 204 || response.headers.get("content-length") === "0") {
            return { success: true };
        }

        return await response.json();
    } catch (error) {
        console.error('API Request Error:', error);
        notificationStore.addNotification({ message: `API Error: ${error.message}`, type: 'error' });
        throw error;
    }
}

async function authRequest(endpoint, options = {}) {
    const authStore = useAuthStore();
    if (!authStore.token) {
        throw new Error("Authentication token not found.");
    }

    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${authStore.token}`,
    };

    return apiRequest(endpoint, { ...options, headers });
}

export const authService = {
    login: (email, password) => {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        return apiRequest('/users/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData,
        });
    },
    register: (username, email, password) => apiRequest('/users/register', {
        method: 'POST',
        body: JSON.stringify({ username, email, password }),
    }),
};

export const projectService = {
    getProjects: () => authRequest('/projects'),
    createProject: (projectData) => authRequest('/projects', {
        method: 'POST',
        body: JSON.stringify(projectData),
    }),
};

// --- NEW SERVICE ---
export const savedResultsService = {
    getSavedResults: (projectId) => authRequest(`/projects/${projectId}/saved-results`),
    saveResult: (projectId, docId) => authRequest(`/projects/${projectId}/saved-results/${docId}`, {
        method: 'POST',
    }),
    removeResult: (projectId, docId) => authRequest(`/projects/${projectId}/saved-results/${docId}`, {
        method: 'DELETE',
    }),
};

export const documentService = {
    getDocumentById: (projectId, docId) => authRequest(`/projects/${projectId}/documents/${docId}`),
    updateDocument: (projectId, docId, updates) => authRequest(`/projects/${projectId}/documents/${docId}`, {
        method: 'PUT',
        body: JSON.stringify(updates),
    }),
};

export const searchService = {
    searchDocuments: (projectId, query, mode, guidingPrompt) => authRequest(`/projects/${projectId}/search/documents`, {
        method: 'POST',
        body: JSON.stringify({ query, mode, guidingPrompt }),
    }),
    searchExtractions: (projectId, query, contentTypes, stances, guidingPrompt) => authRequest(`/projects/${projectId}/search/extractions`, {
        method: 'POST',
        body: JSON.stringify({ query, contentTypes, stances, guidingPrompt }),
    }),
    getSummaryUpdate: (searchId) => authRequest(`/search/summary/updates/${searchId}`),
};

export const processingService = {
    getBucket: (projectId) => authRequest(`/projects/${projectId}/processing/bucket`),
    addToBucket: (projectId, documentId) => authRequest(`/projects/${projectId}/processing/bucket`, {
        method: 'POST',
        body: JSON.stringify({ documentId }),
    }),
    removeFromBucket: (projectId, documentIds) => authRequest(`/projects/${projectId}/processing/bucket`, {
        method: 'DELETE',
        body: JSON.stringify({ documentIds }),
    }),
    submitJob: (projectId, jobDetails) => authRequest(`/projects/${projectId}/processing/jobs`, {
        method: 'POST',
        body: JSON.stringify(jobDetails),
    }),
};

export const reportsService = {
    fetchReports: (projectId) => authRequest(`/projects/${projectId}/reports`),
};
