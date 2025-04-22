<template>
  <div id="day-plan">
    <div class="container">
      <SideBar :isTestActive="false" />

      <main class="main-content">
        <h2>Занятия</h2>

        <div class="filter-container">
          <label for="lesson-filter">Фильтр:</label>
          <select id="lesson-filter" v-model="selectedStatus">
            <option value="">Все</option>
            <option value="upcoming">Предстоящие</option>
            <option value="past">Прошедшие</option>
          </select>
        </div>

        <div class="task-container">
          <div class="task-block" v-for="lesson in filteredLessons" :key="lesson.id">
            <!-- Удаление доступно только учителю, крестик справа сверху -->
            <button v-if="isTeacher" class="delete-btn" @click="deleteLesson(lesson.id)" title="Удалить урок">×</button>

            <div class="task-header-container">
              <div class="task-header" :class="lessonHeaderClass(lesson)">
                {{ lesson.name }}
              </div>
            </div>

            <div class="task-bottom">
              <div class="task-info">
                <div class="task-time">
                  <img src="@/assets/svg/sidebar/calendar.svg" alt="calendar" class="calendar-icon" />
                  <span class="calendar-text">
                    {{ formatTime(lesson.date) }}
                  </span>
                </div>
              </div>
              <BaseButton :color="buttonColor" @click="openLesson(lesson.id)">
                {{ buttonText }}
              </BaseButton>
            </div>
          </div>
        </div>

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
import SideBar from "@/components/SideBar.vue";
import BaseButton from "@/components/UI/BaseButton.vue";

export default {
  name: "DayPlan",
  components: { SideBar, BaseButton },
  data() {
    return {
      lessons: [],
      role: null,
      isTeacher: false,
      selectedStatus: "",
    };
  },
  computed: {
    buttonText() {
      return this.role === "teacher" ? "Перейти" : "Посмотреть";
    },
    buttonColor() {
      return "green";
    },
    filteredLessons() {
      const now = Date.now();
      if (this.selectedStatus === "upcoming")
        return this.lessons.filter(l => new Date(l.date).getTime() >= now);
      if (this.selectedStatus === "past")
        return this.lessons.filter(l => new Date(l.date).getTime() < now);
      return this.lessons;
    },
  },
  created() {
    this.fetchLessons();
    this.loadUserRole();
  },
  methods: {
    async fetchLessons() {
      try {
        const { data } = await this.$axios.get("/lessons");
        this.lessons = data;
      } catch {
        console.error("Не удалось загрузить занятия");
      }
    },
    loadUserRole() {
      try {
        const u = JSON.parse(localStorage.getItem("user") || "{}");
        this.role = u.role;
        this.isTeacher = u.role === "teacher";
      } catch {
        this.role = null;
      }
    },
    formatTime(dt) {
      const d = new Date(dt);
      return [
        String(d.getDate()).padStart(2, "0"),
        String(d.getMonth() + 1).padStart(2, "0"),
        d.getFullYear()
      ].join('.') + ' ' +
        [String(d.getHours()).padStart(2, "0"), String(d.getMinutes()).padStart(2, "0")].join(':');
    },
    lessonHeaderClass(lesson) {
      return new Date(lesson.date).getTime() >= Date.now()
        ? "header-upcoming"
        : "header-past";
    },
    openLesson(id) {
      this.$router.push({ name: "lesson-details", params: { id } });
    },
    goToAddLessonPage() {
      this.$router.push({ name: "add-lesson" });
    },
    async deleteLesson(id) {
      if (!confirm("Удалить этот урок?")) return;
      try {
        await this.$axios.delete(`/lessons/${id}`);
        this.lessons = this.lessons.filter(l => l.id !== id);
      } catch {
        alert("Ошибка при удалении урока");
      }
    },
  },
};
</script>

<style scoped>
#day-plan {
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
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

h2 {
  text-align: center;
  font-weight: 450;
}

.filter-container {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
  align-items: center;
}

.filter-container select {
  padding: 5px 12px;
  border: 2px solid #56AEF6;
  border-radius: 8px;
  outline: none;
}

.task-container {
  margin-bottom: 30px;
}

.task-block {
  position: relative;
  padding: 15px;
  margin-bottom: 15px;
  border: 2px solid #56AEF6;
  border-radius: 20px;
  background: #fff;
}

.delete-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  font-size: 18px;
  line-height: 1;
  cursor: pointer;
  color: #a00;
}

.delete-btn:hover {
  color: #f00;
}

.task-header {
  display: inline-block;
  padding: 8px 12px;
  font-size: 18px;
  font-weight: 350;
  border-radius: 8px;
  margin-left: 12px;
}

.header-upcoming {
  background: #D2FFF4;
}

.header-past {
  background: #FFD2D2;
}

.task-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  padding: 10px 15px;
}

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
}

.add-task-btn-container {
  display: flex;
  justify-content: flex-end;
}

.add-task-btn {
  width: 50px;
  height: 50px;
  background: #56AEF6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  margin-top: 20px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.add-task-btn:hover {
  background: #1e9275;
}

.plus-icon {
  font-size: 28px;
  font-weight: bold;
  color: #fff;
}
</style>
