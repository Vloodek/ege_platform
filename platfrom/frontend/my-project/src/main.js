import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import axios from 'axios';

// Настройка базового URL
axios.defaults.baseURL = 'http://localhost:8000';

// Флаг для предотвращения повторной обработки ошибки 401
let isUnauthorizedHandled = false;

axios.interceptors.response.use(
  response => response,
  error => {
    console.error('❌ Ошибка Axios:', error);

    // Если сервер вернул ответ, проверяем код
    if (error.response) {
      const status = error.response.status;
      if (status === 401) {
        handleUnauthorized();
      } else {
        console.error('Ошибка с сервером:', status);
      }
    } else if (error.message === 'Network Error') {
      // Если нет ответа от сервера (например, из-за CORS или недоступности)
      console.error('Ошибка сети. Очистка токена и переход на страницу логина');
      handleUnauthorized();
    } else {
      console.error('Неизвестная ошибка:', error);
    }

    return Promise.reject(error);
  }
);

function handleUnauthorized() {
  if (!isUnauthorizedHandled) {
    isUnauthorizedHandled = true;
    // Удаляем только те данные, которые отвечают за авторизацию
    // localStorage.removeItem('access_token');
    // localStorage.removeItem('user');
    localStorage.clear()

    // Если мы не на странице логина, перенаправляем пользователя туда
    if (router.currentRoute.value.name !== 'login') {
      router.push({ name: 'login' }).then(() => {
        window.location.reload(); // Принудительно обновляем страницу
      });
    }
  }
}






const app = createApp(App);

// Добавляем Axios в глобальный объект Vue
app.config.globalProperties.$axios = axios;

// Подключаем маршрутизацию и монтируем приложение
app.use(router).mount('#app');
