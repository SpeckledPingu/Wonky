import { createApp } from 'vue'
import './style.css' // Import Tailwind CSS
import App from './App.vue'
import router from './router'
import * as LucideIcons from 'lucide-vue-next';


const app = createApp(App)

// Register all Lucide icons globally
for (const [name, component] of Object.entries(LucideIcons)) {
    app.component(name, component);
  }

app.use(router)
app.mount('#app')
