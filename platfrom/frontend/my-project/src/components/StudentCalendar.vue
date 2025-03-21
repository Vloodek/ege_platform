<template>
  <div class="main-container">
    <div class="content">
      <!-- Боковое меню -->
      <SideBar />

      <!-- Основной контент с календарем -->
      <main class="main-content">
        <!-- Заголовок с переключением месяцев -->
        <div class="calendar-header">
          <div class="month-nav">
            <button @click="changeMonth(-1)" class="arrow-button">
              <img src="@/assets/svg/Calendar/arrow_left.svg" alt="Prev Month" />
            </button>
            
            <button @click="changeMonth(1)" class="arrow-button">
              <img src="@/assets/svg/Calendar/arrow_right.svg" alt="Next Month" />
            </button>
            <h2>{{ currentMonthName }} {{ currentYear }}</h2>
          </div>
          <div class="toggle">
            <div class="toggle-container">
              <button @click="toggleView" :class="{'active': isScheduleView}" class="toggle-button">
                Занятия
              </button>
              <button @click="toggleView" :class="{'active': !isScheduleView}" class="toggle-button">
                ДЗ
              </button>
            </div>
          </div>
        </div>

        <!-- Дни недели -->
        <div class="calendar-days">
          <div class="weekdays">
            <span>Пн</span>
            <span>Вт</span>
            <span>Ср</span>
            <span>Чт</span>
            <span>Пт</span>
            <span>Сб</span>
            <span>Вс</span>
          </div>

          <!-- Дни месяца -->
          <div class="days">
            <div
              v-for="(day, index) in daysInMonth"
              :key="index"
              :class="['day', { 'current-day': isCurrentDay(day), 'has-lessons': lessonsByDate[day] }]"
              @mouseover="showLessonMenu(index)"
              @mouseleave="hideLessonMenu"
            >
              <div class="day-number">
                <span>{{ day }}</span>
              </div>
              <div v-if="lessonsByDate[day]" class="lesson-indicator"></div>
              <div
                v-if="isMenuVisible(index) && lessonsByDate[day]"
                class="lesson-context-menu"
              >
                <ul>
                  <li
                    v-for="(lesson, idx) in lessonsByDate[day]"
                    :key="idx"
                    @click="openLesson(lesson.id)"
                  >
                    {{ lesson.name }}
                  </li>
                </ul>
              </div>
            </div>
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
      currentMonth: new Date().getMonth(),
      currentYear: new Date().getFullYear(),
      daysInMonth: [],
      isScheduleView: true,
      lessonsByDate: {}, // Содержит занятия по текущему месяцу
      activeMenuIndex: null,
    };
  },
  computed: {
    currentMonthName() {
      const monthNames = [
        'Январь',
        'Февраль',
        'Март',
        'Апрель',
        'Май',
        'Июнь',
        'Июль',
        'Август',
        'Сентябрь',
        'Октябрь',
        'Ноябрь',
        'Декабрь',
      ];
      return monthNames[this.currentMonth];
    },
    daysInCurrentMonth() {
      const days = [];
      const firstDayOfMonth = new Date(this.currentYear, this.currentMonth, 1);
      const lastDayOfMonth = new Date(this.currentYear, this.currentMonth + 1, 0);
      const startDay = firstDayOfMonth.getDay() || 7;
      const endDay = lastDayOfMonth.getDate();

      for (let i = 1; i < startDay; i++) {
        days.push('');
      }
      for (let i = 1; i <= endDay; i++) {
        days.push(i);
      }
      return days;
    },
  },
  mounted() {
    this.loadCalendar();
  },
  methods: {
    async fetchLessons() {
    try {
        const response = await this.$axios.get("/lessons", {
            params: {
                month: this.currentMonth + 1,
                year: this.currentYear,
            },
        });
        this.lessonsByDate = this.groupLessonsByDate(response.data);
        console.log("Занятия загружены:", response.data);
    } catch (error) {
        console.error("Ошибка при загрузке занятий:", error);
    }
}
,
    groupLessonsByDate(lessons) {
      const grouped = {};
      lessons.forEach((lesson) => {
        const lessonDate = new Date(lesson.date);
        const lessonMonth = lessonDate.getMonth();
        const lessonYear = lessonDate.getFullYear();
        const lessonDay = lessonDate.getDate();

        // Учитываем только занятия для текущего месяца и года
        if (lessonMonth === this.currentMonth && lessonYear === this.currentYear) {
          if (!grouped[lessonDay]) {
            grouped[lessonDay] = [];
          }
          grouped[lessonDay].push(lesson);
        }
      });
      return grouped;
    },
    loadCalendar() {
      this.daysInMonth = this.daysInCurrentMonth;
      this.fetchLessons();
    },
    changeMonth(direction) {
      this.currentMonth += direction;
      if (this.currentMonth < 0) {
        this.currentMonth = 11;
        this.currentYear--;
      } else if (this.currentMonth > 11) {
        this.currentMonth = 0;
        this.currentYear++;
      }
      this.loadCalendar();
    },
    toggleView() {
      this.isScheduleView = !this.isScheduleView;
    },
    isCurrentDay(day) {
      const today = new Date();
      return (
        today.getDate() === day &&
        today.getMonth() === this.currentMonth &&
        today.getFullYear() === this.currentYear
      );
    },
    showLessonMenu(index) {
      this.activeMenuIndex = index;
    },
    hideLessonMenu() {
      this.activeMenuIndex = null;
    },
    isMenuVisible(index) {
      return this.activeMenuIndex === index;
    },
    openLesson(lessonId) {
      this.$router.push({ name: 'lesson-details', params: { id: lessonId } });
    },
  },
};
</script>

