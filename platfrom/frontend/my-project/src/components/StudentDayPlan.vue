<template>
  <div id="day-plan">
    <div class="container">
      <!-- Боковое меню -->
      <SideBar :isTestActive="false" />

      <!-- Основной контент -->
      <main class="main-content">
        <h2>План на день</h2>

        <!-- Блоки заданий -->
        <div class="task-container">
          <div
            class="task-block"
            v-for="(item, index) in dayItems"
            :key="index"
            @click="openItem(item)"
          >
            <div class="task-left">
              <div class="task-type">{{ item.type }}</div>
              <div class="task-name">{{ item.name }}</div>
            </div>
            <div class="task-time">{{ formatTime(item.date) }}</div>
          </div>
        </div>

        <!-- Кнопка Плюс (только для учителя) -->
        <div v-if="isTeacher" class="add-task-btn-container">
          <div class="add-task-btn" @click="goToAddLessonPage">
            <span class="plus-icon">+</span>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import SideBar from "../components/SideBar.vue";

export default {
  components: {
    SideBar,
  },
  data() {
    return {
      dayItems: [],
      isTeacher: false,
    };
  },
  created() {
    this.fetchDayItems();
    this.checkUserRole();
  },
  methods: {
    async fetchDayItems() {
      try {
        const [lessonsRes, homeworksRes] = await Promise.all([
          this.$axios.get("/lessons"),
          this.$axios.get("/homeworks/")
        ]);

        const today = new Date().toISOString().split("T")[0];

        const lessons = lessonsRes.data
          .filter(l => l.date.startsWith(today))
          .map(l => ({ ...l, type: "Занятие" }));

        const homeworks = homeworksRes.data
          .filter(h => h.date.startsWith(today))
          .map(h => ({
            ...h,
            type: "Домашнее задание",
            name: h.description || "Домашнее задание"
          }));

        this.dayItems = [...lessons, ...homeworks].sort(
          (a, b) => new Date(a.date) - new Date(b.date)
        );

      } catch (error) {
        console.error("Ошибка при получении плана на день:", error);
      }
    },

    checkUserRole() {
      const user = JSON.parse(localStorage.getItem("user"));
      if (user?.role === "teacher") {
        this.isTeacher = true;
      }
    },

    openItem(item) {
  if (item.type === "Домашнее задание") {
    this.$router.push({ name: "homework-details", params: { id: item.lesson_id } });
  } else {
    this.$router.push({ name: "lesson-details", params: { id: item.id } });
  }
}

,

    formatTime(dateString) {
      const date = new Date(dateString);
      const h = String(date.getHours()).padStart(2, "0");
      const m = String(date.getMinutes()).padStart(2, "0");
      return `${h}:${m}`;
    },

    goToAddLessonPage() {
      this.$router.push({ name: "add-lesson" });
    },
  },
};
</script>


<style scoped>
/* Основной контейнер */
#day-plan {
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

.task-container {
  margin-bottom: 30px;
}

.task-block {
  display: flex;
  flex-direction: row;
  padding: 20px;
  margin-bottom: 15px;
  justify-content: space-between;
  height: 105px;
  cursor: pointer;
}

.task-left {
  flex: 0 1 60%;
  display: flex;
  flex-direction: column;
  border: 2px solid #56AEF6;
  padding: 20px;
  border-radius: 20px;
  transition: border 0.3s ease;
  max-width: 450px;
}

.task-left:hover {
  border: 2px solid #1e9275;
}

.task-type {
  background-color: transparent;
  color: #56AEF6;
  padding: 5px 0;
  text-align: left;
  font-size: 14px;
}

.task-name {
  font-size: 20px;
  color: #333;
  font-weight: light;
  margin-bottom: 12px;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
}

.task-time {
  flex: 0 1 15%;
  background-color: transparent;
  color: #000000;
  padding: 20px;
  font-size: 20px;
  font-weight: light;
  border-radius: 20px;
  text-align: center;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-left: 20px;
  border: 2px solid #56AEF6;
  transition: border 0.3s ease;
}

.task-time:hover {
  border: 2px solid #1e9275;
}

/* Контейнер для кнопки Плюс */
.add-task-btn-container {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

/* Кнопка Плюс */
.add-task-btn {
  width: 50px;
  height: 50px;
  background-color: #56AEF6;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  margin-top: 20px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.add-task-btn:hover {
  background-color: #1e9275;
}

.plus-icon {
  font-size: 28px;
  font-weight: bold;
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 5px;
}
</style>
