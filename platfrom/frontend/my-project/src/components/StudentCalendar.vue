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
            <h2>{{ currentMonthName }} {{ currentYear }}</h2>
            <button @click="changeMonth(1)" class="arrow-button">
              <img src="@/assets/svg/Calendar/arrow_right.svg" alt="Next Month" />
            </button>
          </div>
          <div class="toggle">
            <div class="toggle-container">
              <button
                @click="toggleView(true)"
                :class="{ active: isScheduleView }"
                class="toggle-button"
              >
                Занятия
              </button>
              <button
                @click="toggleView(false)"
                :class="{ active: !isScheduleView }"
                class="toggle-button"
              >
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
              :class="[
                'day',
                { 'current-day': isCurrentDay(day), 'has-items': scheduleByDate[day] }
              ]"
              @mouseover="showItemMenu(index)"
              @mouseleave="hideItemMenu"
            >
            <div class="day-number">
  <span>{{ day }}</span>
</div>
<!-- Добавляем индикатор для занятий -->
<div
  v-if="isScheduleView && scheduleByDate[day]"
  class="lesson-indicator"
></div>
<!-- Индикатор для ДЗ (если текущий режим – ДЗ) -->
<div
  v-if="!isScheduleView && scheduleByDate[day]"
  class="homework-indicator"
  :class="getHomeworkIndicatorClass(scheduleByDate[day])"
></div>

              <!-- Всплывающее меню для отображения списка уроков/ДЗ -->
              <div
                v-if="isMenuVisible(index) && scheduleByDate[day]"
                class="lesson-context-menu"
              >
                <ul>
                  <li
                    v-for="(item, idx) in scheduleByDate[day]"
                    :key="idx"
                    @click="openItem(item.id)"
                  >
                  {{ item.name }}

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
  name: "CalendarPage",
  components: {
    SideBar,
  },
  data() {
    return {
      currentMonth: new Date().getMonth(),
      currentYear: new Date().getFullYear(),
      daysInMonth: [],
      isScheduleView: true, // true: занятия, false: домашние задания
      scheduleByDate: {}, // данные уроков/ДЗ, сгруппированные по числу месяца
      activeMenuIndex: null,
    };
  },
  computed: {
    currentMonthName() {
      const monthNames = [
        "Январь",
        "Февраль",
        "Март",
        "Апрель",
        "Май",
        "Июнь",
        "Июль",
        "Август",
        "Сентябрь",
        "Октябрь",
        "Ноябрь",
        "Декабрь",
      ];
      return monthNames[this.currentMonth];
    },
    daysInCurrentMonth() {
      const days = [];
      const firstDayOfMonth = new Date(this.currentYear, this.currentMonth, 1);
      const lastDayOfMonth = new Date(this.currentYear, this.currentMonth + 1, 0);
      const startDay = firstDayOfMonth.getDay() || 7; // если 0, то понедельник
      const endDay = lastDayOfMonth.getDate();

      // Заполняем пустые ячейки в начале месяца
      for (let i = 1; i < startDay; i++) {
        days.push("");
      }
      // Заполняем числа месяца
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
    async fetchSchedule() {
      const type = this.isScheduleView ? "lessons" : "homeworks";
      try {
        const response = await this.$axios.get("/schedule", {
          params: {
            month: this.currentMonth + 1, // месяцы с 1
            year: this.currentYear,
            type: type,
          },
        });
        this.scheduleByDate = this.groupScheduleByDate(response.data);
        console.log("Расписание загружено:", response.data);
      } catch (error) {
        console.error("Ошибка при загрузке расписания:", error);
      }
    },
    groupScheduleByDate(schedule) {
      const grouped = {};
      schedule.forEach((item) => {
        const day = new Date(item.date).getDate();
        if (!grouped[day]) {
          grouped[day] = [];
        }
        grouped[day].push(item);
      });
      return grouped;
    },
    loadCalendar() {
      this.daysInMonth = this.daysInCurrentMonth;
      this.fetchSchedule();
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
    toggleView(isLessons) {
      this.isScheduleView = isLessons;
      this.fetchSchedule();
    },
    isCurrentDay(day) {
      const today = new Date();
      return (
        today.getDate() === day &&
        today.getMonth() === this.currentMonth &&
        today.getFullYear() === this.currentYear
      );
    },
    showItemMenu(index) {
      this.activeMenuIndex = index;
    },
    hideItemMenu() {
      this.activeMenuIndex = null;
    },
    isMenuVisible(index) {
      return this.activeMenuIndex === index;
    },
    openItem(itemId) {
      // Перенаправление в зависимости от типа расписания
      if (this.isScheduleView) {
        this.$router.push({ name: "lesson-details", params: { id: itemId } });
      } else {
        this.$router.push({ name: "homework-details", params: { id: itemId } });
      }
    },
    // Дополнительная функция для определения CSS-класса по статусу выполнения ДЗ
    getHomeworkIndicatorClass(items) {
  const status = items[0].submission_status;
  return {
    red: status === "red",
    green: status === "green",
    gray: status === "gray",
    orange: status === "orange",
  };
}
,
  },
};
</script>

<style scoped>
.main-container {
  display: flex;
  min-height: 100vh;
  background-color: #f5f5f5;
  justify-content: center;
}

.content {
  display: flex;
  width: 100%;
  max-width: 1200px;
  padding: 20px;
  gap: 20px;
}

.main-content {
  flex: 1;
  background-color: #ffffff;
  padding: 20px;
  border-radius: 20px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

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

.day {
  position: relative;
  width: 81px;
  height: 84px;
  text-align: center;
  border-radius: 10px;
  border: 2px solid #115544;
  background-color: transparent;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.day.current-day {
  background-color: #d1f2d1;
  color: #115544;
  font-weight: bold;
}


.day-number {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  margin-bottom: auto;
  padding-top: 10px;
}

.day-number span {
  font-size: 16px;
}

/* Индикатор ДЗ (отображается на календаре) */
.homework-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  position: absolute;
  bottom: 8px;
  left: 50%;
  transform: translateX(-50%);
}
.homework-indicator.red {
  background-color: red;
}
.homework-indicator.green {
  background-color: green;
}
.homework-indicator.gray {
  background-color: gray;
}
.lesson-indicator {
  width: 12px;
  height: 12px;
  background-color: green;
  border-radius: 50%;
  position: absolute;
  bottom: 8px;
  left: 50%;
  transform: translateX(-50%);
}

/* Всплывающее меню */
.lesson-context-menu {
  position: absolute;
  top: 100%;
  left: 0;
  background-color: white;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  padding: 10px;
  z-index: 10;
  min-width: 180px;
  word-wrap: break-word;
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

h2 {
  color: #115544;
  font-weight: 500;
}
.homework-indicator.orange {
  background-color: orange;
}
</style>
