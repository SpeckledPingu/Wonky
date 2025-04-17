<script setup>
import { ref, watch, nextTick, computed } from 'vue';

// --- Props ---
// Defines the properties that this component accepts from its parent (App.vue).
const props = defineProps({
  // 'selectedDocument' prop receives the file object selected in the FileExplorer.
  // It can be an Object or null if no file is selected.
  selectedDocument: {
    type: Object,
    default: null // Default value is null
  }
});

// --- Reactive State ---

// An array to store the chat message history.
// Each message object should have at least 'id', 'sender' ('user' or 'ai'), and 'text'.
const messages = ref([]);

// Holds the text currently typed into the message input field.
// Uses v-model for two-way data binding with the textarea.
const newMessage = ref('');

// A template ref used to access the chat body DOM element directly,
// primarily for scrolling to the bottom.
const chatBody = ref(null);

// --- Computed Properties ---

// Computes the title to display in the chat header based on the selected document.
const documentTitle = computed(() => {
    // If a document is selected, use its name; otherwise, show a default message.
    return props.selectedDocument ? props.selectedDocument.name : 'Chat';
});

// Computes whether the 'Send' button should be enabled.
const canSendMessage = computed(() => {
    // Requires a document to be selected AND the input field to have non-whitespace text.
    return props.selectedDocument && newMessage.value.trim() !== '';
});

// --- Methods ---

/**
 * Sends the user's message.
 * Adds the message to the local history, clears the input,
 * simulates/calls the backend, and adds the AI response.
 */
async function sendMessage() {
  // Prevent sending if conditions aren't met (no doc selected or empty message)
  if (!canSendMessage.value) return;

  const userMessageText = newMessage.value.trim();

  // 1. Add user's message to the chat display immediately.
  messages.value.push({
    id: Date.now(), // Simple unique ID using timestamp
    sender: 'user',
    text: userMessageText
  });

  // 2. Clear the input field.
  newMessage.value = '';

  // --- 3. LLM Backend Integration Point ---
  // This is where you would make the actual API call to your backend.
  console.log(`Sending to backend: "${userMessageText}" (Context: ${props.selectedDocument.name})`);
  // Replace the simulation below with your fetch/axios call.
  // Example using fetch (uncomment and adapt):
  /*
  try {
    const response = await fetch('/api/chat', { // Your backend endpoint
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: userMessageText,
        documentContext: props.selectedDocument // Send relevant doc info
      })
    });
    if (!response.ok) throw new Error('Network response was not ok');
    const aiResponseData = await response.json();
    const aiResponseText = aiResponseData.reply; // Adjust based on your API response structure

    // 4. Add AI's response to the chat display.
     messages.value.push({
       id: Date.now() + 1, // Ensure unique ID
       sender: 'ai',
       text: aiResponseText
     });

  } catch (error) {
    console.error("Error calling backend:", error);
    // Optionally add an error message to the chat
    messages.value.push({
      id: Date.now() + 1,
      sender: 'ai',
      text: 'Sorry, I encountered an error. Please try again.'
    });
  }
  */

  // --- Simulation (Remove when using real backend) ---
  await new Promise(resolve => setTimeout(resolve, 800)); // Simulate network delay
  const aiResponseText = `Simulated AI response about "${userMessageText}" concerning ${props.selectedDocument.name}. Integrate your backend here.`;
  messages.value.push({ id: Date.now() + 1, sender: 'ai', text: aiResponseText });
  // --- End Simulation ---


  // 5. Scroll the chat window to the bottom to show the latest messages.
  scrollToBottom();
}

/**
 * Scrolls the chat body element to its bottom.
 * Uses nextTick to ensure the DOM has updated with new messages before scrolling.
 */
function scrollToBottom() {
  nextTick(() => {
    if (chatBody.value) {
      // Set the scrollTop property to the full scrollHeight to scroll down.
      chatBody.value.scrollTop = chatBody.value.scrollHeight;
    }
  });
}

// --- Watchers ---

// Watches the 'selectedDocument' prop for changes.
watch(() => props.selectedDocument, (newDoc, oldDoc) => {
  // Only react if the document has actually changed.
  if (newDoc !== oldDoc) {
    console.log('Document changed in ChatInterface:', newDoc?.name);
    // Clear existing messages when the document context changes.
    messages.value = [];
    // Clear the input field as well.
    newMessage.value = '';
    // If a new document is selected (not null), add an initial AI message.
    if (newDoc) {
        messages.value.push({
            id: Date.now(),
            sender: 'ai',
            text: `Switched context to "${newDoc.name}". How can I help with this document?`
        });
        // TODO: Optionally load chat history specific to 'newDoc' from backend/storage here.
    }
    // Ensure chat scrolls to top/shows initial message after clearing/adding.
    nextTick(() => {
        if (chatBody.value) chatBody.value.scrollTop = 0;
    });
  }
});

