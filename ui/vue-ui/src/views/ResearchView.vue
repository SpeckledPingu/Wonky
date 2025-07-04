<template>
  <div class="flex flex-col h-screen overflow-hidden bg-gray-100">
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center">
            <button @click="goBackToSetup" class="flex items-center text-sm text-blue-600 hover:text-blue-800 mr-4">
              <ArrowLeft class="h-4 w-4 mr-1" />
              Setup
            </button>
            <h1 class="text-xl font-semibold text-gray-800 truncate" :title="projectDisplayTitle">
              {{ projectDisplayTitle }}
            </h1>
          </div>
          <div class="flex items-center space-x-3">
            <button @click="showAnalytics" title="Analytics" class="p-2 rounded-md text-gray-600 hover:bg-gray-100 hover:text-gray-800 transition-colors">
              <BarChart2 class="h-5 w-5" />
              <span class="sr-only">Analytics</span>
            </button>
            <button @click="shareProject" title="Share" class="p-2 rounded-md text-gray-600 hover:bg-gray-100 hover:text-gray-800 transition-colors">
              <Share2 class="h-5 w-5" />
              <span class="sr-only">Share</span>
            </button>
            <div class="relative">
                <button @click="toggleUserMenu" title="User Menu" class="p-2 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <UserCircle class="h-7 w-7 text-gray-500"/>
                </button>
            </div>
          </div>
        </div>
      </div>
    </header>

    <div class="flex flex-1 overflow-hidden" ref="mainContentAreaRef">
      <div
        :style="{ flexBasis: `${leftPanelWidthPercent}%` }"
        class="relative bg-white border-r border-gray-200 flex flex-col overflow-hidden flex-shrink-0"
        ref="leftPanelContainerRef"
      >
        <div v-if="!viewingDocument" class="flex flex-col h-full">
            <div class="flex border-b border-gray-200 flex-shrink-0">
              <button
                  v-for="tab in leftPanelTabs" :key="tab.id"
                  @click="activeLeftPanelTab = tab.id"
                  :class="['flex-1 py-2.5 px-3 text-xs font-medium text-center focus:outline-none transition-colors', activeLeftPanelTab === tab.id ? 'border-b-2 border-indigo-500 text-indigo-600 bg-indigo-50' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50']">
                  <component :is="tab.icon" class="h-4 w-4 inline-block mr-1 mb-0.5" /> {{ tab.name }}
              </button>
            </div>
            <div class="flex-1 overflow-y-auto p-4 space-y-4" v-if="activeLeftPanelTab === 'streams'">
              <div class="flex justify-between items-center mb-1">
                <h2 class="text-base font-semibold text-gray-700">Document Streams</h2>
                <button v-if="focusedStreamId" @click="focusedStreamId = null"
                        class="text-xs text-blue-600 hover:text-blue-800 flex items-center">
                  <List class="h-3 w-3 mr-1"/> View All Streams
                </button>
              </div>
              <div v-for="stream in displayedResearchStreams" :key="stream.id" class="mb-3">
                  <ResearchStreamItem
                    :stream="stream"
                    :is-expanded="expandedStreams[stream.id]"
                    :highlighted-document-ids="highlightedDocumentIds"
                    @toggle-expand="toggleStreamExpand(stream.id)"
                    @document-click="handleDocumentClick"
                    v-model:selected-documents="selectedDocumentsPerStream[stream.id]"
                  />
              </div>
              <div v-if="researchStreams.length === 0" class="text-center text-gray-500 py-10"> <FileTextIcon class="h-10 w-10 mx-auto text-gray-400 mb-2"/> <p class="text-sm">No research streams available.</p> </div>
            </div>
            <TimelineView v-if="activeLeftPanelTab === 'timeline'" :documents="allProjectDocuments" :highlighted-document-ids="highlightedDocumentIds" @document-click="handleDocumentClick" class="flex-1 overflow-hidden"/>
            <GraphView v-if="activeLeftPanelTab === 'graph'" :documents="allProjectDocuments" :highlighted-document-ids="highlightedDocumentIds" @document-click="handleDocumentClick" class="flex-1 overflow-hidden"/>
        </div>
        <MarkdownViewer
            v-if="viewingDocument && currentDocument"
            :document="currentDocument"
            @close="closeDocumentViewer"
            class="h-full w-full overflow-y-auto shadow-lg z-10"
        />
      </div>

      <div
        class="w-1.5 bg-gray-300 hover:bg-indigo-500 cursor-col-resize flex-shrink-0 transition-colors select-none"
        @mousedown="startResize($event, 'left')"
        title="Resize left panel"
      ></div>

      <main
        :style="{ flexBasis: `${centerPanelWidthPercent}%` }"
        class="flex flex-col overflow-hidden p-4 bg-gray-50 flex-shrink-0"
        >
        <!-- New Tab Navigation for Center Panel -->
        <div class="flex border-b border-gray-200 flex-shrink-0 mb-4">
          <button
            v-for="tab in centerPanelTabs" :key="tab.id"
            @click="activeCenterPanelTab = tab.id"
            :class="['flex-1 py-2.5 px-3 text-xs font-medium text-center focus:outline-none transition-colors', activeCenterPanelTab === tab.id ? 'border-b-2 border-blue-500 text-blue-600 bg-blue-50' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50']"
          >
            <component :is="tab.icon" class="h-4 w-4 inline-block mr-1 mb-0.5" /> {{ tab.name }}
          </button>
        </div>

        <!-- Chat Content (conditional) -->
        <div v-if="activeCenterPanelTab === 'chat'" class="flex-1 flex flex-col">
          <div class="flex-1 overflow-y-auto bg-white rounded-lg shadow p-4 mb-4 space-y-4" ref="chatMessagesContainerRef">
            <div v-for="message in chatMessages" :key="message.id" :class="['flex', message.isUser ? 'justify-end' : 'justify-start']"> <div :class="['max-w-xs lg:max-w-md px-4 py-2 rounded-lg shadow', message.isUser ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800']"> <p class="text-sm break-words">{{ message.text }}</p> <span class="text-xs opacity-70 block mt-1">{{ message.isUser ? 'You' : 'Assistant' }} - {{ message.time }}</span> </div> </div>
            <div v-if="chatMessages.length === 0" class="text-center text-gray-400 h-full flex flex-col justify-center items-center"> <MessageSquareDashed class="h-12 w-12 mx-auto text-gray-400 mb-2"/> <p>No messages yet.</p> </div>
          </div>
          <div class="mt-auto"> <form @submit.prevent="sendChatMessage" class="flex items-center bg-white p-2 rounded-lg shadow"> <input type="text" v-model="newMessage" placeholder="Start typing..." class="flex-grow px-4 py-2 border-none focus:ring-0 rounded-lg text-sm" /> <button type="submit" class="p-2 text-blue-500 hover:text-blue-700 rounded-full"> <Send class="h-5 w-5" /> </button> </form> </div>
        </div>

        <!-- Source Documents Content (conditional) -->
        <!-- Find and replace the existing SourceDocumentsView tag -->
        <SourceDocumentsView
          v-if="activeCenterPanelTab === 'documents'"
          :documents="unfilteredAllProjectDocuments"
          :project-id="projectId"
          :highlighted-document-ids="highlightedDocumentIds"
          :initial-selected-document-id="selectedDocumentForHierarchy"
          @document-click="handleDocumentClick"
          class="flex-1"
        />

      </main>

      <div
        v-if="isRightPanelEffectivelyVisible"
        class="w-1.5 bg-gray-300 hover:bg-indigo-500 cursor-col-resize flex-shrink-0 transition-colors select-none"
        @mousedown="startResize($event, 'right')"
        title="Resize right panel"
      ></div>

      <aside
        v-if="isRightPanelEffectivelyVisible"
        :style="{ flexBasis: `${rightPanelWidthPercent}%` }"
        class="bg-white border-l border-gray-200 overflow-y-hidden flex flex-col flex-shrink-0"
        ref="rightPanelRef"
      >
         <div class="flex flex-col h-full">
            <div class="flex border-b border-gray-200 flex-shrink-0">
                <button v-for="tab in rightPanelTabs" :key="tab.id" @click="activeRightPanelTab = tab.id" :class="['flex-1 py-2.5 px-3 text-xs font-medium text-center focus:outline-none transition-colors', activeRightPanelTab === tab.id ? 'border-b-2 border-purple-500 text-purple-600 bg-purple-50' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50']" :title="tab.name"> <component :is="tab.icon" class="h-4 w-4 inline-block mr-1 mb-0.5" /> {{ tab.name }} </button>
            </div>
            <div class="p-4 overflow-y-auto flex-1 space-y-5">
                <div v-if="activeRightPanelTab === 'actions'">
                    <div class="mb-6">
                        <h3 class="text-sm font-semibold text-gray-600 mb-3 flex items-center"> <Zap class="h-4 w-4 mr-2 text-purple-600"/> Pre-defined Research Actions </h3>
                        <div class="space-y-2">
                            <button @click="runStudioAction('executiveSummary')" class="w-full btn btn-primary btn-sm text-xs py-2 flex items-center justify-center"> <FileTextIcon class="h-4 w-4 mr-1.5"/> Create Executive Overview </button>
                            <button @click="runStudioAction('whatsMissing')" class="w-full btn btn-primary btn-sm text-xs py-2 flex items-center justify-center"> <SearchSlash class="h-4 w-4 mr-1.5"/> Run What's Missing Analysis </button>
                            <button @click="runStudioAction('keyStakeholders')" class="w-full btn btn-secondary btn-sm text-xs py-2 flex items-center justify-center"> <Users class="h-4 w-4 mr-1.5"/> Identify Key Stakeholders </button>
                            <button @click="runStudioAction('policyMemo')" class="w-full btn btn-secondary btn-sm text-xs py-2 flex items-center justify-center"> <FileSignature class="h-4 w-4 mr-1.5"/> Generate Policy Memo Draft </button>
                            <button @click="runStudioAction('comparePolicies')" class="w-full btn btn-secondary btn-sm text-xs py-2 flex items-center justify-center"> <GitCompareArrows class="h-4 w-4 mr-1.5"/> Compare Policy Options </button>
                            <button @click="runStudioAction('legislativeHistory')" class="w-full btn btn-secondary btn-sm text-xs py-2 flex items-center justify-center"> <ScrollText class="h-4 w-4 mr-1.5"/> Summarize Legislative History </button>
                            <button @click="runStudioAction('extractStatistics')" class="w-full btn btn-secondary btn-sm text-xs py-2 flex items-center justify-center"> <SigmaSquare class="h-4 w-4 mr-1.5"/> Extract Key Statistics </button>
                        </div>
                    </div>
                    <div>
                        <h3 class="text-sm font-semibold text-gray-600 mb-3 flex items-center"> <UserPlus class="h-4 w-4 mr-2 text-teal-600"/> User-Defined Actions </h3>
                        <div v-if="userDefinedActions.length === 0" class="text-xs text-gray-500 italic text-center py-3"> No user actions defined yet. Create them in the Prompt Library. </div>
                        <div v-else class="space-y-2"> <button v-for="action in userDefinedActions" :key="action.id" @click="runUserAction(action)" class="w-full btn btn-sm text-xs py-2 flex items-center justify-center bg-teal-500 hover:bg-teal-600 text-white"> <Play class="h-4 w-4 mr-1.5"/> {{ action.name }} </button> </div>
                    </div>
                </div>
                <ImportantSubjectsPanel v-if="activeRightPanelTab === 'subjects'" :documents="allProjectDocuments" @subjects-selected="updateHighlightedDocumentsBySubject"/>
                <div v-if="activeRightPanelTab === 'audio'"> <h3 class="text-sm font-semibold text-gray-600 mb-2 flex items-center"> <Mic class="h-4 w-4 mr-2 text-blue-600"/> Audio Tools </h3> <p class="text-xs text-gray-500 mb-3">Create an audio summary of selected documents.</p> <button @click="runStudioAction('generateAudio')" class="w-full btn btn-primary btn-sm text-xs py-1.5"> <PlayCircle class="h-4 w-4 inline mr-1"/> Generate Audio Summary </button> </div>

                <div v-if="activeRightPanelTab === 'guidedChat'">
                    <div class="mb-6">
                        <h3 class="text-sm font-semibold text-gray-600 mb-3 flex items-center">
                            <UserCog class="h-4 w-4 mr-2 text-sky-600"/> Select Persona
                        </h3>
                        <div class="grid grid-cols-2 gap-2">
                            <button v-for="persona in personas" :key="persona.id"
                                @click="selectPersona(persona)"
                                :class="['btn btn-sm text-xs py-2 flex items-center justify-center transition-colors', selectedPersona?.id === persona.id ? 'bg-sky-600 text-white' : 'bg-sky-100 text-sky-700 hover:bg-sky-200']">
                                <component :is="getIconComponent(persona.icon)" class="h-4 w-4 mr-1.5"/> {{ persona.name }}
                            </button>
                        </div>
                    </div>
                    <div class="mb-6">
                        <h3 class="text-sm font-semibold text-gray-600 mb-3 flex items-center">
                            <Lightbulb class="h-4 w-4 mr-2 text-amber-600"/> Explore Tangents
                        </h3>
                        <div class="space-y-2">
                             <button v-for="tangent in tangents" :key="tangent.id"
                                @click="selectTangent(tangent)"
                                :class="['w-full btn btn-sm text-xs py-2 flex items-center justify-center transition-colors', selectedTangent?.id === tangent.id ? 'bg-amber-600 text-white' : 'bg-amber-100 text-amber-700 hover:bg-amber-200']">
                                <component :is="getIconComponent(tangent.icon)" class="h-4 w-4 mr-1.5"/> {{ tangent.name }}
                            </button>
                        </div>
                    </div>
                     <div>
                        <h3 class="text-sm font-semibold text-gray-600 mb-3 flex items-center">
                            <MessagesSquare class="h-4 w-4 mr-2 text-lime-600"/> Custom Deep Dive
                        </h3>
                        <textarea v-model="customDeepDiveInput" placeholder="Enter your custom topic or question for a deep dive..." rows="3" class="w-full text-xs p-2 border border-gray-300 rounded-md focus:ring-lime-500 focus:border-lime-500"></textarea>
                        <button @click="startCustomDeepDive" class="mt-2 w-full btn btn-success btn-sm text-xs py-2 bg-lime-500 hover:bg-lime-600">
                            <Send class="h-4 w-4 mr-1.5"/> Start Custom Deep Dive
                        </button>
                    </div>
                </div>

                <div v-if="activeRightPanelTab === 'notes'">
                    <h3 class="text-sm font-semibold text-gray-600 mb-2 flex items-center">
                        <ClipboardEdit class="h-4 w-4 mr-2 text-yellow-600"/> Notes
                    </h3>
                    <textarea v-model="currentNoteContent" placeholder="Your quick notes here..." rows="8" class="w-full text-xs p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 mb-3"></textarea>
                    <button @click="addNoteAsDocument" class="w-full btn btn-primary btn-sm text-xs py-2 bg-yellow-500 hover:bg-yellow-600 text-white">
                        <FilePlus2 class="h-4 w-4 mr-1.5"/> Add Note as Document
                    </button>
                </div>
            </div>
         </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed, watch, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import ResearchStreamItem from '../components/ResearchStreamItem.vue';
