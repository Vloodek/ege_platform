<template>
  <div class="main-container">
    <div class="content">
      
      <!-- Боковое меню -->
      <SideBar />

      <!-- Основной контент с календарем -->
      <main class="main-content">
        <div class="calendar-header">
          <button @click="changeMonth(-1)">&#8592;</button>
          <h2>{{ currentMonthName }} {{ currentYear }}</h2>
          <button @click="changeMonth(1)">&#8594;</button>
          <div class="toggle">
            <button @click="toggleView">Занятия/ДЗ</button>
          </div>
        </div>

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

          <div class="days">
            <div
              v-for="(day, index) in daysInMonth"
              :key="index"
              :class="['day', { 'current-day': isCurrentDay(day) }]">
              <div>{{ day }}</div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import SideBar from "../components/SideBar.vue"; // Импорт компонента Sidebar
export default {
  components: {
    SideBar, // Регистрируем Sidebar как локальный компонент
  },
  data() {
    return {
      currentMonth: new Date().getMonth(), // Текущий месяц
      currentYear: new Date().getFullYear(), // Текущий год
      currentDate: new Date(),
      daysInMonth: [], // Массив дней в текущем месяце
      isScheduleView: true, // Переключатель между "Занятия" и "ДЗ"
    };
  },
  computed: {
    currentMonthName() {
      const monthNames = [
        'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 
        'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
      ];
      return monthNames[this.currentMonth];
    },
    // Вычисляем дни текущего месяца
    daysInCurrentMonth() {
      const days = [];
      const firstDayOfMonth = new Date(this.currentYear, this.currentMonth, 1);
      const lastDayOfMonth = new Date(this.currentYear, this.currentMonth + 1, 0);
      const startDay = firstDayOfMonth.getDay() || 7; // Если воскресенье, то считаем как 7
      const endDay = lastDayOfMonth.getDate();

      // Добавляем пустые ячейки перед первым днем месяца
      for (let i = 1; i < startDay; i++) {
        days.push('');
      }

      // Добавляем дни месяца
      for (let i = 1; i <= endDay; i++) {
        days.push(i);
      }

      return days;
    }
  },
  mounted() {
    this.loadCalendar();
  },
  methods: {
    loadCalendar() {
      // Загружаем дни текущего месяца
      this.daysInMonth = this.daysInCurrentMonth;
    },

    changeMonth(direction) {
      // Меняем месяц
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
      // Переключаем между "Занятия" и "ДЗ"
      this.isScheduleView = !this.isScheduleView;
    },

    isCurrentDay(day) {
      // Проверяем, является ли день текущим днем
      const today = new Date();
      return (
        today.getDate() === day &&
        today.getMonth() === this.currentMonth &&
        today.getFullYear() === this.currentYear
      );
    }
  }
};
</script>

<style scoped>
/* Сбрасываем отступы и поля для body и html */
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
}

/* Основной контейнер */
.main-container {
  display: flex;
  height: 100vh;
  margin: 0 360px; /* Отступы по бокам минимум 360px */
  padding-top: 0; /* Убираем отступ сверху */
}

/* Контент */
.content {
  display: flex;
  flex: 1;
  padding: 20px;
  min-height: 80px;
  gap: 20px; /* Отступы между боковым меню и основным контентом */
}

/* Боковое меню */
.sidebar {
  width: 240px;
  background-color: #ffffff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.sidebar ul {
  list-style: none;
  padding: 0;
}

.sidebar li {
  margin-bottom: 16px;
}

.sidebar a {
  text-decoration: none;
  color: #333;
  font-size: 16px;
  font-weight: 500;
}

.sidebar a:hover {
  color: #4CAF50;
}

/* Основной контент с календарем */
.main-content {
  flex: 1;
  background-color: #ffffff;
  border-radius: 8px;
  padding: 20px;
  min-height: 80px;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toggle {
  display: flex;
  align-items: center;
}

.toggle button {
  padding: 8px 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  cursor: pointer;
  margin-left: 20px;
}

/* Календарь */
.calendar-days {
  display: flex;
  flex-direction: column;
  margin-top: 25px;
}

.weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  margin-bottom: 10px;
}

.weekdays span {
  font-weight: bold;
}

.days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 10px;
}

.day {
  padding: 10px;
  text-align: center;
  border-radius: 5px;
  background-color: #e0e0e0;
  cursor: pointer;
}

.day.current-day {
  background-color: #4CAF50;
  color: white;
}

.day:hover {
  background-color: #d0d0d0;
}
</style>
