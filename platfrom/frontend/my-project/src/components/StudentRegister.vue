<template>
  <div>
    <h1>{{ isLogin ? 'Вход' : 'Регистрация' }}</h1>
    <form @submit.prevent="handleSubmit">
      <div>
        <label for="email">Email:</label>
        <input v-model="email" type="email" id="email" required />
      </div>
      <div>
        <label for="password">Пароль:</label>
        <input v-model="password" type="password" id="password" required />
      </div>
      <div v-if="!isLogin">
        <label for="name">Имя:</label>
        <input v-model="name" type="text" id="name" required />
      </div>
      <button type="submit" :disabled="isSubmitting">{{ isLogin ? 'Войти' : 'Зарегистрироваться' }}</button>
    </form>

    <p v-if="error" style="color: red;">{{ error }}</p>
    <p v-if="success" style="color: green;">{{ isLogin ? 'Добро пожаловать!' : 'Регистрация успешна!' }}</p>

    <p>
      <span v-if="isLogin">Нет аккаунта? <a href="#" @click="toggleForm">Зарегистрироваться</a></span>
      <span v-else>Есть аккаунт? <a href="#" @click="toggleForm">Войти</a></span>
    </p>
  </div>
</template>

<script>
import axios from 'axios';
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);
export default {
  data() {
    return {
      name: '',
      email: '',
      password: '',
      success: false,
      error: null,
      isSubmitting: false,
      isLogin: false,  // Флаг для переключения между формами регистрации и входа
    };
  },
  methods: {
    async handleSubmit() {
  this.error = null;
  this.success = false;
  this.isSubmitting = true;

  const url = this.isLogin ? 'http://localhost:8000/login' : 'http://localhost:8000/register';
  const data = this.isLogin
    ? { email: this.email, password: this.password }
    : {
        name: this.name,
        email: this.email,
        password: this.password,
      };

  try {
    const response = await axios.post(url, data);
    console.log(response.data); // Вывод данных из ответа сервера

    this.success = true;

    // Сохраняем токен и данные пользователя
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem(
      'user',
      JSON.stringify({ name: response.data.name, role: response.data.role }) // Сохраняем роль
    );

    // Перенаправление на главную страницу
    this.$nextTick(() => {
      this.$router.push('/');
    });
  } catch (err) {
    this.error = 'Ошибка: ' + (err.response ? err.response.data.detail : 'Неизвестная ошибка');
  } finally {
    this.isSubmitting = false;
  }
}
,
    toggleForm() {
      this.isLogin = !this.isLogin;
    }
  },
  mounted() {
  const isLoggedIn = localStorage.getItem('access_token');
  if (isLoggedIn) {
    const user = JSON.parse(localStorage.getItem('user'));
    if (user) {
      this.userName = user.name;  // Извлекаем имя пользователя
    }

    // Перенаправляем на главную страницу
    this.$nextTick(() => {
      this.$router.push('/');  // Перенаправление на страницу StudentCalendar
    });
  }
}

};
</script>


<style scoped>
form {
  display: flex;
  flex-direction: column;
  max-width: 300px;
  margin: 0 auto;
}

input {
  margin-bottom: 10px;
  padding: 8px;
}

button {
  padding: 10px;
  background-color: #4CAF50;
  color: white;
  border: none;
  cursor: pointer;
}

button:disabled {
  background-color: #cccccc;
}

button:hover {
  background-color: #45a049;
}

p {
  font-size: 14px;
}
</style>