import MarkdownViewer from '../components/MarkdownViewer.vue';
import TimelineView from '../components/TimelineView.vue';
import GraphView from '../components/GraphView.vue';
import ImportantSubjectsPanel from '../components/ImportantSubjectsPanel.vue';
import SourceDocumentsView from '../components/SourceDocumentsView.vue'; // NEW: Import the new component

// Import all Lucide icons to be able to map them by string name
import * as LucideIcons from 'lucide-vue-next';

import {
  ArrowLeft, BarChart2, Share2, UserCircle, MessageCircle, Send, Sparkles, PlayCircle, Users, FileText as FileTextIconOriginal,
  MessageSquareDashed, Zap, SearchSlash, FileSignature, GitCompareArrows, Mic, Users2, ClipboardEdit,
  List, Clock, Spline, Tags, ScrollText, SigmaSquare, UserPlus, Play,
  UserCog, Scale, Brain, Lightbulb, Shuffle, EyeOff, MessagesSquare, FilePlus2
} from 'lucide-vue-next';

const FileTextIcon = FileTextIconOriginal;

const route = useRoute();
const router = useRouter();
const API_BASE_URL = 'http://localhost:8000';

// --- Refs for DOM elements ---
const mainContentAreaRef = ref(null);
const leftPanelContainerRef = ref(null);
const rightPanelRef = ref(null);
const chatMessagesContainerRef = ref(null);

