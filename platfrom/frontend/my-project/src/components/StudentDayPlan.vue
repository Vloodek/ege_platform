<template>
  <div id="day-plan">
    <div class="container">
      <!-- Боковое меню -->
      <SideBar :isTestActive="false" />
  
      <!-- Основной контент с планом на день -->
      <main class="main-content">
        <h2>План на день</h2>
  
        <!-- Контейнер для блоков с заданиями -->
        <div class="task-container">
          <!-- Блоки с заданиями -->
          <div class="task-block" v-for="(task, index) in tasks" :key="index">
            <div class="task-name">{{ task.name }}</div>
            <div class="task-time">{{ task.time }}</div>
          </div>
        </div>

        <!-- Кнопка Плюс под последним заданием -->
        <div v-if="isTeacher" class="add-task-btn-container">
          <div class="add-task-btn" @click="toggleMenu">
            <span class="plus-icon">+</span>
          </div>

          <!-- Контекстное меню (показывается при клике на плюсик) -->
          <div v-if="showMenu" class="context-menu-container">
            <button @click="goToAddTaskPage('homework')">Добавить ДЗ</button>
            <button @click="goToAddTaskPage('lesson')">Добавить занятие</button>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import SideBar from "../components/SideBar.vue"; // Импортируем Sidebar

export default {
  components: {
    SideBar, // Регистрируем Sidebar как компонент
  },
  data() {
    return {
      isTeacher: true, // Для теста показываем плюсик у преподавателя
      tasks: [
        { name: "Занятие по математике", time: "10:00" },
        { name: "6 задание ЕГЭ", time: "13:00" },
        { name: "Занятие по физике", time: "15:00" },
        { name: "Решение задач по химии", time: "17:00" },
      ],
      showMenu: false, // Для показа контекстного меню
    };
  },
  methods: {
    toggleMenu() {
      // Показать или скрыть контекстное меню
      this.showMenu = !this.showMenu;
    },
    goToAddTaskPage(type) {
      // Переход на страницу добавления задания или занятия
      this.$router.push({ name: 'add-task', query: { type: type } });
    }
  }
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
  border-radius: 8px;
}

h2 {
  font-size: 24px;
  margin-bottom: 20px;
  color: #333;
}

/* Контейнер для блоков с заданиями */
.task-container {
  margin-bottom: 30px; /* Отступ снизу для кнопки с плюсом */
}

/* Стили для блоков с заданиями */
.task-block {
  display: flex;
  justify-content: space-between;
  background-color: #f0f0f0;
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 8px;
}

.task-name {
  font-size: 18px;
  color: #333;
}

.task-time {
  font-size: 16px;
  color: #888;
}

/* Контейнер для кнопки Плюс и контекстного меню */
.add-task-btn-container {
  display: flex;
  flex-direction: column;
  align-items: flex-end;  /* Выравниваем кнопку справа */
}

/* Кнопка Плюс */
.add-task-btn {
  width: 50px;
  height: 50px;
  background-color: #4CAF50;
  color: white;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  margin-top: 20px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.plus-icon {
  font-size: 28px;
  font-weight: bold;
}

/* Контекстное меню */
.context-menu-container {
  margin-top: 10px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  width: 150px;
  padding: 10px;
  text-align: left;
  z-index: 10; /* Чтобы меню было на переднем плане */
}

.context-menu-container button {
  background: none;
  border: none;
  padding: 5px 10px;
  font-size: 14px;
  cursor: pointer;
  width: 100%;
  text-align: left;
}

.context-menu-container button:hover {
  background-color: #f0f0f0;
}
</style>
