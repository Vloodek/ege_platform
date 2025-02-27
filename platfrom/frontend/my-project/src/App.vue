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
          <span class="icon-dropdown" @click="toggleDropdown">&#x25BC;</span>
          <div v-if="dropdownOpen" class="dropdown-menu">
            <ul>
              <li @click="goToProfile">Профиль</li>
              <li @click="logout">Выйти</li>
            </ul>
          </div>
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
import axios from 'axios';

export default {
  data() {
    return {
      isAuthenticated: false,
      userName: 'Гость',
      dropdownOpen: false, // Состояние выпадающего меню
    };
  },
  mounted() {
    console.log('Компонент App загружен');
    
    const user = localStorage.getItem('user');
    console.log('Данные пользователя из localStorage:', user);

    if (user) {
      try {
        const parsedUser = JSON.parse(user);
        if (parsedUser && parsedUser.name) {
          this.userName = parsedUser.name;
          this.isAuthenticated = true;
        } else {
          this.clearLocalStorage();
        }
      } catch (error) {
        this.clearLocalStorage();
      }
    } else {
      this.clearLocalStorage();
    }

    const token = localStorage.getItem('access_token');
    if (token) {
      axios.defaults.headers['Authorization'] = `Bearer ${token}`;
    }

    // Закрытие dropdown при клике вне
    document.addEventListener('click', this.closeDropdownOutside);
  },
  beforeUnmount() {
    document.removeEventListener('click', this.closeDropdownOutside);
  },
  methods: {
    goToDayPlan() {
      this.$router.push('/day-plan');
    },
    goToProfile() {
      this.$router.push('/profile');
      this.dropdownOpen = false;
    },
    logout() {
      console.log('Выход из системы');
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      this.$router.push('/register');
      location.reload(); // Обновляем страницу
    },
    toggleDropdown(event) {
      event.stopPropagation(); // Чтобы не срабатывало на document
      this.dropdownOpen = !this.dropdownOpen;
    },
    closeDropdownOutside(event) {
      if (!this.$el.contains(event.target)) {
        this.dropdownOpen = false;
      }
    },
    clearLocalStorage() {
      console.log('Очищаем localStorage');
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      this.$router.push('/register');
    },
  },
};
</script>


<style scoped>
/* Общие стили */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Navigo', sans-serif;
}

#app {
  height: 100%;
  width: 100%;
  background-color: #F3F3F3;
}

/* Шапка */
.header {
  background-color: #ffffff;
  height: 80px;
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
  cursor: pointer;
}

/* Основной контент */
.content {
  display: flex;
  min-height: calc(100vh - 80px); /* Учитываем высоту шапки */
}

.main-content {
  flex: 1;
  padding: 20px;
  background-color: #F3F3F3;
  border-radius: 8px;
  min-height: 100%;
}
/* Стили для dropdown */
.dropdown-menu {
  position: absolute;
  top: 50px;
  right: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 10px 0;
  width: 150px;
}

.dropdown-menu ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

.dropdown-menu li {
  padding: 10px 15px;
  cursor: pointer;
  font-size: 14px;
  color: #333;
}

.dropdown-menu li:hover {
  background-color: #f0f0f0;
}

.user-info {
  display: flex;
  align-items: center;
  position: relative;
}

.icon-dropdown {
  margin-right: 20px;
  cursor: pointer;
  font-size: 18px;
}
</style>

<style>
/* Глобальные стили */
body {
  margin: 0;
  padding: 0;
  
}
</style>
