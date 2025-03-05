import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import axios from 'axios';

// Настройка базового URL
axios.defaults.baseURL = 'http://localhost:8000';

// Флаг для предотвращения повторной обработки ошибки 401
let isUnauthorizedHandled = false;

axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
      config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

axios.interceptors.response.use(
  response => response,
  error => {
      if (error.response) {
          console.log("Ошибка на сервере:", error.response.status, error.response.data);
          if (error.response.status === 401) {
              console.log("Ошибка 401, токен протух");
              handleUnauthorized();
          }
      } else if (error.code === 'ERR_NETWORK') {
          console.log('Ошибка сети (ERR_NETWORK)');
      }
      return Promise.reject(error);
  }
);

function handleUnauthorized() {
  if (!isUnauthorizedHandled) {
      isUnauthorizedHandled = true;
      localStorage.clear();
      if (router.currentRoute.value.name !== 'login') {
          router.push({ name: 'login' }).then(() => {
              window.location.reload();
          });
      }
  }
}






const app = createApp(App);

// Добавляем Axios в глобальный объект Vue
app.config.globalProperties.$axios = axios;

// Подключаем маршрутизацию и монтируем приложение
app.use(router).mount('#app');
