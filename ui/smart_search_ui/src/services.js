import { useUserStore } from '../stores/userStore';
import { useNotificationStore } from '../stores/notificationStore';

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

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

// --- Service Objects ---

export const documentService = {
    getDocumentById: (docId) => apiRequest(`/documents/${docId}`),
    updateDocument: (docId, updates) => apiRequest(`/documents/${docId}`, {
        method: 'PUT',
        body: JSON.stringify(updates),
    }),
};

export const searchService = {
    searchDocuments: (query, mode) => apiRequest('/search/documents', {
        method: 'POST',
        body: JSON.stringify({ query, mode }),
    }),
    searchExtractions: (query, contentTypes, stances) => apiRequest('/search/extractions', {
        method: 'POST',
        body: JSON.stringify({ query, contentTypes, stances }),
    }),
    getGuidedSummary: (searchId, interest) => apiRequest(`/search/summary/${searchId}`, {
        method: 'POST',
        body: JSON.stringify({ interest }),
    }),
};

export const processingService = {
    addToBucket: (documentId) => apiRequest('/processing/bucket', {
        method: 'POST',
        body: JSON.stringify({ documentId }),
    }),
    // --- NEW FUNCTION ---
    removeFromBucket: (documentIds) => apiRequest('/processing/bucket', {
        method: 'DELETE',
        body: JSON.stringify({ documentIds }),
    }),
    submitJob: (jobDetails) => apiRequest('/processing/jobs', {
        method: 'POST',
        body: JSON.stringify(jobDetails),
    }),
};

export const reportsService = {
    fetchReports: () => apiRequest('/reports'),
};
