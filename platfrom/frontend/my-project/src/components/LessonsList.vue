<template>
  <div id="day-plan">
    <div class="container">
      <!-- Боковое меню -->
      <SideBar :isTestActive="false" />

      <!-- Основной контент с уроками -->
      <main class="main-content">
        <h2>Занятия</h2>

        <!-- Контейнер для блоков с уроками -->
        <div class="task-container">
          <!-- Блоки с уроками -->
          <div
            class="task-block"
            v-for="(lesson, index) in lessons"
            :key="index"
            @click="openLesson(lesson.id)"
          >
            <div class="task-left">
              <div class="task-type">{{ lesson.type }}</div>
              <div class="task-name">{{ lesson.name }}</div>
            </div>
            <div class="task-time">{{ formatTime(lesson.date) }}</div>
          </div>
        </div>

        <!-- Кнопка Плюс (видна только для учителя) -->
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
  components: { SideBar },
  data() {
    return {
      lessons: [],
      isTeacher: false, // По умолчанию считаем, что это не учитель
    };
  },
  created() {
    this.fetchLessons();
    this.checkUserRole(); // Проверяем роль пользователя при создании компонента
  },
  methods: {
    // Метод для получения списка уроков
    async fetchLessons() {
        try {
            const response = await this.$axios.get("/lessons");
            this.lessons = response.data;
            console.log("Уроки получены:", this.lessons);
        } catch (error) {
            console.error("Ошибка при загрузке уроков:", error);
        }
    },

    // Метод для проверки роли пользователя
    checkUserRole() {
      const user = JSON.parse(localStorage.getItem("user"));
      if (user && user.role === "teacher") {
        this.isTeacher = true;
      }
    },

    // Метод для перехода на страницу подробностей урока
    openLesson(lessonId) {
      if (!lessonId) {
        console.error("ID урока отсутствует");
        return;
      }
      this.$router.push({ name: "lesson-details", params: { id: lessonId } });
    },

    // Метод для форматирования времени
    formatTime(dateString) {
      const date = new Date(dateString);
      const hours = String(date.getHours()).padStart(2, "0");
      const minutes = String(date.getMinutes()).padStart(2, "0");
      return `${hours}:${minutes}`;
    },

    // Метод для перехода на страницу добавления занятия
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

/* Контейнер для основного контента и бокового меню */
.container {
  display: flex;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* Стили для основного контента */
.main-content {
  flex: 1;
  background-color: #fff;
  padding: 20px;
  border-radius: 20px;
  margin-left: 20px;
}

/* Заголовок */
h2 {
  font-size: 24px;
  margin-bottom: 20px;
  color: #333;
  text-align: center;
}

/* Контейнер для блоков с уроками */
.task-container {
  margin-bottom: 30px;
}

/* Блоки с уроками */
.task-block {
  display: flex;
  flex-direction: row;
  padding: 20px;
  margin-bottom: 15px;
  justify-content: space-between;
  height: 105px;
  cursor: pointer;
}

/* Блок с текстом задания */
.task-left {
  flex: 0 1 60%;
  display: flex;
  flex-direction: column;
  border: 2px solid #115544;
  padding: 20px;
  border-radius: 20px;
  transition: border 0.3s ease;
  max-width: 450px;
}

.task-left:hover {
  border: 2px solid #1e9275;
}

/* Тип задания */
.task-type {
  background-color: transparent;
  color: #115544;
  padding: 5px 0;
  text-align: left;
  font-size: 14px;
}

/* Название задания */
.task-name {
  font-size: 20px;
  color: #333;
  font-weight: light;
  margin-bottom: 12px;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
}

/* Время задания */
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
  border: 2px solid #115544;
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
  background-color: #115544;
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
