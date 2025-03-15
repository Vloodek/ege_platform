import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import axios from 'axios';

// Настройка базового URL
axios.defaults.baseURL = 'http://localhost:8000';

let isRefreshing = false;
let refreshSubscribers = [];
let isUnauthorizedHandled = false; // Флаг, чтобы handleUnauthorized вызывался только один раз

function onRefreshed(newToken) {
  refreshSubscribers.forEach(callback => callback(newToken));
  refreshSubscribers = [];
}

function handleUnauthorized() {
  if (!isUnauthorizedHandled) {
    isUnauthorizedHandled = true;
    localStorage.clear();
    if (router.currentRoute.value.name !== 'register') {
      router.push({ name: 'register' }).then(() => {
        window.location.reload();
      });
    }
  }
}

// Интерцептор запроса: для URL '/refresh-token' не добавляем заголовок Authorization
axios.interceptors.request.use((config) => {
  if (config.url && config.url.includes("/refresh-token")) {
    delete config.headers.Authorization;
    return config;
  }
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Интерцептор ответа: обработка 401 и обновление токена
// Интерцептор ответа: обработка 401 и обновление токена
axios.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;
    if (error.response) {
      console.log("Ошибка на сервере:", error.response.status, error.response.data);
      
      // Если запрос к refresh-token возвращает 401, сразу выходим
      if (error.response.status === 401 && originalRequest.url.includes("/refresh-token")) {
        console.log("Refresh token failed, logging out");
        handleUnauthorized();
        return Promise.reject(error);
      }
      
      // Если ошибка 401 для любого другого запроса, пробуем обновить токен
      if (error.response.status === 401) {
        console.log("Ошибка 401: токен протух или недействителен");
        if (!isRefreshing) {
          isRefreshing = true;
          try {
            // Запрос к /refresh-token для обновления токена
            const refreshResponse = await axios.post('/refresh-token', {}, { withCredentials: true });
            const newAccessToken = refreshResponse.data.access_token;

            localStorage.setItem('access_token', newAccessToken);
            axios.defaults.headers.common['Authorization'] = `Bearer ${newAccessToken}`;
            onRefreshed(newAccessToken);

            isRefreshing = false;
            return axios(originalRequest);
          } catch (refreshError) {
            console.log("Ошибка обновления токена, разлогиниваем пользователя", refreshError);
            isRefreshing = false;
            handleUnauthorized();
            return Promise.reject(refreshError);
          }
        }

        return new Promise((resolve) => {
          refreshSubscribers.push((newToken) => {
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            resolve(axios(originalRequest));
          });
        });
      }
    } else if (error.code === 'ERR_NETWORK') {
      console.log('Ошибка сети (ERR_NETWORK)');
    }
    return Promise.reject(error);
  }
);


const app = createApp(App);
app.config.globalProperties.$axios = axios;
app.use(router).mount('#app');
