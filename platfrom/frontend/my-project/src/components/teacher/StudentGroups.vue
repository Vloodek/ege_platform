<template>
    <div id="student-groups">
      <div class="container">
        <SideBar :isTestActive="false" />
    
        <main class="main-content">
          <h2>Мои группы</h2>
    
          <!-- Контейнер для блоков с группами -->
          <div class="groups-container">
            <!-- Блоки с группами -->
            <div
              class="group-card"
              v-for="(group, index) in groups"
              :key="index"
              @click="selectGroup(group)"
            >
              <div class="group-left">
                <div class="group-name">{{ group.name }}</div>
                <div class="group-code" @click.stop="copyGroupCode(group.code)">{{ group.code }}</div>
              </div>
            </div>
          </div>
  
          <!-- Форма создания группы для преподавателя -->
          <div v-if="user.role === 'teacher'" class="group-create">
            <input type="text" v-model="newGroupName" placeholder="Название новой группы" />
            <BaseButton :disabled="isCreating" @click="createGroup">Создать группу</BaseButton>
          </div>
  
          <!-- Студенты в выбранной группе -->
          <div v-if="selectedGroup" class="students-list">
            <h3>Студенты в группе {{ selectedGroup.name }}</h3>
            <table class="students-table">
              <thead>
                <tr>
                  <th>Имя</th>
                  <th>Email</th>
                  <th>Баллы</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="student in studentsInGroup" :key="student.id">
                  <td>{{ student.name }}</td>
                  <td>{{ student.email }}</td>
                  <td>{{ student.total_points }}</td>
                </tr>
              </tbody>
            </table>
          </div>
    
          <!-- Уведомление о копировании кода -->
          <div v-if="copied" class="toast">Код скопирован в буфер обмена</div>
  
          <!-- Сообщение для преподавателя после создания группы -->
          <div v-if="messageText" :class="['message', messageType]">
            {{ messageText }}
          </div>
        </main>
      </div>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  import SideBar from "../SideBar";
  import BaseButton from "@/components/UI/BaseButton.vue";
  
  export default {
    components: { SideBar, BaseButton },
    data() {
      return {
        user: {
          userId: "",
          name: "",
          email: "",
          role: "student",
          groupName: "Нет группы",
          group_id: null,
        },
        newGroupName: "",
        groups: [],
        selectedGroup: null,
        studentsInGroup: [],
        copied: false,
        messageText: "",
        messageType: "", // "success" или "error"
        isCreating: false, // Флаг для блокировки кнопки при создании группы
      };
    },
  
    mounted() {
      this.loadUserData();
      this.loadGroups();
    },
  
    methods: {
      loadUserData() {
        try {
          const userData = JSON.parse(localStorage.getItem("user")) || {};
          this.user = {
            userId: userData.userId || "",
            name: userData.name || "",
            email: userData.email || "",
            role: userData.role || "student",
            groupName: userData.group_name || "Нет группы",
            group_id: userData.group_id || null,
          };
        } catch (error) {
          console.error("Ошибка загрузки данных пользователя:", error);
        }
      },
  
      // Загрузка групп
      async loadGroups() {
        try {
          const userData = JSON.parse(localStorage.getItem("user")) || {};
          if (!userData.userId) return;
  
          const response = await axios.get(`/groups?teacher_id=${userData.userId}`);
          this.groups = response.data;
        } catch (error) {
          console.error("Ошибка загрузки групп:", error);
        }
      },
  
      // Выбор группы
      async selectGroup(group) {
        this.selectedGroup = group;
        try {
          const response = await axios.get(`/groups/${group.id}/users`);
          this.studentsInGroup = response.data;
        } catch (error) {
          console.error("Ошибка при загрузке студентов:", error);
        }
      },
  
      // Копирование кода группы
      async copyGroupCode(code) {
        try {
          await navigator.clipboard.writeText(code);
          this.copied = true;
          setTimeout(() => (this.copied = false), 2000);
        } catch (error) {
          console.error("Ошибка копирования:", error);
        }
      },
  
      // Создание новой группы
      async createGroup() {
        if (this.isCreating) return; // Игнорировать повторные клики
  
        this.isCreating = true; // Блокируем кнопку
  
        if (!this.newGroupName.trim()) {
          this.messageText = "Введите название группы";
          this.messageType = "error";
          this.isCreating = false;
          return;
        }
  
        if (!this.user.userId) {
          this.messageText = "Ошибка: не удалось получить ID пользователя";
          this.messageType = "error";
          this.isCreating = false;
          return;
        }
  
        try {
          const response = await axios.post(
            "/groups",
            { name: this.newGroupName },
            { params: { user_id: this.user.userId } }
          );
          this.messageText = `Группа "${this.newGroupName}" создана! Код: ${response.data.code}`;
          this.messageType = "success";
          this.loadGroups();
        } catch (error) {
          console.error("Ошибка при создании группы:", error);
          this.messageText = "Ошибка при создании группы. Попробуйте снова.";
          this.messageType = "error";
        } finally {
          this.isCreating = false; // Разблокируем кнопку
          // Убираем сообщение через 5 секунд
          setTimeout(() => {
            this.messageText = "";
          }, 5000);
        }
      }
    }
  };
  </script>
  
  <style scoped>
  /* Основной контейнер */
  #student-groups {
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
    font-size: 24px;
    margin-bottom: 20px;
    color: #333;
    text-align: center;
  }
  
  .groups-container {
    margin-bottom: 30px;
  }
  
  .group-card {
    display: flex;
    flex-direction: column;
    padding: 20px;
    margin-bottom: 15px;
    justify-content: space-between;
    height: 105px;
    cursor: pointer;
    border: 2px solid #115544;
    border-radius: 20px;
    transition: border 0.3s ease;
  }
  
  .group-card:hover {
    border: 2px solid #1e9275;
  }
  
  .group-left {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
  }
  
  .group-name {
    font-size: 20px;
    color: #333;
    font-weight: light;
    margin-bottom: 12px;
    text-overflow: ellipsis;
    overflow: hidden;
    white-space: nowrap;
  }
  
  .group-code {
    font-size: 14px;
    background-color: #f0f0f0;
    padding: 5px;
    border-radius: 5px;
    cursor: pointer;
  }
  
  .students-list {
    margin-top: 20px;
  }
  
  .students-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
  }
  
  .students-table th,
  .students-table td {
    border: 1px solid #115544;
    padding: 10px;
    text-align: left;
  }
  
  .students-table thead {
    background-color: #115544;
    color: #fff;
  }
  
  .students-table tbody tr:nth-child(even) {
    background-color: #f9f9f9;
  }
  
  .toast {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    background-color: #28a745;
    color: white;
    padding: 10px 15px;
    border-radius: 5px;
    font-size: 14px;
    animation: fadeInOut 2s ease-in-out;
  }
  
  @keyframes fadeInOut {
    0% { opacity: 0; }
    20% { opacity: 1; }
    80% { opacity: 1; }
    100% { opacity: 0; }
  }
  
  /* Сообщения об успехе и ошибке */
  .message {
    padding: 10px;
    margin: 10px 0;
    border-radius: 5px;
    font-weight: bold;
    text-align: center;
  }
  
  .message.success {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
  }
  
  .message.error {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
  }
  
  .group-create {
    margin-top: 20px;
    display: flex;
    gap: 10px;
  }
  </style>
  