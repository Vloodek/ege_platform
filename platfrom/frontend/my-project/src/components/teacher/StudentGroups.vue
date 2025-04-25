<template>
  <div id="student-groups">
    <div class="container">
      <SideBar :isTestActive="false" />
      <main class="main-content">
        <h2>Группы студентов</h2>

        <!-- Контейнер с группами -->
        <div class="groups-container">
          <div class="group-card" v-for="(group, index) in groups" :key="index" @click="selectGroup(group)">
            <div class="group-left">
              <div class="group-name">{{ group.name }}</div>
              <div class="group-code" @click.stop="copyGroupCode(group.code)">
                {{ group.code }}
              </div>
            </div>
          </div>
        </div>

        <!-- Плюсик под карточками -->
        <div v-if="user.role === 'teacher'" class="bottom-create-button">
          <span @click="showCreateGroup = true">+</span>
        </div>

        <!-- Модалка создания группы -->
        <div v-if="showCreateGroup" class="create-group-modal" @click.self="showCreateGroup = false">
          <div class="modal-content">
            <input v-model="newGroupName" placeholder="Название новой группы" class="large-input" />
            <BaseButton :disabled="isCreating" @click="createGroup">Создать</BaseButton>
            <BaseButton color="gray" @click="showCreateGroup = false">Отмена</BaseButton>
          </div>
        </div>

        <!-- Модалка студентов в группе -->
<div v-if="showStudentsModal" class="create-group-modal" @click.self="closeStudentsModal">
  <div class="modal-content students-modal">
    
    <!-- Верхняя панель с кнопкой удаления -->
    <div class="modal-header">
      <h3>Студенты в группе "{{ selectedGroup?.name }}"</h3>
      <BaseButton
        color="red"
        size="small"
        class="delete-icon-btn"
        @click="confirmGroupDelete"
      >
        Удалить
      </BaseButton>
    </div>

    <p class="group-code-display">
      Код группы: <span @click="copyGroupCode(selectedGroup.code)">{{ selectedGroup.code }}</span>
    </p>

    <table class="students-table" style="margin-top: 20px">
      <thead>
        <tr>
          <th>Имя</th>
          <th>Email</th>
          <th>Баллы</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="student in studentsInGroup" :key="student.id">
          <td>{{ student.name }}</td>
          <td>{{ student.email }}</td>
          <td>{{ student.total_points }}</td>
          <td><button class="remove-btn" @click="confirmRemove(student)">×</button></td>
        </tr>
      </tbody>
    </table>

    <div style="text-align: right; margin-top: 20px">
      <BaseButton color="gray" @click="closeStudentsModal">Закрыть</BaseButton>
    </div>
  </div>
</div>


        <!-- Модалка подтверждения удаления -->
        <div v-if="studentToRemove" class="create-group-modal" @click.self="studentToRemove = null">
          <div class="modal-content">
            <p>Вы уверены, что хотите удалить "{{ studentToRemove.name }}" из группы?</p>
            <div style="display: flex; justify-content: flex-end; gap: 10px">
              <BaseButton color="gray" @click="studentToRemove = null">Отмена</BaseButton>
              <BaseButton color="red" @click="removeStudentConfirmed">Удалить</BaseButton>
            </div>
          </div>
        </div>

        <!-- Список студентов под карточками (если не открыта модалка) -->
        <div v-if="selectedGroup && !showStudentsModal" class="students-list">
          <h3>Студенты в группе "{{ selectedGroup?.name }}"</h3>
          <p class="group-code-display">
            Код группы: <span @click="copyGroupCode(selectedGroup.code)">{{ selectedGroup.code }}</span>
          </p>

          <!-- Кнопка удаления группы -->
          <BaseButton color="red" class="delete-group-btn" @click="confirmGroupDelete">
            Удалить группу
          </BaseButton>

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

        <!-- Центрированное сообщение -->
        <div v-if="messageText" :class="['message', messageType]">
          {{ messageText }}
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import SideBar from "../SideBar";
import BaseButton from "@/components/UI/BaseButton.vue";

