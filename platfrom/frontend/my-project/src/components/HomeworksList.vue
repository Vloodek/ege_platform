<template>
  <div id="homeworks">
    <div class="container">
      <!-- Боковое меню -->
      <SideBar :isTestActive="false" />

      <!-- Контент -->
      <main class="main-content">
        <h2>Домашние задания</h2>

        <!-- Фильтр -->
        <div class="filter-container">
          <label for="status-filter">Фильтр по статусу:</label>
          <select id="status-filter" v-model="selectedStatus">
            <option value="">Все</option>
            <option value="graded">Оценено</option>
            <option value="response_received">Получен ответ</option>
            <option value="submitted">Отправлено</option>
            <option value="not_submitted">Не выполнено</option>
          </select>
        </div>

        <!-- Карточки домашних заданий -->
        <div class="task-container">
          <div
            class="task-block"
            v-for="(homework, index) in filteredHomeworks"
            :key="index"
          >
            <!-- Контейнер заголовка с авто-подстройкой размера -->
            <div class="task-header-container">
              <div class="task-header" :class="statusHeaderClass(homework)">
                {{ homework.description }}
              </div>
            </div>
            <div class="task-bottom">
              <!-- Левая часть: дата и статус (иконка со смайликом + текст) -->
              <div class="task-info">
                <div class="task-time">
                  <img
                    src="@/assets/svg/sidebar/calendar.svg"
                    alt="calendar"
                    class="calendar-icon"
                  />
                  <span class="calendar-text">{{ formatTime(homework.date) }}</span>
                </div>
                <div class="task-status" v-if="homework.status">
                  <img :src="getStatusIcon(homework.status)" class="status-icon" />
                  <span class="task-status-text">{{ statusLabel(homework.status) }}</span>
                </div>
              </div>
              <!-- Правая часть: кнопка действия -->
              <BaseButton :color="buttonColor" @click="handleButtonClick(homework)">
                {{ buttonText }}
              </BaseButton>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import SideBar from "./SideBar.vue";
import BaseButton from "@/components/UI/BaseButton.vue";

export default {
  components: {
    SideBar,
    BaseButton,
  },
  data() {
    return {
      homeworks: [],
      selectedStatus: "",
      role: null,
    };
  },
  computed: {
    filteredHomeworks() {
      if (!this.selectedStatus) return this.homeworks;
      return this.homeworks.filter(hw => hw.status === this.selectedStatus);
    },
    buttonText() {
      return this.role === "teacher" ? "Проверить" : "Посмотреть";
    },
    buttonColor() {
      return this.role === "teacher" ? "green" : "green";
    },
  },
  created() {
    // Извлечение объекта пользователя из localStorage и получение роли
    const userData = localStorage.getItem("user");
    if (userData) {
      try {
        const user = JSON.parse(userData);
        this.role = user.role;
      } catch (e) {
        console.error("Ошибка парсинга user из localStorage:", e);
        this.role = "student";
      }
    } else {
      this.role = "student";
    }
    this.fetchHomeworks();
  },
  methods: {
    async fetchHomeworks() {
      try {
        const response = await this.$axios.get("/homeworks/with-status");
        this.homeworks = response.data;
      } catch (error) {
        console.error("Ошибка при загрузке домашних заданий:", error);
      }
    },
    openHomework(homework) {
      if (!homework.lesson_id) return;
      this.$router.push({ name: "homework-details", params: { id: homework.lesson_id } });
    },
    handleButtonClick(homework) {
      this.openHomework(homework);
    },
    formatTime(dateStr) {
      const date = new Date(dateStr);
      const d = String(date.getDate()).padStart(2, "0");
      const m = String(date.getMonth() + 1).padStart(2, "0");
      const y = date.getFullYear();
      const h = String(date.getHours()).padStart(2, "0");
      const min = String(date.getMinutes()).padStart(2, "0");
      return `${d}.${m}.${y} ${h}:${min}`;
    },
    statusLabel(status) {
      switch (status) {
        case "graded": return "Оценено";
        case "submitted": return "Отправлено";
        case "response_received": return "Получен ответ";
        case "not_submitted": return "Не выполнено";
        default: return "Неизвестно";
      }
    },
    getStatusIcon(status) {
      switch (status) {
        case "graded": return require("@/assets/svg/status/graded.svg");
        case "submitted": return require("@/assets/svg/status/submit.svg");
        case "response_received": return require("@/assets/svg/status/nosubmit.svg");
        case "not_submitted": return require("@/assets/svg/status/overdue.svg");
        default: return require("@/assets/svg/status/nosubmit.svg");
      }
    },
    statusHeaderClass(hw) {
      const now = new Date();
      const hwDate = new Date(hw.date);
      if (hwDate < now && hw.status === "not_submitted") {
        return "header-overdue";
      }
      switch (hw.status) {
        case "graded": return "header-graded";
        case "submitted":
        case "response_received": return "header-submitted";
        default: return "";
      }
    },
  },
};
</script>

<style scoped>
/* Общие стили страницы */
#homeworks {
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
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}
h2 {
  text-align: center;
  font-weight: 450;
}

/* Стили фильтра */
.filter-container {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
  align-items: center;
}
.filter-container label {
  font-weight: 500;
}
.filter-container select {
  padding: 5px 12px;
  border: 2px solid #115544;
  border-radius: 8px;
  background-color: #fff;
  font-size: 16px;
  outline: none;
}

/* Карточки домашних заданий */
.task-container {
  margin-bottom: 30px;
}
.task-block {
  padding: 15px;
  margin-bottom: 15px;
  border: 2px solid #115544;
  border-radius: 20px;
  background-color: #fff;

}

/* Контейнер заголовка для подстройки по содержимому */
.task-header-container {
  display: flex;
  justify-content: flex-start;
  /* Если нужно задать отступ сверху/снизу — можно добавить padding */
  margin-bottom: 10px;
}
.task-header {
  display: inline-block; /* чтобы ширина подстраивалась по содержимому */
  padding: 8px 12px;
  font-size: 18px;
  font-weight: 350;
  border-radius: 8px;
  margin-left: 12px;
}
.header-graded {
  background-color: #D2FFF4;
}
.header-submitted {
  background-color: #FFEFCF;
}
.header-overdue {
  background-color: #FFD2D2;
}

/* Нижняя часть карточки */
.task-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  padding: 10px 15px;
}

/* Левая часть: дата и статус */
.task-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.task-time {
  display: flex;
  align-items: center;
  font-size: 16px;
  margin-bottom: 5px;
}
.calendar-icon {
  width: 20px;
  height: 20px;
  margin-right: 8px;
  filter: brightness(0);
  padding-left: 1px;
}
/* Блок для статуса с выравниванием по центру */
.task-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #444;
}
.task-status-text{
  padding-top: 3px;
}

.calendar-text{
  padding-top: 6px;
}
.status-icon {
  width: 23px;
  height: 23px;
  vertical-align: middle;
}
</style>
