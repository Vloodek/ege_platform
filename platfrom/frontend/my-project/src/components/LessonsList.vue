<template>
  <div id="day-plan">
    <div class="container">
      <!-- Боковое меню -->
      <SideBar :isTestActive="false" />

      <!-- Основной контент с занятиями -->
      <main class="main-content">
        <h2>Занятия</h2>

        <!-- Фильтр для уроков -->
        <div class="filter-container">
          <label for="lesson-filter">Фильтр:</label>
          <select id="lesson-filter" v-model="selectedStatus">
            <option value="">Все</option>
            <option value="upcoming">Предстоящие</option>
            <option value="past">Прошедшие</option>
          </select>
        </div>

        <!-- Контейнер для карточек занятий -->
        <div class="task-container">
          <div
            class="task-block"
            v-for="(lesson, index) in filteredLessons"
            :key="index"
          >
            <!-- Контейнер заголовка, который растягивается под длину названия -->
            <div class="task-header-container">
              <div class="task-header" :class="lessonHeaderClass(lesson)">
                {{ lesson.name }}
              </div>
            </div>
            <!-- Нижняя часть карточки -->
            <div class="task-bottom">
              <!-- Левая часть: время занятия (с датой и иконкой календаря) -->
              <div class="task-info">
                <div class="task-time">
                  <img
                    src="@/assets/svg/sidebar/calendar.svg"
                    alt="calendar"
                    class="calendar-icon"
                  />
                  <span class="calendar-text">{{ formatTime(lesson.date) }}</span>
                </div>
              </div>
              <!-- Правая часть: кнопка для перехода на занятие -->
              <BaseButton :color="buttonColor" @click="openLesson(lesson.id)">
                {{ buttonText }}
              </BaseButton>
            </div>
          </div>
        </div>

        <!-- Кнопка добавления занятия (видна только для преподавателя) -->
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
import BaseButton from "@/components/UI/BaseButton.vue";

export default {
  components: { SideBar, BaseButton },
  data() {
    return {
      lessons: [],
      isTeacher: false,
      role: null,
      selectedStatus: "", // Значение фильтра: "" - все, "upcoming" - предстоящие, "past" - прошедшие
    };
  },
  computed: {
    buttonText() {
      // Если пользователь-преподаватель — выводим "Перейти", иначе "Посмотреть"
      return this.role === "teacher" ? "Перейти" : "Посмотреть";
    },
    buttonColor() {
      // Можно задать разный цвет кнопки, здесь для примера всегда зеленый
      return "green";
    },
    filteredLessons() {
      if (!this.selectedStatus) return this.lessons;
      const now = new Date();
      if (this.selectedStatus === "upcoming") {
        return this.lessons.filter(lesson => new Date(lesson.date) >= now);
      } else if (this.selectedStatus === "past") {
        return this.lessons.filter(lesson => new Date(lesson.date) < now);
      }
      return this.lessons;
    },
  },
  created() {
    this.fetchLessons();
    this.checkUserRole();
  },
  methods: {
    async fetchLessons() {
      try {
        const response = await this.$axios.get("/lessons");
        this.lessons = response.data;
        console.log("Занятия получены:", this.lessons);
      } catch (error) {
        console.error("Ошибка при загрузке занятий:", error);
      }
    },
    checkUserRole() {
      const userData = localStorage.getItem("user");
      if (userData) {
        try {
          const user = JSON.parse(userData);
          this.role = user.role;
          this.isTeacher = user.role === "teacher";
        } catch (e) {
          console.error("Ошибка парсинга user из localStorage:", e);
        }
      }
    },
    openLesson(lessonId) {
      if (!lessonId) {
        console.error("ID урока отсутствует");
        return;
      }
      this.$router.push({ name: "lesson-details", params: { id: lessonId } });
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
    goToAddLessonPage() {
      this.$router.push({ name: "add-lesson" });
    },
    lessonHeaderClass(lesson) {
      // Если дата занятия больше или равна текущей – считается предстоящим (зеленый),
      // иначе прошло (красный)
      const now = new Date();
      const lessonDate = new Date(lesson.date);
      return lessonDate >= now ? "header-upcoming" : "header-past";
    },
  },
};
</script>

<style scoped>
/* Основной контейнер страницы */
#day-plan {
  display: flex;
  min-height: 100vh;
  background-color: #f5f5f5;
}

/* Контейнер для бокового меню и основного контента */
.container {
  display: flex;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* Основной контент */
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

/* Фильтр */
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

/* Карточки занятий */
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

/* Контейнер заголовка — подстраивается под содержимое */
.task-header-container {
  margin-bottom: 10px;
}
.task-header {
  display: inline-block;
  padding: 8px 12px;
  font-size: 18px;
  font-weight: 350;
  border-radius: 8px;
  margin-left: 12px;
}

/* Классы окраски заголовка */
.header-upcoming {
  background-color: #D2FFF4; /* зеленый оттенок для предстоящих занятий */
}
.header-past {
  background-color: #FFD2D2; /* красный оттенок для прошедших занятий */
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

/* Левая часть: иконка календаря и время */
.task-info {
  display: flex;
  align-items: center;
}
.task-time {
  display: flex;
  align-items: center;
  font-size: 16px;
}
.calendar-icon {
  width: 20px;
  height: 20px;
  margin-right: 8px;
  filter: brightness(0);
  padding-left: 1px;
}
.calendar-text {
  padding-top: 6px;
}

/* Кнопка добавления занятия */
.add-task-btn-container {
  display: flex;
  justify-content: flex-end;
}
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