// --- Panel Width State ---
const leftPanelWidthPercent = ref(25);
const rightPanelWidthPercent = ref(25);
const centerPanelWidthPercent = computed(() => {
    const rightWidth = isRightPanelEffectivelyVisible.value ? rightPanelWidthPercent.value : 0;
    const remaining = 100 - leftPanelWidthPercent.value - rightWidth;
    return Math.max(minPanelPercent, remaining);
});

// --- Resizing State ---
const isResizing = ref(false);
const activeResizer = ref(null); // 'left' or 'right'
const dragStartX = ref(0);
const initialLeftPanelWidthPx = ref(0);
const initialRightPanelWidthPx = ref(0);
const minPanelPercent = 10; // Minimum panel width

// --- Panel Visibility ---
const isRightPanelEffectivelyVisible = ref(true);

// --- Project Data State ---
const projectId = ref(null);
const projectName = ref(null);
const researchStreams = ref([]);
const expandedStreams = ref({});
const selectedDocumentsPerStream = ref({});
const highlightedDocumentIds = ref([]);
const viewingDocument = ref(false);
const currentDocument = ref(null);
const focusedStreamId = ref(null); // To store the ID of the focused stream
const selectedDocumentForHierarchy = ref(null); // NEW reactive state for SourceDocumentsView

