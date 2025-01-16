import { createApp, nextTick } from 'vue';
import App from './App.vue';
import router from './router';
import axios from 'axios';

const app = createApp(App);

// Настраиваем базовый URL для Axios
axios.defaults.baseURL = 'http://localhost:8000'; // Замените на ваш адрес API

axios.interceptors.response.use(
    (response) => {
      return response;
    },
    (error) => {
      // Выводим ошибку в консоль для отладки
      console.log('Ошибка в перехватчике Axios', error.response);
  
      if (error.response && error.response.status === 401) {
        console.warn('Ошибка 401. Перенаправляем на /register');
  
        // Удаляем токен и пользователя из localStorage
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
  
        // Используем nextTick для корректного выполнения редиректа
        nextTick(() => {
          router.push('/register').catch((err) => {
            console.error('Ошибка при редиректе на /register:', err);
          });
        });
      }
  
      return Promise.reject(error);
    }
  );
  
  

// Добавляем Axios в глобальный объект Vue
app.config.globalProperties.$axios = axios;

// Подключаем маршрутизацию и монтируем приложение
app.use(router).mount('#app');
