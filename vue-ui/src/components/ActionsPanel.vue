<script setup>
import { ref } from 'vue';

// --- Emits ---
// Declares the 'action-triggered' event that this component emits
// when one of the action buttons is clicked.
const emit = defineEmits(['action-triggered']);

// --- Reactive State ---
// Holds the content of the notes textarea using v-model.
const notes = ref('');
// Placeholder for saved notes (in a real app, this might be an array)
const savedNotes = ref([]);

// --- Methods ---

/**
 * Emits the 'action-triggered' event upwards to the parent (App.vue)
 * with the name of the action that was clicked.
 * @param {string} actionName - The identifier for the action (e.g., 'Generate Summary').
 */
function triggerAction(actionName) {
    console.log('Action button clicked:', actionName);
    emit('action-triggered', actionName);
}

/**
 * Placeholder function for saving the current content of the notes textarea.
 * In a real app, this would save to localStorage, backend, or state management.
 */
function saveCurrentNote() {
    const noteText = notes.value.trim();
    if (noteText) {
        console.log('Saving note:', noteText);
        // Add to our temporary saved notes list (replace with real persistence)
        savedNotes.value.push({ id: Date.now(), text: noteText });
        notes.value = ''; // Clear the textarea after saving
        alert('Note saved (simulated).');
        // TODO: Implement actual saving logic (localStorage, API call, etc.)
    } else {
        alert('Note cannot be empty.');
    }
}

/**
 * Placeholder function to add a new, empty note area or focus the existing one.
 */
 function addNewNote() {
     console.log("Add new note clicked");
     // In this simple version, we just focus the textarea
     // A more complex version might create distinct note objects
     const textarea = document.querySelector('.notes-section textarea'); // Find textarea
     if (textarea) textarea.focus(); // Focus it
     alert('Add Note clicked - focus set to textarea (implement multi-note logic if needed).')
 }

</script>

<template>
  <div class="actions-panel-content">
    <h3>Studio</h3> <div class="section action-buttons-section">
        <button @click="triggerAction('Audio Overview')">Audio Overview</button>
        <button @click="triggerAction('Study Guide')">Study Guide</button>
        <button @click="triggerAction('Briefing Doc')">Briefing Doc</button>
        <button @click="triggerAction('FAQ')">FAQ</button>
        <button @click="triggerAction('Timeline')">Timeline</button>
        <button @click="triggerAction('Mind Map')">Mind Map</button>
        </div>

    <div class="section notes-section">
      <div class="notes-header">
          <h4>Notes</h4>
          <button class="add-note-button" @click="addNewNote">+ Add Note</button>
      </div>
      <textarea v-model="notes" placeholder="Save insights, ideas, or summaries here..."></textarea>
      <div class="saved-notes-area">
            <div v-if="savedNotes.length === 0" class="saved-notes-placeholder">
                Saved notes will appear here. Click 'Add Note' or save a chat message.
            </div>
            <ul v-else class="saved-notes-list">
                <li v-for="note in savedNotes" :key="note.id">
                    {{ note.text }}
                </li>
            </ul>
       </div>
    </div>

  </div>
</template>

<style scoped>
.actions-panel-content {
  padding: 0; /* Remove default padding */
  height: 100%;
  display: flex;
  flex-direction: column; /* Stack sections vertically */
}

h3 {
  margin: 0;
  padding: 15px;
  border-bottom: 1px solid #eee;
  font-size: 1.1em;
  color: #333;
  flex-shrink: 0; /* Prevent shrinking */
}
h4 {
    margin-top: 0;
    margin-bottom: 10px;
    font-size: 1em;
    color: #555;
}

.section {
    padding: 15px;
    border-bottom: 1px solid #eee;
    flex-shrink: 0; /* Prevent sections from shrinking initially */
}
.section:last-child {
    border-bottom: none;
}

/* Styles for the action buttons grid/list */
.action-buttons-section {
    display: grid; /* Use grid for two columns */
    grid-template-columns: 1fr 1fr; /* Two equal columns */
    gap: 10px; /* Spacing between buttons */
}
.action-buttons-section button {
    /* display: block; */ /* Remove if using grid */
    /* width: 100%; */ /* Remove if using grid */
    padding: 10px;
    /* margin-bottom: 10px; */ /* Remove if using grid gap */
    text-align: center; /* Center text */
    background-color: #f8f9fa; /* Very light gray */
    border: 1px solid #dee2e6; /* Light border */
    border-radius: 6px; /* Rounded corners */
    cursor: pointer;
    transition: background-color 0.2s, border-color 0.2s;
    font-size: 0.9em;
    white-space: nowrap; /* Prevent wrapping */
    overflow: hidden;
    text-overflow: ellipsis;
}
.action-buttons-section button:hover {
    background-color: #e9ecef; /* Darken slightly on hover */
    border-color: #ced4da;
}

/* Styles for the notes section */
.notes-section {
    flex-grow: 1; /* Allow this section to take remaining vertical space */
    display: flex;
    flex-direction: column; /* Stack header, textarea, saved notes vertically */
    overflow: hidden; /* Hide overflow for the section itself */
}
.notes-header {
    display: flex;
    justify-content: space-between; /* Space out title and button */
    align-items: center; /* Align items vertically */
    margin-bottom: 10px;
}
.add-note-button {
    padding: 4px 8px;
    font-size: 0.85em;
    background-color: #e9ecef;
    border: 1px solid #ced4da;
    border-radius: 4px;
    cursor: pointer;
}
.add-note-button:hover {
    background-color: #dee2e6;
}

.notes-section textarea {
    width: 100%;
    min-height: 100px; /* Minimum height */
    /* flex-grow: 1; */ /* Let textarea grow initially, but limit */
    max-height: 200px; /* Max height before scrolling */
    padding: 10px;
    border: 1px solid #ced4da;
    border-radius: 4px;
    resize: vertical; /* Allow vertical resize only */
    margin-bottom: 10px;
    box-sizing: border-box; /* Include padding in height */
    font-size: 0.95em;
    line-height: 1.4;
    flex-shrink: 0; /* Prevent shrinking past min-height */
}

/* Area for displaying saved notes */
.saved-notes-area {
    flex-grow: 1; /* Take remaining space */
    overflow-y: auto; /* Allow scrolling if many notes */
    padding-top: 10px;
    margin-top: 10px;
    border-top: 1px solid #eee; /* Separator line */
}

.saved-notes-placeholder {
    padding: 20px;
    background-color: #f8f9fa;
    border: 1px dashed #ced4da;
    border-radius: 4px;
    text-align: center;
    color: #6c757d;
    font-size: 0.9em;
}

.saved-notes-list {
    list-style: none;
    padding: 0;
    margin: 0;
}
.saved-notes-list li {
    background-color: #f8f9fa;
    padding: 8px 12px;
    border-radius: 4px;
    margin-bottom: 8px;
    font-size: 0.9em;
    border: 1px solid #eee;
}

/* Optional: Style for a dedicated save button if re-enabled */
/*
.save-note-button {
    padding: 8px 15px;
    background-color: #28a745;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    align-self: flex-end;
    margin-top: 10px;
}
.save-note-button:hover {
    background-color: #218838;
}
*/
</style>
