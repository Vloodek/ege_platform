<template>
  <div class="auth-container">
    <div class="auth-form">
      <h1>{{ isLogin ? 'Вход' : 'Регистрация' }}</h1>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="email">Email:</label>
          <input v-model="email" type="email" id="email" required />
        </div>
        <div class="form-group">
          <label for="password">Пароль:</label>
          <input v-model="password" type="password" id="password" required />
        </div>
        <div v-if="!isLogin" class="form-group">
          <label for="name">Имя:</label>
          <input v-model="name" type="text" id="name" required />
        </div>
        <button type="submit" :disabled="isSubmitting">{{ isLogin ? 'Войти' : 'Зарегистрироваться' }}</button>
      </form>

      <p v-if="error" class="error-message">{{ error }}</p>
      <p v-if="success" class="success-message">{{ isLogin ? 'Добро пожаловать!' : 'Регистрация успешна!' }}</p>

      <p>
        <span v-if="isLogin">Нет аккаунта? <a href="#" @click="toggleForm">Зарегистрироваться</a></span>
        <span v-else>Есть аккаунт? <a href="#" @click="toggleForm">Войти</a></span>
      </p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  data() {
    return {
      name: '',
      email: '',
      password: '',
      success: false,
      error: null,
      isSubmitting: false,
      isLogin: false,
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

    const { access_token, name, role, id, group_id } = response.data;

    localStorage.setItem('access_token', access_token);
    localStorage.setItem(
      'user',
      JSON.stringify({ name, role, userId: id, ...(group_id ? { group_id } : {}) })
    );

    this.$router.push('/');  // Перенаправление на главную страницу
  } catch (err) {
    this.error = 'Ошибка: ' + (err.response ? err.response.data.detail : 'Неизвестная ошибка');
  } finally {
    this.isSubmitting = false;
  }
}

,
    toggleForm() {
      this.isLogin = !this.isLogin;
    },
  },
  mounted() {
    const isLoggedIn = localStorage.getItem('access_token');
    if (isLoggedIn) {
      const user = JSON.parse(localStorage.getItem('user'));
      if (user) {
        this.userName = user.name;  // Извлекаем имя пользователя
      }

      this.$nextTick(() => {
        this.$router.push('/');  // Перенаправление на страницу StudentCalendar
      });
    }
  }
};
</script>

<style scoped>
/* Основной контейнер для центрирования формы */
.auth-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  height: 100vh;
  background-color: #f4f4f4;
  margin: 0;
  padding-top: 60px; /* Добавляем отступ сверху */
}

/* Стили для формы */
.auth-form {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px; /* Ограничиваем максимальную ширину */
}

h1 {
  text-align: center;
  margin-bottom: 20px;
}

form {
  display: flex;
  flex-direction: column;
}

.form-group {
  margin-bottom: 15px;
}

input {
  width: 90%; /* Ширина поля ввода на всю доступную ширину */
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

button {
  padding: 12px;
  background-color: #4CAF50;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 4px;
}

button:disabled {
  background-color: #cccccc;
}

button:hover {
  background-color: #45a049;
}

.error-message {
  color: red;
  text-align: center;
  margin-top: 10px;
}

.success-message {
  color: green;
  text-align: center;
  margin-top: 10px;
}

p {
  font-size: 14px;
  text-align: center;
}

a {
  color: #4CAF50;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}
</style>
