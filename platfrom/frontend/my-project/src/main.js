// src/main.js
import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

const app = createApp(App);
app.use(router);  // Используем Vue Router
app.mount('#app');
