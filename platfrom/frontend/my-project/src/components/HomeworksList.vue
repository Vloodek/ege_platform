<template>
  <div id="homeworks">
    <div class="container">
      <SideBar :isTestActive="false" />
      <main class="main-content">
        <h2>Домашние задания</h2>

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

        <div class="task-container">
          <div
            class="task-block"
            v-for="(homework, index) in filteredHomeworks"
            :key="index"
          >
            <div class="task-header-container">
              <div class="task-header" :class="statusHeaderClass(homework)">
                {{ homework.description }}
              </div>
            </div>
            <div class="task-bottom">
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
  components: { SideBar, BaseButton },

  data() {
    return {
      homeworks: [],
      selectedStatus: "",
      role: "student",
      groupId: null,
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
      return "green";
    },
  },

  created() {
    const userData = localStorage.getItem("user");
    if (userData) {
      try {
        const user = JSON.parse(userData);
        this.role = user.role || "student";
        this.groupId = user.group_id || null;
      } catch (e) {
        console.error("Ошибка парсинга user:", e);
      }
    }
    this.fetchHomeworks();
  },

  methods: {
    async fetchHomeworks() {
      const params = {};
      if (this.role !== "teacher") {
        if (!this.groupId) {
          console.error("Группа пользователя не найдена.");
          return;
        }
        params.group_id = this.groupId;
      }
      try {
        const { data } = await this.$axios.get("/homeworks/", { params });
        this.homeworks = data;
      } catch (err) {
        console.error("Ошибка при загрузке домашних заданий:", err);
      }
    },

    openHomework(hw) {
      if (!hw.lesson_id) return;
      this.$router.push({ name: "homework-details", params: { id: hw.lesson_id } });
    },
    handleButtonClick(hw) {
      this.openHomework(hw);
    },

    formatTime(dateStr) {
      const d = new Date(dateStr);
      const dd = String(d.getDate()).padStart(2, "0");
      const mm = String(d.getMonth() + 1).padStart(2, "0");
      const yy = d.getFullYear();
      const hh = String(d.getHours()).padStart(2, "0");
      const min = String(d.getMinutes()).padStart(2, "0");
      return `${dd}.${mm}.${yy} ${hh}:${min}`;
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
      // именно такие же пути, как у вас в assets
      switch (status) {
        case "graded":
          return require("@/assets/svg/status/graded.svg");
        case "submitted":
          return require("@/assets/svg/status/submit.svg");
        case "response_received":
          return require("@/assets/svg/status/nosubmit.svg");
        case "not_submitted":
          return require("@/assets/svg/status/overdue.svg");
        default:
          return require("@/assets/svg/status/nosubmit.svg");
      }
    },

    statusHeaderClass(hw) {
      const now = Date.now();
      const due = new Date(hw.date).getTime();
      if (hw.status === "not_submitted" && due < now) {
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
  border: 2px solid #56AEF6;
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
  border: 2px solid #56AEF6;
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