<style scoped>
/* Основной контейнер */
.main-container {
  display: flex;
  min-height: 100vh;
  background-color: #f5f5f5;
  justify-content: center;
}

/* Контент */
.content {
  display: flex;
  width: 100%;
  max-width: 1200px;
  padding: 20px;
  gap: 20px;
}

/* Основной контент */
.main-content {
  flex: 1;
  background-color: #ffffff;
  padding: 20px;
  border-radius: 20px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

/* Календарь */
.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.month-nav {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-left: 10px;
}

.arrow-button {
  background-color: transparent;
  border: none;
  cursor: pointer;
  width: 30px;
  height: 30px;
}

.arrow-button img {
  width: 100%;
  height: 100%;
}

.toggle-container {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.toggle-button {
  padding: 10px 20px;
  background-color: transparent;
  border: 2px solid #115544;
  color: #115544;
  border-radius: 20px;
  cursor: pointer;
  width: 90px;
}

.toggle-button.active {
  background-color: #115544;
  color: white;
}

/* Дни недели */
.weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  margin-bottom: 10px;
}

.weekdays span {
  font-weight: bold;
  font-size: 14px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 10px;
  justify-items: center;
}

/* Календарь */
.day {
  position: relative;
  width: 81px;
  height: 84px;
  text-align: center;
  border-radius: 10px;
  border: 2px solid #115544;
  background-color: transparent;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column; /* Обеспечивает вертикальное расположение */
}

/* Для текущего дня */
.day.current-day {
  background-color: #115544; /* Зеленая заливка */
  color: white;
}

.day-number {
  display: flex;
  justify-content: center;
  align-items: flex-start; /* Размещает цифру в верхней части */
  margin-bottom: auto; /* Отодвигает цифру вверх */
  padding-top: 10px; /* Дополнительное пространство сверху */
}

.day-number span {
  font-size: 16px;
}

/* Индикатор занятия */
.lesson-indicator {
  width: 12px;
  height: 12px;
  background-color: green;
  border-radius: 50%;
  position: absolute;
  bottom: 8px; /* Центрируем внизу */
  left: 50%;
  transform: translateX(-50%);
}

.lesson-context-menu {
  position: absolute;
  top: 100%;
  left: 0;
  background-color: white;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  padding: 10px;
  z-index: 10;
}

.lesson-context-menu ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

.lesson-context-menu li {
  padding: 5px;
  cursor: pointer;
}

.lesson-context-menu li:hover {
  background-color: #f0f0f0;
}
h2{
  color: #115544;
  font-weight: 500;
}
</style>
