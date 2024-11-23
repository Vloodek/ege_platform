<template>
  <div id="app">
    <header class="header">
      <div class="header-container">
        <div class="logo-container">
          <img src="@/assets/svg/logo.svg" alt="Логотип" class="logo" />
          <h1 class="academy-name">АКАДЕМИЯ ИНК</h1>
        </div>
        <div class="user-info">
          <span class="user-name">{{ isAuthenticated ? userName : 'Гость' }}</span>
          <span class="icon-dropdown">&#x25BC;</span>
          <img 
            src="@/assets/svg/home-icon.svg" 
            alt="Домик" 
            class="home-icon"
            @click="goToDayPlan"
          />
        </div>
      </div>
    </header>

    <div class="content">
      <main class="main-content">
        <router-view></router-view>
      </main>
    </div>
  </div>
</template>


<script>
export default {
  data() {
    return {
      isAuthenticated: false,
      userName: 'Гость', // Значение по умолчанию, если пользователь не найден
    };
  },
  mounted() {
    const user = localStorage.getItem('user');
    if (user) {
      try {
        const parsedUser = JSON.parse(user);

        // Проверяем, что у объекта есть поле `name`
        if (parsedUser && parsedUser.name) {
          this.userName = parsedUser.name; // Устанавливаем имя пользователя
          this.isAuthenticated = true;
        } else {
          console.warn("Имя пользователя не найдено в данных.");
          this.$router.push('/register'); // Перенаправляем, если данные некорректны
        }
      } catch (error) {
        console.error("Ошибка при парсинге данных из localStorage:", error);
        this.$router.push('/register');
      }
    } else {
      console.warn("Пользователь не найден в localStorage.");
      this.$router.push('/register');
    }
  },
  methods: {
    goToDayPlan() {
      this.$router.push('/day-plan'); // Переход на страницу с планом на день
    },
  },
};
</script>


<style scoped>
/* Общие стили для сброса */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Navigo', sans-serif;
}

html, body {
  height: 100%;
  margin: 0;
  padding: 0;
  background-color: #f3f3f3;
}

#app {
  height: 100%;
  background-color: #F3F3F3;
}

/* Шапка */
.header {
  background-color: #ffffff;
  height: 80px;
  width: 100%;
  display: flex;
  justify-content: center;
  padding: 0 20px;
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  max-width: 1200px;
}

.logo-container {
  display: flex;
  align-items: center;
}

.logo {
  width: 40px;
  height: auto;
  margin-right: 10px;
}

.academy-name {
  font-size: 24px;
  font-weight: bold;
  color: #115544;
}

.user-info {
  display: flex;
  align-items: center;
}

.user-name {
  margin-right: 6px;
  font-size: 16px;
  color: #333;
}

.icon-dropdown {
  margin-right: 20px;
  cursor: pointer;
  font-size: 18px;
}

.home-icon {
  width: 24px;
  height: auto;
  cursor: pointer;
}

/* Основной контент */
.content {
  display: flex;
  min-height: calc(100vh - 80px); /* Подгоняем высоту контента с учетом высоты шапки */
}

/* Основной контент */
.main-content {
  flex: 1;
  padding: 20px;
  background-color: #F3F3F3;
  border-radius: 8px;
  min-height: 100%;
}
</style>
