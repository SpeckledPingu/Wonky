import { reactive, readonly } from 'vue';

// --- Reactive State ---
const state = reactive({
  projects: [
    // Example initial project
    // {
    //   id: 'proj_123',
    //   name: 'Sample Project Alpha',
    //   goal: 'To demonstrate mock data',
    //   description: 'This is a pre-loaded sample project.',
    //   createdAt: new Date(),
    //   sourceCount: 2,
    //   researchStreams: [
    //     { id: 'stream_abc', subject: 'Topic 1', focus: 'Focus A', analysisType: 'Domestic Policy', createdAt: new Date() },
    //     { id: 'stream_def', subject: 'Topic 2', focus: 'Focus B', analysisType: 'Impact Analysis', createdAt: new Date() }
    //   ],
    //   researchData: {
    //      notes: { content: 'Initial notes for Sample Project Alpha.' }
    //   }
    // }
  ],
  currentProjectId: null,
  // We'll use a global user ID for simplicity, as auth is removed.
  // In a real app without Firebase, you'd handle user sessions differently.
  userId: 'localUser123',
});

// --- Helper Functions (Mutations/Actions) ---

// Generate a simple unique ID
const generateId = (prefix = 'id_') => {
  return prefix + Math.random().toString(36).substr(2, 9);
};

// Projects
const addProject = (projectData) => {
  const newProject = {
    id: generateId('proj_'),
    ...projectData,
    createdAt: new Date(), // Use JS Date object
    sourceCount: 0,
    researchStreams: [],
    researchData: {
        notes: { content: '' } // Initialize notes for the new project
    }
  };
  state.projects.unshift(newProject); // Add to the beginning like order by desc
  return newProject;
};

const getProjectById = (projectId) => {
  return state.projects.find(p => p.id === projectId);
};

const getAllProjects = () => {
  // Return a sorted copy (by createdAt descending)
  return [...state.projects].sort((a, b) => b.createdAt - a.createdAt);
};

// Research Streams
const addResearchStream = (projectId, streamData) => {
  const project = getProjectById(projectId);
  if (project) {
    const newStream = {
      id: generateId('stream_'),
      ...streamData,
      createdAt: new Date()
    };
    project.researchStreams.push(newStream);
    project.sourceCount = project.researchStreams.length; // Update source count
    return newStream;
  }
  console.error(`Project with ID ${projectId} not found for adding stream.`);
  return null;
};

const getResearchStreamsByProjectId = (projectId) => {
  const project = getProjectById(projectId);
  if (project) {
    return [...project.researchStreams].sort((a, b) => a.createdAt - b.createdAt);
  }
  return [];
};

const deleteResearchStream = (projectId, streamId) => {
  const project = getProjectById(projectId);
  if (project) {
    const initialLength = project.researchStreams.length;
    project.researchStreams = project.researchStreams.filter(s => s.id !== streamId);
    if (project.researchStreams.length < initialLength) {
        project.sourceCount = project.researchStreams.length; // Update source count
        return true;
    }
  }
  return false;
};

// Notes
const getNotes = (projectId) => {
  const project = getProjectById(projectId);
  if (project && project.researchData && project.researchData.notes) {
    return project.researchData.notes.content;
  }
  return '';
};

const saveNotes = (projectId, notesContent) => {
  const project = getProjectById(projectId);
  if (project) {
    if (!project.researchData) {
        project.researchData = { notes: { content: '' } };
    }
    project.researchData.notes.content = notesContent;
    return true;
  }
  return false;
};


// --- Export Store ---
// We export methods to interact with the state, and a readonly version of the state
// for components to consume reactively.
export default {
  state: readonly(state), // Components get a readonly version of the state
  addProject,
  getProjectById,
  getAllProjects,
  addResearchStream,
  getResearchStreamsByProjectId,
  deleteResearchStream,
  getNotes,
  saveNotes,
  // You can add setCurrentProjectId if needed for global state management
  setCurrentProjectId: (id) => { state.currentProjectId = id; }
};