export default {
  components: { SideBar, BaseButton },

  data() {
    return {
      user: {},
      groups: [],
      selectedGroup: null,
      studentsInGroup: [],
      showCreateGroup: false,
      newGroupName: "",
      showStudentsModal: false,
      isCreating: false,
      messageText: "",
      messageType: "",
      studentToRemove: null,
    };
  },

  mounted() {
    this.loadUserData();
    this.loadGroups();
  },

  methods: {
    loadUserData() {
      const data = JSON.parse(localStorage.getItem("user")) || {};
      this.user = {
        userId: data.userId || "",
        name: data.name || "",
        email: data.email || "",
        role: data.role || "student",
        groupName: data.group_name || "",
        group_id: data.group_id || null,
      };
    },

    async loadGroups() {
      if (!this.user.userId) return;
      try {
        const res = await this.$axios.get("/groups", {
          params: { teacher_id: this.user.userId },
        });
        this.groups = res.data;
      } catch (err) {
        console.error("Ошибка загрузки групп:", err);
      }
    },

    async selectGroup(group) {
      this.selectedGroup = group;
      this.showStudentsModal = true;
      try {
        const res = await this.$axios.get(
          `/groups/${group.id}/users`
        );
        this.studentsInGroup = res.data;
      } catch (err) {
        console.error("Ошибка загрузки студентов:", err);
      }
    },

    confirmGroupDelete() {
      if (!this.selectedGroup) return;
      if (
        confirm(`Удалить группу "${this.selectedGroup.name}"?`)
      ) {
        this.deleteGroup();
      }
    },

    async deleteGroup() {
      try {
        await this.$axios.delete(
          `/groups/${this.selectedGroup.id}`
        );
        this.groups = this.groups.filter(
          (g) => g.id !== this.selectedGroup.id
        );
        this.showMessage("Группа удалена", "success");
        this.closeStudentsModal();
      } catch (err) {
        console.error("Ошибка при удалении группы:", err);
        this.showMessage("Не удалось удалить группу", "error");
      }
    },

    closeStudentsModal() {
      this.showStudentsModal = false;
      this.selectedGroup = null;
      this.studentsInGroup = [];
    },

    confirmRemove(student) {
      this.studentToRemove = student;
    },

    async removeStudentConfirmed() {
      if (!this.studentToRemove || !this.selectedGroup) return;
      try {
        await this.$axios.delete(
          `/groups/${this.selectedGroup.id}/members/${this.studentToRemove.id}`
        );
        this.studentsInGroup = this.studentsInGroup.filter(
          (s) => s.id !== this.studentToRemove.id
        );
        this.showMessage(
          `Студент "${this.studentToRemove.name}" удалён`,
          "success"
        );
      } catch (err) {
        console.error("Ошибка удаления студента:", err);
        this.showMessage(
          "Ошибка при удалении студента",
          "error"
        );
      } finally {
        this.studentToRemove = null;
      }
    },

    async copyGroupCode(code) {
      try {
        await navigator.clipboard.writeText(code);
        this.showMessage("Код скопирован в буфер обмена", "success");
      } catch (err) {
        console.error("Ошибка копирования:", err);
        this.showMessage("Не удалось скопировать код", "error");
      }
    },

    async createGroup() {
      if (this.isCreating) return;
      this.isCreating = true;

      if (!this.newGroupName.trim()) {
        this.showMessage("Введите название группы", "error");
        this.isCreating = false;
        return;
      }

      try {
        const res = await this.$axios.post(
          "/groups",
          { name: this.newGroupName },
          { params: { user_id: this.user.userId } }
        );
        this.showMessage(
          `Группа создана! Код: ${res.data.code}`,
          "success"
        );
        this.loadGroups();
      } catch (err) {
        console.error("Ошибка при создании группы:", err);
        this.showMessage("Ошибка при создании группы", "error");
      } finally {
        this.isCreating = false;
        this.showCreateGroup = false;
        this.newGroupName = "";
      }
    },

    showMessage(text, type = "success") {
      this.messageText = text;
      this.messageType = type;
      setTimeout(() => {
        this.messageText = "";
      }, 4000);
    },
  },
};
</script>

<style scoped>
/* Общие стили */
#student-groups {
  display: flex;
  min-height: 100vh;
  background: #f5f5f5;
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
  background: #fff;
  padding: 20px;
  border-radius: 20px;
  margin-left: 20px;
}

.groups-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.group-card {
  border: 2px solid #56AEF6;
  border-radius: 20px;
  padding: 20px;
  height: 105px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  cursor: pointer;
  transition: border 0.3s ease;
}

.group-card:hover {
  background-color: #b8dfff;
}

.group-name {
  font-size: 20px;
  margin-bottom: 12px;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.group-code {
  font-size: 14px;
  display: inline-block;
  /* ✅ ширина по содержимому */
  background: #f0f0f0;
  padding: 5px 8px;
  border-radius: 5px;
  cursor: pointer;
  max-width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}


/* Плюс под карточками */
.bottom-create-button {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.bottom-create-button span {
  display: inline-block;
  width: 48px;
  height: 48px;
  background: #b8dfff;
  color: white;
  font-size: 32px;
  border-radius: 50%;
  text-align: center;
  line-height: 48px;
  cursor: pointer;
}

.bottom-create-button span:hover {
  background: #b8dfff;
}

/* Модалки */
.create-group-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  backdrop-filter: blur(3px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1001;
}

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  gap: 15px;
  min-width: 300px;
}

.students-modal {
  max-width: 600px;
  width: 100%;
}

.group-code-display {
  margin: 10px 0;
  font-size: 14px;
  color: #666;
}

.group-code-display span {
  text-decoration: underline;
  cursor: pointer;
}

.large-input {
  font-size: 18px;
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 8px;
  width: 90%;
}

/* Студенты */
.students-table {
  width: 100%;
  border-collapse: collapse;
}

.remove-group-btn {
  background: none;
  border: none;
  color: #c00;
  font-size: 22px;
  font-weight: bold;
  cursor: pointer;
  margin-left: 15px;
}


.students-table th,
.students-table td {
  border: 1px solid #56AEF6;
  padding: 10px;
  text-align: left;
}

.students-table thead {
  background: #56AEF6;
  color: white;
}

.students-table tbody tr:nth-child(even) {
  background: #f9f9f9;
}

.remove-btn {
  background: none;
  border: none;
  color: #c00;
  font-size: 18px;
  cursor: pointer;
}

/* Уведомление */
.message {
  position: fixed;
  bottom: 30px;
  /* ✅ отступ снизу */
  left: 50%;
  transform: translateX(-50%);
  padding: 15px 25px;
  border-radius: 10px;
  font-weight: bold;
  z-index: 2000;
  min-width: 250px;
  text-align: center;
  animation: fadeInOut 4s ease-in-out;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}


.message.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

@keyframes fadeInOut {
  0% {
    opacity: 0;
  }

  10% {
    opacity: 1;
  }

  90% {
    opacity: 1;
  }

  100% {
    opacity: 0;
  }
}

.delete-group-btn {
  margin-top: 10px;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.delete-icon-btn {
  font-size: 13px;
  padding: 6px 10px;
  height: auto;
  line-height: 1;
}
.main-content h2 {
  text-align: center;
}

</style>