// --- UI State ---
const activeLeftPanelTab = ref('streams');
const activeRightPanelTab = ref('actions');
const activeCenterPanelTab = ref('chat'); // NEW: Default to chat tab in center
const newMessage = ref('');
const chatMessages = ref([]);
const currentNoteContent = ref('');

// --- Dynamic Configuration Data State (formerly hardcoded) ---
const userDefinedActions = ref([]); // Now fetched from backend
const personas = ref([]); // Now fetched from backend
const tangents = ref([]); // Now fetched from backend

const selectedPersona = ref(null);
const selectedTangent = ref(null);
const customDeepDiveInput = ref('');

const leftPanelTabs = ref([
    { id: 'streams', name: 'Streams', icon: List },
    { id: 'timeline', name: 'Timeline', icon: Clock },
    { id: 'graph', name: 'Graph', icon: Spline }
]);

// NEW: Tabs for the center panel
const centerPanelTabs = ref([
    { id: 'chat', name: 'Chat', icon: MessageCircle },
    { id: 'documents', name: 'Documents', icon: FileTextIcon } // Using the aliased FileTextIcon
]);

const rightPanelTabs = ref([
    { id: 'actions', name: 'Actions', icon: Zap },
    { id: 'subjects', name: 'Subjects', icon: Tags },
    { id: 'guidedChat', name: 'Guided Chat', icon: MessagesSquare },
    { id: 'audio', name: 'Audio', icon: Mic },
    { id: 'notes', name: 'Notes', icon: ClipboardEdit },
]);

