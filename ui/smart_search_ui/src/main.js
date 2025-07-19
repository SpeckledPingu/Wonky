import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import './style.css'

// Create the Vue application instance
const app = createApp(App)

// --- FIX ---
// Create the Pinia instance for state management
const pinia = createPinia()
app.use(pinia)

// Mount the application to the DOM
app.mount('#app')