// Watches the 'messages' array for any changes (new messages added).
// Calls scrollToBottom whenever the array is modified.
// 'deep: true' is important if message objects themselves might change, though usually not needed for just adding/removing.
watch(messages, scrollToBottom, { deep: true });

</script>

<template>
  <div class="chat-interface">
    <div class="chat-header">
      <h2>{{ documentTitle }}</h2>
      <span v-if="selectedDocument" class="header-context">
         </span>
    </div>

    <div class="chat-body" ref="chatBody">
      <div v-if="!selectedDocument" class="placeholder-message">
        Select a document from the left panel to begin chatting.
      </div>
      <div
        v-for="message in messages"
        :key="message.id"
        :class="['message', message.sender]" >
        <span class="message-text">{{ message.text }}</span>
      </div>
    </div>

    <div class="chat-input-area">
      <textarea
        v-model="newMessage"
        placeholder="Start typing..."
        @keydown.enter.prevent="sendMessage"
        :disabled="!selectedDocument"
        rows="1" ></textarea>
      <button @click="sendMessage" :disabled="!canSendMessage">
        <span>&#10148;</span>
      </button>
    </div>
     <div class="chat-footer">
        Note: LLM responses can be inaccurate. Always double-check important information.
    </div>
  </div>
</template>

<style scoped>
.chat-interface {
  display: flex;
  flex-direction: column; /* Stack header, body, input vertically */
  height: 100%; /* Fill the parent panel */
  background-color: #fff; /* White background */
}

.chat-header {
  padding: 10px 15px;
  border-bottom: 1px solid #eee;
  flex-shrink: 0; /* Prevent header from shrinking */
  display: flex;
  align-items: center;
  justify-content: space-between; /* Space out title and context */
}
.chat-header h2 {
    margin: 0;
    padding: 0;
    border: none;
    font-size: 1.2em;
    color: #333;
}
.header-context {
    font-size: 0.9em;
    color: #6c757d; /* Gray text for context */
}

.chat-body {
  flex-grow: 1; /* Take up available vertical space */
  overflow-y: auto; /* Enable scrolling for messages */
  padding: 15px;
  background-color: #f8f9fa; /* Slightly different background for message area */
}

.placeholder-message {
    color: #6c757d;
    text-align: center;
    margin-top: 30px;
    font-style: italic;
}

.message {
  display: flex; /* Use flex for potential icon alignment later */
  margin-bottom: 12px;
  padding: 10px 15px;
  border-radius: 18px; /* More rounded bubbles */
  max-width: 85%; /* Limit message width */
  word-wrap: break-word; /* Wrap long words */
  line-height: 1.4;
}

/* User message specific styles */
.message.user {
  background-color: #007bff; /* Primary blue */
  color: white;
  margin-left: auto; /* Align to the right */
  border-bottom-right-radius: 4px; /* Slightly flatten corner */
}

/* AI message specific styles */
.message.ai {
  background-color: #e9ecef; /* Light gray */
  color: #333;
  margin-right: auto; /* Align to the left */
  border-bottom-left-radius: 4px; /* Slightly flatten corner */
}

.chat-input-area {
  display: flex;
  align-items: center; /* Align textarea and button vertically */
  padding: 10px 15px;
  border-top: 1px solid #eee;
  background-color: #ffffff;
  flex-shrink: 0; /* Prevent input area from shrinking */
}

.chat-input-area textarea {
  flex-grow: 1; /* Take available horizontal space */
  padding: 10px 15px;
  border: 1px solid #ced4da;
  border-radius: 20px; /* Pill shape */
  resize: none; /* Disable manual resizing */
  margin-right: 10px;
  min-height: 24px; /* Base height */
  max-height: 120px; /* Limit expansion */
  overflow-y: auto; /* Scroll if content exceeds max-height */
  line-height: 1.4;
  font-size: 1em;
}
.chat-input-area textarea:disabled {
    background-color: #e9ecef;
    cursor: not-allowed;
}

.chat-input-area button {
  padding: 8px 12px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 50%; /* Make button circular */
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px; /* Fixed width */
  height: 40px; /* Fixed height */
  flex-shrink: 0; /* Prevent button shrinking */
}

.chat-input-area button:hover:not(:disabled) {
  background-color: #0056b3; /* Darker blue on hover */
}
.chat-input-area button:disabled {
    background-color: #adb5bd; /* Gray when disabled */
    cursor: not-allowed;
}
.chat-input-area button span {
    font-size: 1.2em; /* Adjust icon size */
    transform: translateX(1px); /* Fine-tune icon position */
}

.chat-footer {
    padding: 8px 15px;
    text-align: center;
    font-size: 0.8em;
    color: #6c757d;
    border-top: 1px solid #eee;
    flex-shrink: 0;
}

</style>
