<template>
  <div
    :class="['sidebar', userTypeClass]"
    :style="{ height: sidebarHeight }"
  >
    <!-- Навигация во время теста -->
    <div
      v-if="internalTestActive"
      class="test-sidebar-navigation"
    >
      <div class="task-grid-sidebar">
        <div
          v-for="(taskId, index) in taskIds"
          :key="taskId"
          class="task-square-sidebar"
          :class="squareClass(taskId, index)"
          @click="$emit('selectTask', index)"
        >
          {{ index + 1 }}
        </div>
      </div>

      <div
        v-if="!testFinished"
        class="nav-controls"
      >
        <button
          class="nav-arrow"
          @click="$emit('prevTask')"
        >
          ←
        </button>
        <button
          class="nav-arrow"
          @click="$emit('nextTask')"
        >
          →
        </button>
      </div>

      <div class="test-info">
        <p v-if="!testFinished">
          Осталось: {{ formattedTimer }}
        </p>
        <p v-else>
          Итоговый балл: {{ score }}
        </p>
        <p>Всего вопросов: {{ totalQuestions }}</p>
      </div>

      <button
        v-if="!testFinished"
        class="exit-btn-sidebar"
        @click="$emit('finishTest')"
      >
        Завершить тест
      </button>

      <button
        v-if="testFinished"
        class="exit-btn-sidebar"
        @click="$emit('exitTest')"
      >
        Выйти
      </button>
    </div>

    <!-- Обычное меню -->
    <div
      v-else
      class="default-menu"
    >
      <ul class="menu">
        <router-link
          v-for="item in menuItems"
          :key="item.label"
          :to="item.link"
          class="menu-item"
        >
          <img
            :src="item.icon"
            alt="icon"
            class="menu-icon"
          >
          <span :class="['menu-label', labelClass(item.label)]">{{ item.label }}</span>
        </router-link>
      </ul>
    </div>
  </div>
</template>

<script>
import lessonsIcon from "@/assets/svg/sidebar/lessons.svg";
import scheduleIcon from "@/assets/svg/sidebar/calendar.svg";
import homeworkIcon from "@/assets/svg/sidebar/dz.svg";
import trainerIcon from "@/assets/svg/sidebar/train.svg";
import groupsIcon from "@/assets/svg/sidebar/groups.svg";

export default {
  name: "SideBar",
  props: {
    isTestActive: Boolean,
    timerDisplay: Number,
    totalQuestions: Number,
    taskIds: Array,
    currentTaskIndex: Number,
    answers: Object,
    results: Object,
    score: Number,
    testFinished: Boolean,
  },
  data() {
    return {
      userData: JSON.parse(localStorage.getItem("user")) || {},
      internalTestActive: this.isTestActive,
    };
  },
  computed: {
    userTypeClass() {
      return {
        teacher: this.userData.role === "teacher",
        student: this.userData.role === "student",
      };
    },
    sidebarHeight() {
      return this.internalTestActive
        ? "400px"
        : this.userData.role === "teacher"
        ? "340px"
        : "270px";
    },
    menuItems() {
      const base = [
        { label: "Занятия", icon: lessonsIcon, link: "/lessons" },
        { label: "Расписание", icon: scheduleIcon, link: "/calendar" },
        { label: "Домашние задания", icon: homeworkIcon, link: "/homeworks" },
        { label: "Тренажёр", icon: trainerIcon, link: "/trainer" },
      ];
      if (this.userData.role === "teacher") {
        base.push({ label: "Группы", icon: groupsIcon, link: "/groups" });
      }
      return base;
    },
    formattedTimer() {
      const hours = Math.floor(this.timerDisplay / 3600);
      const minutes = Math.floor((this.timerDisplay % 3600) / 60);
      return `${hours} ч ${minutes} мин`;
    },
  },
  watch: {
    $route(to) {
      this.internalTestActive = to.name === "test-session";
    },
  },
  mounted() {
    this.internalTestActive = this.$route.name === "test-session";
  },
  methods: {
    squareClass(taskId, index) {
      if (!this.testFinished) {
        return {
          active: this.currentTaskIndex === index,
          answered: Boolean(this.answers?.[taskId]),
        };
      } else {
        const res = this.results?.[taskId];
        return {
          active: this.currentTaskIndex === index,
          answered: res === true,
          wrong: res === false,
        };
      }
    },
    labelClass(label) {
      return {
        "label-schedule": label === "Расписание",
        "label-homework": label === "Домашние задания",
        "label-groups": label === "Группы",
        "label-train": label === "Тренажёр",
        "label-lessons": label === "Занятия",

      };
    },
  },
};
</script>

<style scoped>
.sidebar {
  width: 257px;
  background-color: #fff;
  color: #000;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}
.label-lessons{
  padding-top: 5px;
}
.menu {
  list-style: none;
  padding: 0;
  margin: 0;
}
.menu-item {
  display: flex;
  align-items: center;
  padding: 10px 15px;
  border-radius: 10px;
  margin-bottom: 10px;
  text-decoration: none;
  color: inherit;
  transition: background-color 0.2s;
}
.label-train{
  padding-top: 4px;
}
.menu-item:hover {
  background-color: #e0e0e0;
}
.menu-icon {
  width: 40px;
  height: 40px;
  margin-right: 15px;
}
.menu-label {
  font-size: 18px;
  font-weight: 350;
}

/* Индивидуальные настройки */
.label-schedule {
  padding-top: 8px;
}
.label-homework {
  padding-top: 4px;
  font-size: 17px;
}
.label-groups {
  padding-top: 6px;
}

/* Тестовая часть */
.test-sidebar-navigation {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 20px;
}
.task-grid-sidebar {
  display: grid;
  grid-template-columns: repeat(5, 20px);
  gap: 4px;
  margin-bottom: 10px;
}
.task-square-sidebar {
  width: 20px;
  height: 20px;
  background-color: #ccc;
  border: 1px solid #56AEF6;
  border-radius: 3px;
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
.task-square-sidebar.active {
  border: 2px solid #56AEF6;
}
.task-square-sidebar.answered {
  background-color: #66bb6a;
}
.task-square-sidebar.wrong {
  background-color: #e57373;
}
.nav-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}
.nav-arrow {
  background-color: #56AEF6;
  color: #fff;
  padding: 5px 8px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
.test-info {
  text-align: center;
  margin-bottom: 10px;
}
.test-info p {
  margin: 5px 0;
  font-size: 16px;
}
.exit-btn-sidebar {
  background-color: #dc3545;
  color: #fff;
  padding: 8px 12px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
</style>
