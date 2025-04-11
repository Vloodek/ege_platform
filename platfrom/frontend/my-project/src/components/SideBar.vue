<template>
  <div :class="['sidebar', userTypeClass]" :style="{ height: sidebarHeight }">
    <!-- Если тест активен, отображаем только тестовую навигацию -->
    <div v-if="internalTestActive" class="test-sidebar-navigation">
      <!-- Маленькая сетка для навигации между заданиями -->
      <div class="task-grid-sidebar">
        <div
          v-for="(id, index) in taskIds"
          :key="index"
          class="task-square-sidebar"
          :class="{ active: currentTaskIndex === index, answered: answers[index + 1] }"
          @click="$emit('selectTask', index)"
        >
          {{ index + 1 }}
        </div>
      </div>
      <!-- Кнопки переключения заданий -->
      <div class="nav-controls">
        <button @click="$emit('prevTask')" class="nav-arrow">←</button>
        <button @click="$emit('nextTask')" class="nav-arrow">→</button>
      </div>
      <!-- Информация о времени и количестве вопросов -->
      <div class="test-info">
        <p>Осталось: {{ formattedTimer }}</p>
        <p>Всего вопросов: {{ totalQuestions }}</p>
      </div>
      <!-- Кнопка выхода -->
      <button class="exit-btn-sidebar" @click="$emit('exitTest')">Выход</button>
    </div>
    <!-- Если тест не активен, показываем стандартное меню -->
    <div v-else class="default-menu">
      <ul class="menu">
        <li v-for="item in menuItems" :key="item.label" class="menu-item">
          <router-link :to="item.link" class="menu-link">
            <img :src="item.icon" alt="icon" class="menu-icon" />
            <span class="menu-label">{{ item.label }}</span>
          </router-link>
        </li>
      </ul>
      <!-- Дополнительная информация, если требуется, можно оставить блок ниже -->
      <div v-if="internalTestActive" class="test-sidebar-info">
        <p>Тест активен</p>
        <p>Время до конца: {{ timerDisplay }}</p>
        <p>Всего вопросов: {{ totalQuestions }}</p>
      </div>
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
    isTestActive: {
      type: Boolean,
      default: false,
    },
    timerDisplay: {
      type: Number,
      default: 0,
    },
    totalQuestions: {
      type: Number,
      default: 0,
    },
    taskIds: {
      type: Array,
      default: () => [],
    },
    currentTaskIndex: {
      type: Number,
      default: 0,
    },
    answers: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      userData: JSON.parse(localStorage.getItem("user")) || {},
      // Локальное состояние для режима теста
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
      if (this.internalTestActive) return "400px";
      return this.userData.role === "teacher" ? "340px" : "270px";
    },
    menuItems() {
      const commonItems = [
        { label: "Занятия", icon: lessonsIcon, link: "/lessons" },
        { label: "Расписание", icon: scheduleIcon, link: "/calendar" },
        { label: "Домашние задания", icon: homeworkIcon, link: "/homeworks" },
        { label: "Тренажёр", icon: trainerIcon, link: "/trainer" },
      ];
      if (this.userData.role === "teacher") {
        return [...commonItems, { label: "Группы", icon: groupsIcon, link: "/groups" }];
      }
      return commonItems;
    },
    // Вычисляем часы из timerDisplay (секунды)
    hours() {
      const totalSeconds = this.timerDisplay;
      return Math.floor(totalSeconds / 3600);
    },
    // Вычисляем минуты из оставшихся секунд
    minutes() {
      const totalSeconds = this.timerDisplay;
      return Math.floor((totalSeconds % 3600) / 60);
    },
    // Объединяем часы и минуты в строку с пояснениями
    formattedTimer() {
      return `${this.hours} часов, ${this.minutes} минут`;
    },
  },
  watch: {
    // Отслеживаем изменение маршрута
    $route(to) {
      // Если имя маршрута не test-session, выключаем тестовый режим
      if (to.name !== "test-session") {
        this.internalTestActive = false;
      } else {
        this.internalTestActive = true;
      }
    },
  },
  mounted() {
    // При инициализации выставляем internalTestActive согласно текущему маршруту
    if (this.$route.name !== "test-session") {
      this.internalTestActive = false;
    } else {
      this.internalTestActive = true;
    }
  },
};
</script>

<style scoped>
.sidebar {
  width: 257px;
  background-color: #ffffff;
  color: #000000;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

/* Стандартное меню */
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
  transition: background-color 0.2s;
  cursor: pointer;
  color: #000000;
}

.menu-item:hover {
  background-color: #e0e0e0;
}

.menu-icon {
  width: 40px;
  height: 40px;
  margin-right: 15px;
}

.menu-link {
  display: flex;
  align-items: center;
  width: 100%;
  text-decoration: none;
  color: inherit;
}

.menu-label {
  font-size: 18px;
  font-weight: 350;
  flex-grow: 1;
}

/* Тестовая панель навигации */
.test-sidebar-navigation {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 20px;
}

/* Сетка маленьких квадратиков */
.task-grid-sidebar {
  display: grid;
  grid-template-columns: repeat(5, 20px);
  grid-gap: 4px;
  margin-bottom: 10px;
}

.task-square-sidebar {
  width: 20px;
  height: 20px;
  background-color: #cccccc;
  border: 1px solid #115544;
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  cursor: pointer;
}

.task-square-sidebar.active {
  background-color: #d0f0e8;
}

.task-square-sidebar.answered {
  background-color: #66bb6a;
}

.nav-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.nav-arrow {
  background-color: #115544;
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
