<template>
    <div id="user-profile">
      <div class="container">
        <!-- Боковое меню -->
        <SideBar :isTestActive="false" />
        
        <!-- Основной контент с профилем пользователя -->
        <main class="main-content">
          <h2>Профиль</h2>
          
          <div class="profile-form">
            <div class="form-group">
              <label for="name">Имя:</label>
              <input type="text" id="name" v-model="user.name" :disabled="!isEditing" />
            </div>
            
            <div class="form-group">
              <label for="email">Почта:</label>
              <input type="email" id="email" v-model="user.email" disabled />
            </div>
            
            <div class="form-group">
              <label for="group">Группа:</label>
              <input type="text" id="group" v-model="user.group" :disabled="!isEditing" />
            </div>
          </div>
          
          <div class="button-container">
            <button :class="{ 'active': isEditing }" @click="saveProfile" :disabled="!isEditing">Сохранить</button>
            <button @click="toggleEdit">{{ isEditing ? 'Отменить' : 'Изменить' }}</button>
            <button @click="changePassword">Изменить пароль</button>
          </div>
        </main>
      </div>
    </div>
  </template>
  
  <script>
  import SideBar from "@/components/SideBar.vue";
  
  export default {
    components: {
      SideBar,
    },
    data() {
      return {
        isEditing: false,
        user: {
          name: '',
          email: '',
          group: ''
        }
      };
    },
    mounted() {
      this.loadUserData();
    },
    methods: {
      loadUserData() {
        const userData = JSON.parse(localStorage.getItem('user')) || {};
        this.user.name = userData.name || '';
        this.user.email = userData.email || '';
        this.user.group = userData.group || '';
      },
      toggleEdit() {
        this.isEditing = !this.isEditing;
        if (!this.isEditing) {
          this.loadUserData();
        }
      },
      saveProfile() {
        localStorage.setItem('user', JSON.stringify(this.user));
        this.isEditing = false;
        alert('Профиль сохранен!');
      },
      changePassword() {
        this.$router.push('/change-password');
      }
    }
  };
  </script>
  
  <style scoped>
  #user-profile {
    display: flex;
    min-height: 100vh;
    background-color: #f5f5f5;
  }
  
  .container {
    display: flex;
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
  }
  
  .main-content {
    flex: 1;
    background-color: #fff;
    padding: 20px;
    border-radius: 20px;
    margin-left: 20px;
  }
  
  h2 {
    text-align: center;
    margin-bottom: 20px;
  }
  
  .profile-form {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
  }
  
  .form-group {
    display: flex;
    flex-direction: column;
  }
  
  label {
    font-size: 14px;
    margin-bottom: 5px;
  }
  
  input {
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 5px;
  }
  
  .button-container {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin-top: 20px;
  }
  
  button {
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    background-color: #ccc;
    color: white;
  }
  
  button.active {
    background-color: #115544;
  }
  
  button:hover {
    opacity: 0.8;
  }
  </style>
  