// --- Computed Properties ---
const projectDisplayTitle = computed(() => {
    const name = projectName.value || "Unnamed Project";
    return name.length > 50 ? name.substring(0, 47) + "..." : name;
});

// Filter research streams based on focusedStreamId
const displayedResearchStreams = computed(() => {
  if (focusedStreamId.value) {
    return researchStreams.value.filter(stream => stream.id === focusedStreamId.value);
  }
  return researchStreams.value;
});

// Update allProjectDocuments to also respect focusedStreamId
const allProjectDocuments = computed(() => {
  let streamsToProcess = researchStreams.value;
  if (focusedStreamId.value) {
    streamsToProcess = researchStreams.value.filter(stream => stream.id === focusedStreamId.value);
  }
  return streamsToProcess.reduce((acc, stream) => {
    return acc.concat(stream.documents.map(doc => ({...doc, streamName: stream.subject, streamId: stream.id })));
  }, []);
});


// Utility to get Lucide icon component by string name
const getIconComponent = (iconName) => {
  return LucideIcons[iconName] || null; // Return the component or null if not found
};

// --- Methods ---
const checkRightPanelVisibility = () => {
    if (typeof window !== 'undefined') {
        isRightPanelEffectivelyVisible.value = window.innerWidth >= 768;
    }
};

const scrollToBottom = () => {
  nextTick(() => {
    if (chatMessagesContainerRef.value) {
      chatMessagesContainerRef.value.scrollTop = chatMessagesContainerRef.value.scrollHeight;
    }
  });
};

// Function to load static configuration data from backend
const loadStaticData = async () => {
  try {
    const [personasRes, tangentsRes, userActionsRes] = await Promise.all([
      fetch(`${API_BASE_URL}/api/personas`),
      fetch(`${API_BASE_URL}/api/tangents`),
      fetch(`${API_BASE_URL}/api/user-actions`)
    ]);

    if (!personasRes.ok) throw new Error(`HTTP error! status: ${personasRes.status} for personas`);
    if (!tangentsRes.ok) throw new Error(`HTTP error! status: ${tangentsRes.status} for tangents`);
    if (!userActionsRes.ok) throw new Error(`HTTP error! status: ${userActionsRes.status} for user actions`);

    personas.value = await personasRes.json();
    tangents.value = await tangentsRes.json();
    userDefinedActions.value = await userActionsRes.json();

  } catch (error) {
    console.error("Failed to load static configuration data:", error);
    addAssistantMessage("Failed to load some configuration data. Please check the backend.", true);
  }
};

