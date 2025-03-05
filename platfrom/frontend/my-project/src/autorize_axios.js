import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  // Другие настройки, если необходимо
});

// Перехватчик ответов
api.interceptors.response.use(
  response => response, // Возвращаем успешный ответ
  error => {
    if (error.response) {
      // Сервер вернул код состояния, отличный от 2xx
      if (error.response.status === 401) {
        // Очистить localStorage
        localStorage.clear();
        // Перенаправить пользователя на страницу входа
        window.location.href = '/login';
      }
    } else if (error.request) {
      // Запрос был сделан, но ответ не получен
      console.error('Ошибка сети:', error.request);
    } else {
      // Произошла ошибка при настройке запроса
      console.error('Ошибка:', error.message);
    }
    return Promise.reject(error);
  }
);

export default api;
