import axios from 'axios';

// Create an axios instance with a base URL.
// This points to your FastAPI backend.
const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000/api', // Make sure this matches your backend's address
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- Project Endpoints ---

export const fetchProjects = () => {
  return apiClient.get('/projects');
};

export const fetchProjectById = (projectId) => {
  return apiClient.get(`/projects/${projectId}`);
};

export const createProject = (projectData) => {
  // projectData should match the ProjectCreate Pydantic model
  return apiClient.post('/projects', projectData);
};

// --- Research Stream Endpoints ---

export const fetchStreamsForProject = (projectId) => {
  return apiClient.get(`/projects/${projectId}/streams`);
};

export const addStreamToProject = (projectId, streamData) => {
  // streamData should match the ResearchStreamCreate Pydantic model
  return apiClient.post(`/projects/${projectId}/streams`, streamData);
};

export const deleteStreamFromProject = (projectId, streamId) => {
  return apiClient.delete(`/projects/${projectId}/streams/${streamId}`);
};

// You can add more functions here for documents, prompts, etc. as you build them out.