const loadProjectData = async () => {
  console.log("Fetching project data for ID:", projectId.value);
  if (!projectId.value) {
    console.error("Data load failed: Project ID is missing.");
    alert("Could not load project. Returning to projects list.");
    router.push({ name: 'ProjectsView' });
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/projects/${projectId.value}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const projectData = await response.json();

    researchStreams.value = projectData.researchStreams || [];


    const newExpandedState = {};
    const newSelectedDocsState = {};
    (projectData.researchStreams || []).forEach(stream => {
      newSelectedDocsState[stream.id] = [];
      newExpandedState[stream.id] = true;
    });

    // Set focusedStreamId from route query
    focusedStreamId.value = route.query.focusStream || null;

    if (focusedStreamId.value && newExpandedState[focusedStreamId.value] !== undefined) {
      const focusedStream = projectData.researchStreams.find(s => s.id === focusedStreamId.value);
      if (focusedStream && focusedStream.documents.length === 0) {
        activeRightPanelTab.value = 'notes';
        addAssistantMessage(`Ready to research "${focusedStream.subject}". Add your first note or upload a document.`);
      }
    }

    expandedStreams.value = newExpandedState;
    selectedDocumentsPerStream.value = newSelectedDocsState;

    if (chatMessages.value.length === 0) {
        addAssistantMessage(`Hello! How can I help you with project "${projectName.value || 'this project'}"?`);
    }

  } catch (error) {
    console.error("Failed to load project data:", error);
    alert("Could not load project data from the server. Please check the connection and try again.");
    router.push({ name: 'ProjectsView' });
  }
};


const startResize = (event, resizer) => {
  event.preventDefault();
  isResizing.value = true;
  activeResizer.value = resizer;
  dragStartX.value = event.clientX;
  if (mainContentAreaRef.value && leftPanelContainerRef.value) {
    initialLeftPanelWidthPx.value = leftPanelContainerRef.value.offsetWidth;
    if (isRightPanelEffectivelyVisible.value && rightPanelRef.value) {
        initialRightPanelWidthPx.value = rightPanelRef.value.offsetWidth;
    }
  }
  document.body.style.cursor = 'col-resize';
  document.body.style.userSelect = 'none';
  window.addEventListener('mousemove', handleDrag);
  window.addEventListener('mouseup', stopDrag);
};

const handleDrag = (event) => {
  if (!isResizing.value || !mainContentAreaRef.value) return;
  const deltaX = event.clientX - dragStartX.value;
  const totalWidthPx = mainContentAreaRef.value.offsetWidth;
  if (totalWidthPx === 0) return;

  if (activeResizer.value === 'left') {
    let newLeftWidthPx = initialLeftPanelWidthPx.value + deltaX;
    const minCenterPx = (minPanelPercent / 100) * totalWidthPx;
    const rightWidthPx = isRightPanelEffectivelyVisible.value ? ((rightPanelWidthPercent.value / 100) * totalWidthPx) : 0;
    const resizersWidth = isRightPanelEffectivelyVisible.value ? 12 : 6;
    const maxLeftPx = totalWidthPx - minCenterPx - rightWidthPx - resizersWidth;
    newLeftWidthPx = Math.max((minPanelPercent / 100) * totalWidthPx, Math.min(newLeftWidthPx, maxLeftPx));
    leftPanelWidthPercent.value = parseFloat(((newLeftWidthPx / totalWidthPx) * 100).toFixed(2));
  } else if (activeResizer.value === 'right' && isRightPanelEffectivelyVisible.value) {
    let newRightWidthPx = initialRightPanelWidthPx.value - deltaX;
    const minCenterPx = (minPanelPercent / 100) * totalWidthPx;
    const leftWidthPx = (leftPanelWidthPercent.value / 100) * totalWidthPx;
    const maxRightPx = totalWidthPx - minCenterPx - leftWidthPx - 12;
    newRightWidthPx = Math.max((minPanelPercent / 100) * totalWidthPx, Math.min(newRightWidthPx, maxRightPx));
    rightPanelWidthPercent.value = parseFloat(((newRightWidthPx / totalWidthPx) * 100).toFixed(2));
  }
};

const stopDrag = () => {
  isResizing.value = false;
  activeResizer.value = null;
  document.body.style.cursor = '';
  document.body.style.userSelect = '';
  window.removeEventListener('mousemove', handleDrag);
  window.removeEventListener('mouseup', stopDrag);
};

const toggleStreamExpand = (streamId) => { expandedStreams.value[streamId] = !expandedStreams.value[streamId]; };
const handleDocumentClick = (document) => {
  currentDocument.value = document;
  viewingDocument.value = true;
  // NEW: When a document is clicked, also switch to the 'documents' tab
  // and set it as the root for hierarchy display.
  activeCenterPanelTab.value = 'documents';
  selectedDocumentForHierarchy.value = document.id;
};
const closeDocumentViewer = () => { viewingDocument.value = false; currentDocument.value = null; };

const addAssistantMessage = (text, isError = false) => {
    chatMessages.value.push({
        id: `chat_${Date.now()}`,
        text: text,
        isUser: false,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    });
    scrollToBottom();
};

