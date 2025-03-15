<template>
  <div v-if="isVisible" class="modal-overlay">
    <div class="modal">
      <h3>Список групп</h3>
      <table class="group-table">
        <thead>
          <tr>
            <th>Название</th>
            <th>Код группы</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="group in groups" :key="group.id">
            <td @click="selectGroup(group)" class="group-name">{{ group.name }}</td>
            <td @click="copyGroupCode(group.code)" class="group-code">{{ group.code }}</td>
          </tr>
        </tbody>
      </table>
      <BaseButton @click="closeModal">Закрыть</BaseButton>
      
      <!-- Всплывающее уведомление -->
      <div v-if="copied" class="toast">Код скопирован в буфер обмена</div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import BaseButton from "@/components/UI/BaseButton.vue";

export default {
  components: { BaseButton },
  props: {
    isVisible: { type: Boolean, required: true },
    closeModal: { type: Function, required: true },
    onSelectGroup: { type: Function, required: true }
  },
  data() {
    return {
      groups: [],
      copied: false
    };
  },
  watch: {
    isVisible(newValue) {
      if (newValue) {
        this.loadGroups();
      }
    }
  },
  methods: {
    async loadGroups() {
      try {
        const response = await axios.get("/groups");
        this.groups = response.data;
      } catch (error) {
        console.error("Ошибка при загрузке групп:", error);
      }
    },
    selectGroup(group) {
      this.onSelectGroup(group);
      this.closeModal();
    },
    async copyGroupCode(code) {
      try {
        await navigator.clipboard.writeText(code);
        this.copied = true;
        setTimeout(() => (this.copied = false), 2000);
      } catch (error) {
        console.error("Ошибка копирования:", error);
      }
    }
  }
};
</script>

<style scoped>
/* Модальное окно */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  width: 450px;
  max-height: 80%;
  overflow-y: auto;
  position: relative;
}

.modal h3 {
  text-align: center;
  margin-bottom: 15px;
  font-weight: normal;
}

/* Таблица */
.group-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 15px;
}

.group-table th, .group-table td {
  padding: 10px;
  border: 1px solid #ccc;
  text-align: left;
  font-weight: normal;
}

.group-table th {
  background-color: #115544;
  color: white;
}

/* Название группы */
.group-name {
  cursor: pointer;
  color: #115544;
  font-weight: normal;
}

.group-name:hover {
  text-decoration: underline;
}

/* Код группы */
.group-code {
  cursor: pointer;
  text-align: center;
  font-family: monospace;
  font-size: 18px; /* Увеличенный размер текста */
  background-color: #f8f8f8;
  transition: background 0.3s, color 0.3s;
}

.group-code:hover {
  background-color: #d4edda;
  color: #115544;
}

/* Всплывающее уведомление */
.toast {
  position: absolute;
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

/* Анимация для уведомления */
@keyframes fadeInOut {
  0% { opacity: 0; }
  20% { opacity: 1; }
  80% { opacity: 1; }
  100% { opacity: 0; }
}
</style>
