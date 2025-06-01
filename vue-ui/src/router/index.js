import { createRouter, createWebHistory } from 'vue-router'
import ProjectsView from '../views/ProjectsView.vue'
import ProjectSetupView from '../views/ProjectSetupView.vue'
import ResearchView from '../views/ResearchView.vue'
import PromptLibraryView from '../views/PromptLibraryView.vue'
import ResearchStreamBuilderView from '../views/ResearchStreamBuilderView.vue' // Import the new view

const routes = [
  {
    path: '/',
    name: 'ProjectsView',
    component: ProjectsView,
    meta: { title: 'Research Workspace' }
  },
  {
    path: '/setup/:projectId/:projectName',
    name: 'ProjectSetupView',
    component: ProjectSetupView,
    props: true,
    meta: { title: 'Setup Research' }
  },
  {
    path: '/research/:projectId/:projectName',
    name: 'ResearchView',
    component: ResearchView,
    props: true,
    meta: { title: 'Research Project' }
  },
  {
    path: '/prompts',
    name: 'PromptLibraryView',
    component: PromptLibraryView,
    meta: { title: 'Prompt Library' }
  },
  { // New route for the Research Stream Builder
    path: '/stream-builder',
    name: 'ResearchStreamBuilderView',
    component: ResearchStreamBuilderView,
    meta: { title: 'Research Stream Builder' }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title || 'Research App';
  next();
});

export default router
