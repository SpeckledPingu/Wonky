<template>
  <nav class="bg-white shadow-md border-b border-gray-200 sticky top-0 z-50">
    <div class="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <div class="flex items-center">
          <router-link to="/" class="flex items-center text-indigo-600 hover:text-indigo-700">
            <Rocket class="h-8 w-8 mr-2" />
            <span class="font-bold text-xl text-gray-800">Wonky</span>
          </router-link>
        </div>

        <div class="hidden md:flex items-center space-x-6">
          <router-link
            to="/"
            class="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100 hover:text-indigo-600 transition-colors"
            active-class="bg-indigo-50 text-indigo-600 font-semibold"
          >
            <LayoutDashboard class="h-4 w-4 mr-1.5 inline-block" />
            Projects
          </router-link>
          <router-link
            to="/stream-builder" class="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100 hover:text-indigo-600 transition-colors"
            active-class="bg-indigo-50 text-indigo-600 font-semibold"
          >
            <Workflow class="h-4 w-4 mr-1.5 inline-block" /> Stream Builder
          </router-link>
          <router-link
            to="/prompts"
            class="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100 hover:text-indigo-600 transition-colors"
            active-class="bg-indigo-50 text-indigo-600 font-semibold"
          >
            <LibraryBig class="h-4 w-4 mr-1.5 inline-block" />
            Prompt Library
          </router-link>
        </div>

        <div class="hidden md:flex items-center">
            <button @click="showUserSettings" title="User Settings" class="p-2 rounded-full text-gray-500 hover:text-indigo-600 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">
                <UserCircle class="h-7 w-7"/>
                <span class="sr-only">User Settings</span>
            </button>
        </div>

        <div class="md:hidden flex items-center">
          <button
            @click="toggleMobileMenu"
            class="inline-flex items-center justify-center p-2 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500"
            aria-controls="mobile-menu"
            :aria-expanded="mobileMenuOpen.toString()"
          >
            <span class="sr-only">Open main menu</span>
            <Menu class="block h-6 w-6" v-if="!mobileMenuOpen" />
            <X class="block h-6 w-6" v-else />
          </button>
        </div>
      </div>
    </div>

    <div :class="{'block': mobileMenuOpen, 'hidden': !mobileMenuOpen}" class="md:hidden border-t border-gray-200" id="mobile-menu">
      <div class="px-2 pt-2 pb-3 space-y-1 sm:px-3">
        <router-link
          to="/"
          @click="closeMobileMenu"
          class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100 hover:text-indigo-600"
          active-class="bg-indigo-50 text-indigo-600"
        >
          <LayoutDashboard class="h-5 w-5 mr-2 inline-block" />
          Projects
        </router-link>
        <router-link
          to="/stream-builder" @click="closeMobileMenu"
          class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100 hover:text-indigo-600"
          active-class="bg-indigo-50 text-indigo-600"
        >
          <Workflow class="h-5 w-5 mr-2 inline-block" />
          Stream Builder
        </router-link>
        <router-link
          to="/prompts"
          @click="closeMobileMenu"
          class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100 hover:text-indigo-600"
          active-class="bg-indigo-50 text-indigo-600"
        >
          <LibraryBig class="h-5 w-5 mr-2 inline-block" />
          Prompt Library
        </router-link>
      </div>
      <div class="pt-3 pb-3 border-t border-gray-200">
          <div class="flex items-center px-4">
              <UserCircle class="h-8 w-8 text-gray-500"/>
              <div class="ml-3">
                  <div class="text-base font-medium text-gray-800">User Name</div>
                  <div class="text-sm font-medium text-gray-500">user@example.com</div>
              </div>
          </div>
          <div class="mt-3 px-2 space-y-1">
              <a href="#" @click.prevent="showUserSettings" class="block px-3 py-2 rounded-md text-base font-medium text-gray-600 hover:text-gray-800 hover:bg-gray-100">Settings</a>
              <a href="#" @click.prevent="logout" class="block px-3 py-2 rounded-md text-base font-medium text-gray-600 hover:text-gray-800 hover:bg-gray-100">Sign out</a>
          </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue';
import { Rocket, Menu, X, LayoutDashboard, LibraryBig, UserCircle, Workflow } from 'lucide-vue-next'; // Added Workflow icon

const mobileMenuOpen = ref(false);

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value;
};

const closeMobileMenu = () => {
  mobileMenuOpen.value = false;
};

const showUserSettings = () => {
    alert("User settings clicked!");
    closeMobileMenu();
}

const logout = () => {
    alert("Logout clicked!");
    closeMobileMenu();
}
</script>

<style scoped>
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
</style>
