<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center">
    <div class="max-w-md w-full bg-white p-8 rounded-lg shadow-lg">
      <h2 class="text-3xl font-bold text-center text-gray-800 mb-6">
        {{ isRegistering ? 'Create Account' : 'Welcome Back' }}
      </h2>
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <div v-if="isRegistering">
          <label for="username" class="block text-sm font-medium text-gray-700">Username</label>
          <input v-model="form.username" type="text" id="username" required class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
        </div>
        <div>
          <label for="email" class="block text-sm font-medium text-gray-700">Email Address</label>
          <input v-model="form.email" type="email" id="email" required class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
        </div>
        <div>
          <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
          <input v-model="form.password" type="password" id="password" required class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
        </div>
        <div v-if="error" class="text-red-500 text-sm text-center">
          {{ error }}
        </div>
        <div>
          <button type="submit" class="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
            {{ isRegistering ? 'Register' : 'Sign In' }}
          </button>
        </div>
      </form>
      <div class="mt-6 text-center">
        <button @click="toggleForm" class="text-sm text-indigo-600 hover:text-indigo-500">
          {{ isRegistering ? 'Already have an account? Sign In' : "Don't have an account? Register" }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '../stores/authStore';

const authStore = useAuthStore();
const isRegistering = ref(false);
const form = ref({ username: '', email: '', password: '' });
const error = ref('');

const toggleForm = () => {
  isRegistering.value = !isRegistering.value;
  error.value = '';
};

const handleSubmit = async () => {
  error.value = '';
  let success = false;
  if (isRegistering.value) {
    success = await authStore.register(form.value.username, form.value.email, form.value.password);
    if (success) {
      isRegistering.value = false; // Switch to login form after successful registration
    } else {
      error.value = 'Registration failed. Please try again.';
    }
  } else {
    success = await authStore.login(form.value.email, form.value.password);
    if (!success) {
      error.value = 'Login failed. Please check your credentials.';
    }
  }
};
</script>