const sendChatMessage = async () => {
    const messageText = newMessage.value.trim();
    if (messageText === '') return;

    // Add user message to chat immediately
    chatMessages.value.push({
        id: `chat_${Date.now()}`,
        text: messageText,
        isUser: true,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    });
    newMessage.value = '';
    scrollToBottom();

    try {
        const payload = {
            message: messageText,
            selected_doc_ids: Object.values(selectedDocumentsPerStream.value).flat(),
            persona_id: selectedPersona.value?.id || null,
            tangent_id: selectedTangent.value?.id || null, // Pass tangent_id
            custom_deep_dive: customDeepDiveInput.value.trim() || null // Pass custom_deep_dive
        };
        const response = await fetch(`${API_BASE_URL}/api/projects/${projectId.value}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!response.ok) throw new Error(`API Error: ${response.status}`);
        const data = await response.json();
        addAssistantMessage(data.response_text);
    } catch (error) {
        console.error("Failed to get chat response:", error);
        addAssistantMessage("Sorry, I couldn't get a response. Please try again.", true);
    }
};

const executeAction = async (actionId, customPrompt = null) => {
    const action = userDefinedActions.value.find(a => a.id === actionId) || { name: actionId };
    addAssistantMessage(`Executing action: "${action.name}"...`);

    try {
        const payload = {
            action_id: actionId,
            selected_doc_ids: Object.values(selectedDocumentsPerStream.value).flat(),
            custom_prompt: customPrompt
        };
        const response = await fetch(`${API_BASE_URL}/api/projects/${projectId.value}/actions/run`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!response.ok) throw new Error(`API Error: ${response.status}`);
        const data = await response.json();
        addAssistantMessage(data.response_text);
    } catch (error) {
        console.error(`Failed to execute action ${actionId}:`, error);
        addAssistantMessage(`Sorry, there was an error running the action "${action.name}".`, true);
    }
};

const runStudioAction = (actionType) => executeAction(actionType);
const runUserAction = (action) => executeAction(action.id, action.promptContent);

const goBackToSetup = () => {
  if (projectId.value && projectName.value) {
    router.push({ name: 'ProjectSetupView', params: { projectId: projectId.value, projectName: projectName.value } });
  } else {
    router.push({ name: 'ProjectsView' });
  }
};

const updateHighlightedDocumentsBySubject = (subject) => {
    if (!subject) { highlightedDocumentIds.value = []; return; }
    const newHighlightedIds = [];
    allProjectDocuments.value.forEach(doc => { if (doc.subjects?.includes(subject) || doc.keyPlayers?.includes(subject) || doc.name.toLowerCase().includes(subject.toLowerCase())) { newHighlightedIds.push(doc.id); } });
    highlightedDocumentIds.value = newHighlightedIds;
    addAssistantMessage(`Highlighted ${newHighlightedIds.length} document(s) for "${subject}".`);
};

const showAnalytics = () => { alert("Analytics feature coming soon!"); };
const shareProject = () => { alert("Sharing options coming soon!"); };
const toggleUserMenu = () => { alert("User menu coming soon!"); };

const startAssistantConversation = async (payload) => {
    let initialText = "Okay, let's try that.";

    // Use the fetched persona/tangent data for initial text
    if (payload.persona_id) {
        const persona = personas.value.find(p => p.id === payload.persona_id);
        if (persona) initialText = persona.promptStart;
    }
    if (payload.tangent_id) {
        const tangent = tangents.value.find(t => t.id === payload.tangent_id);
        if (tangent) initialText = tangent.promptStart;
    }
    if (payload.custom_deep_dive) initialText = `Starting a deep dive on: "${payload.custom_deep_dive}".`;

    addAssistantMessage(initialText);

    try {
        const response = await fetch(`${API_BASE_URL}/api/projects/${projectId.value}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: initialText, selected_doc_ids: Object.values(selectedDocumentsPerStream.value).flat(), ...payload })
        });
        if (!response.ok) throw new Error(`API Error: ${response.status}`);
        const data = await response.json();
        addAssistantMessage(data.response_text);
    } catch (error) {
        console.error("Failed to start assistant conversation:", error);
        addAssistantMessage("Sorry, I couldn't process that request.", true);
    }
};

const selectPersona = (persona) => {
    selectedPersona.value = selectedPersona.value?.id === persona.id ? null : persona;
    if (selectedPersona.value) {
        startAssistantConversation({ persona_id: persona.id });
    }
};

const selectTangent = (tangent) => {
    selectedTangent.value = selectedTangent.value?.id === tangent.id ? null : tangent;
     if (selectedTangent.value) {
        startAssistantConversation({ tangent_id: tangent.id });
     }
};

