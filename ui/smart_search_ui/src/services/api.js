import { useUserStore } from '../stores/userStore';
import { useNotificationStore } from '../stores/notificationStore';
import { useProjectStore } from '../stores/projectStore';

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

// --- FIX: This is the core API function that was missing ---
async function apiRequest(endpoint, options = {}) {
    const userStore = useUserStore();
    const notificationStore = useNotificationStore();
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userStore.userId || 'mock-token'}`,
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

export const projectService = {
    getProjects: () => apiRequest('/projects'),
};

export const documentService = {
    getDocumentById: (projectId, docId) => apiRequest(`/projects/${projectId}/documents/${docId}`),
    updateDocument: (projectId, docId, updates) => apiRequest(`/projects/${projectId}/documents/${docId}`, {
        method: 'PUT',
        body: JSON.stringify(updates),
    }),
};

export const searchService = {
    searchDocuments: (projectId, query, mode, guidingPrompt) => apiRequest(`/projects/${projectId}/search/documents`, {
        method: 'POST',
        body: JSON.stringify({ query, mode, guidingPrompt }),
    }),
    searchExtractions: (projectId, query, contentTypes, stances, guidingPrompt) => apiRequest(`/projects/${projectId}/search/extractions`, {
        method: 'POST',
        body: JSON.stringify({ query, contentTypes, stances, guidingPrompt }),
    }),
    getSummaryUpdate: (searchId) => apiRequest(`/search/summary/updates/${searchId}`),
};

export const processingService = {
    getBucket: (projectId) => apiRequest(`/projects/${projectId}/processing/bucket`),
    addToBucket: (projectId, documentId) => apiRequest(`/projects/${projectId}/processing/bucket`, {
        method: 'POST',
        body: JSON.stringify({ documentId }),
    }),
    removeFromBucket: (projectId, documentIds) => apiRequest(`/projects/${projectId}/processing/bucket`, {
        method: 'DELETE',
        body: JSON.stringify({ documentIds }),
    }),
    submitJob: (projectId, jobDetails) => apiRequest(`/projects/${projectId}/processing/jobs`, {
        method: 'POST',
        body: JSON.stringify(jobDetails),
    }),
};

export const reportsService = {
    fetchReports: (projectId) => apiRequest(`/projects/${projectId}/reports`),
};
