<template>
  <div id="user-profile">
    <div class="container">
      <SideBar :is-test-active="false" />

      <main class="main-content">
        <h2>Профиль</h2>

        <!-- Блок сообщений -->
        <div
          v-if="messageText"
          :class="['message', messageType]"
        >
          {{ messageText }}
        </div>

        <!-- Форма профиля -->
        <div class="profile-form">
          <div class="form-group">
            <label for="name">Имя:</label>
            <input
              id="name"
              v-model="user.name"
              type="text"
              disabled
            >
          </div>

          <div class="form-group">
            <label for="email">Почта:</label>
            <input
              id="email"
              v-model="user.email"
              type="email"
              disabled
            >
          </div>

          <div class="form-group">
            <label for="group">Группа:</label>
            <input
              id="group"
              v-model="user.group_name"
              type="text"
              disabled
            >
          </div>
        </div>

        <!-- Для студента: форма для вступления в группу -->
        <div
          v-if="user.role === 'student' && !user.group_id"
          class="join-group"
        >
          <h3>Вступить в группу</h3>
          <input
            v-model="joinGroupCode"
            type="text"
            placeholder="Введите код группы"
          >
          <BaseButton @click="joinGroup">
            Вступить
          </BaseButton>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import SideBar from "@/components/SideBar.vue";
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
        group_name: "Нет группы",
        group_id: null,
      },
      joinGroupCode: "",
      messageText: "",
      messageType: "", // "success" или "error"
    };
  },

  mounted() {
    this.loadUserData();
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
          group_name: userData.group_name || "Нет группы",
          group_id: userData.group_id || null,
        };
      } catch (error) {
        console.error("Ошибка загрузки данных пользователя:", error);
      }
    },

    async joinGroup() {
      if (!this.joinGroupCode.trim()) {
        this.messageText = "Введите код группы";
        this.messageType = "error";
        return;
      }

      if (!this.user.userId) {
        this.messageText = "Ошибка: не удалось получить ID пользователя";
        this.messageType = "error";
        return;
      }

      try {
        const response = await this.$axios.post(
          `/groups/join/${this.joinGroupCode}`,
          { user_id: this.user.userId }
        );
        this.messageText = response.data.message;
        this.messageType = "success";

        // Обновляем данные в localStorage
        const storedUser = JSON.parse(localStorage.getItem("user")) || {};
        storedUser.group_id = response.data.group_id;
        storedUser.group_name = response.data.group_name;
        localStorage.setItem("user", JSON.stringify(storedUser));

        // Обновляем данные в компоненте
        this.user.group_id = response.data.group_id;
        this.user.group_name = response.data.group_name;
      } catch (error) {
        console.error("Ошибка при вступлении в группу:", error);
        this.messageText = "Ошибка при вступлении в группу. Проверьте код и попробуйте снова.";
        this.messageType = "error";
      }
    },
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

.message {
  padding: 10px;
  margin: 10px 0;
  border-radius: 5px;
  font-weight: bold;
  text-align: center;
}

/* Успешное сообщение */
.message.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

/* Сообщение об ошибке */
.message.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
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

.group-actions {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.group-create {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

/* Секция для вступления в группу (для студентов) */
.join-group {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.join-group input {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

/* Таблица студентов в зеленых тонах */
.students-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
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
</style>