const startCustomDeepDive = () => {
    if (customDeepDiveInput.value.trim()) {
        startAssistantConversation({ custom_deep_dive: customDeepDiveInput.value.trim() });
        customDeepDiveInput.value = '';
    } else { alert("Please enter a topic for your custom deep dive."); }
};

const addNoteAsDocument = async () => {
    if (!currentNoteContent.value.trim()) {
        alert("Note is empty. Please write something before adding.");
        return;
    }

    try {
        let notesStream = researchStreams.value.find(s => s.subject === 'My Notes');
        let streamId;

        if (!notesStream) {
            console.log("Creating a 'My Notes' stream...");
            const streamResponse = await fetch(`${API_BASE_URL}/api/projects/${projectId.value}/streams`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    subject: 'My Notes',
                    focus: 'User-generated notes and annotations',
                    analysisType: 'General'
                })
            });
            if (!streamResponse.ok) throw new Error('Failed to create notes stream');
            const newStream = await streamResponse.json();
            streamId = newStream.id;
        } else {
            streamId = notesStream.id;
        }

        const newNoteDocPayload = {
            name: `Note - ${new Date().toLocaleDateString()} ${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`,
            type: 'note',
            content: currentNoteContent.value,
            subjects: ['User Note'],
        };

        const docResponse = await fetch(`${API_BASE_URL}/api/projects/${projectId.value}/streams/${streamId}/documents`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newNoteDocPayload)
        });

        if (!docResponse.ok) throw new Error('Failed to add note as document');
        const createdDocument = await docResponse.json();

        currentNoteContent.value = '';
        alert(`Note added as a document to "My Notes" stream.`);
        addAssistantMessage(`A new note titled "${createdDocument.name}" has been added as a document.`);
        activeLeftPanelTab.value = 'streams';

        await loadProjectData();

    } catch (error) {
        console.error("Error adding note as document:", error);
        alert("There was an error saving your note. Please try again.");
    }
};

const unfilteredAllProjectDocuments = computed(() => {
  return researchStreams.value.reduce((acc, stream) => {
    return acc.concat(stream.documents.map(doc => ({...doc, streamName: stream.subject, streamId: stream.id })));
  }, []);
});


// --- Watchers ---
watch(
  () => [route.params.projectId, route.params.projectName, route.query.focusStream],
  ([newPid, newPname]) => {
    if (newPid && newPname) {
      if (newPid !== projectId.value || !researchStreams.value.length) {
        projectId.value = newPid;
        projectName.value = newPname;
        loadProjectData();
      }
    } else {
      console.warn("Route params projectId or projectName are missing. Current route:", route.fullPath);
    }
  },
  { immediate: true }
);

// Watcher to clear selectedDocumentForHierarchy when switching away from documents tab
watch(activeCenterPanelTab, (newTab) => {
  if (newTab !== 'documents') {
    selectedDocumentForHierarchy.value = null;
  }
});

watch(isRightPanelEffectivelyVisible, (newValue, oldValue) => {
    if (newValue !== oldValue) {
        const currentRightWidth = newValue ? rightPanelWidthPercent.value : 0;
        if (leftPanelWidthPercent.value + minPanelPercent + currentRightWidth > 100) {
            leftPanelWidthPercent.value = Math.max(minPanelPercent, 100 - minPanelPercent - currentRightWidth);
        }
    }
});

onMounted(() => {
  checkRightPanelVisibility();
  window.addEventListener('resize', checkRightPanelVisibility);
  loadStaticData(); // Load dynamic configuration data on mount
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', checkRightPanelVisibility);
  window.removeEventListener('mousemove', handleDrag);
  window.removeEventListener('mouseup', stopDrag);
});

</script>

<style scoped>
.overflow-y-auto::-webkit-scrollbar { width: 6px; }
.overflow-y-auto::-webkit-scrollbar-thumb { background-color: #cbd5e1; border-radius: 10px; }
.overflow-y-auto::-webkit-scrollbar-track { background-color: #f1f5f9; }
.sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border-width: 0; }
.select-none { user-select: none; }
.btn-sm { @apply text-xs py-1.5 px-3; }
.btn-primary { @apply bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500; }
.btn-secondary { @apply bg-indigo-500 text-white hover:bg-indigo-600 focus:ring-indigo-400; }
.btn-success { @apply bg-green-500 text-white hover:bg-green-600 focus:ring-green-400; }
.flex-shrink-0 { flex-shrink: 0; }
.flex-1.overflow-hidden { height: calc(100vh - 4rem); } /* Adjusted for header */
.break-words { word-break: break-word; }
</style>