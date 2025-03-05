<template>
    <div id="user-profile">
      <div class="container">
        <SideBar :isTestActive="false" />
        
        <main class="main-content">
          <h2>Профиль</h2>
  
          <div class="profile-form">
            <div class="form-group">
              <label for="name">Имя:</label>
              <input type="text" id="name" v-model="user.name" disabled />
            </div>
  
            <div class="form-group">
              <label for="email">Почта:</label>
              <input type="email" id="email" v-model="user.email" disabled />
            </div>
  
            <div class="form-group">
              <label for="group">Группа:</label>
              <input type="text" id="group" v-model="user.groupName" disabled />
            </div>
          </div>
  
          <div v-if="user.role === 'teacher'" class="group-actions">
            <input type="text" v-model="newGroupName" placeholder="Название группы" />
            <button @click="createGroup">Создать группу</button>
          </div>
  
          <div v-if="user.role === 'student'" class="group-actions">
            <input type="text" v-model="joinCode" placeholder="Код группы" />
            <button @click="joinGroup">Присоединиться</button>
          </div>
  
        </main>
      </div>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  import SideBar from "@/components/SideBar.vue";
  
  export default {
    components: {
      SideBar,
    },
    data() {
      return {
        user: {
          name: "",
          email: "",
          role: "",
          groupName: "",
        },
        newGroupName: "",
        joinCode: "",
      };
    },
    mounted() {
      this.loadUserData();
    },
    methods: {
      loadUserData() {
        const userData = JSON.parse(localStorage.getItem("user")) || {};
        this.user = {
          name: userData.name || "",
          email: userData.email || "",
          role: userData.role || "student",
          groupName: userData.groupName || "Нет группы",
        };
      },
      async createGroup() {
        try {
          const response = await axios.post("/groups", {
            name: this.newGroupName,
          }, { params: { user_id: localStorage.getItem("user_id") } });
  
          alert(`Группа создана! Код: ${response.data.code}`);
          this.loadUserData();
        } catch (error) {
          alert("Ошибка при создании группы");
        }
      },
      async joinGroup() {
  try {
    const userData = JSON.parse(localStorage.getItem("user"));
    const userId = userData?.userId;

    if (!userId) {
      alert("Ошибка: не удалось получить userId");
      return;
    }

    if (!this.joinCode) {
      alert("Ошибка: введите код группы");
      return;
    }

    const requestData = { user_id: userId };

    console.log("📤 Отправляем запрос:", JSON.stringify(requestData));

    await axios.post(`/groups/join/${this.joinCode}`, requestData, {
      headers: { 
        "Content-Type": "application/json" 
      }
    });

    alert("Вы успешно присоединились к группе!");
    this.loadUserData();
  } catch (error) {
    console.error("❌ Ошибка с сервером:", error.response?.data || error);
    alert("Ошибка при присоединении к группе");
  }
}






,
    },
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
  