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
          <div
            class="task-block"
            v-for="(task, index) in tasks"
            :key="index"
            @click="openTask(task.id)"
          >
            <div class="task-left">
              <div class="task-type">{{ task.type }}</div> <!-- Тип задания (Домашняя работа / Занятие) -->
              <div class="task-name">{{ task.name }}</div>
            </div>
            <div class="task-time">{{ formatTime(task.date) }}</div> <!-- Время в формате 13:50 -->
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
      tasks: [], // Задания будут загружаться с сервера
      showMenu: false, // Для показа контекстного меню
    };
  },
  created() {
    this.fetchTasks();
  },
  methods: {
    async fetchTasks() {
      try {
        const response = await fetch('http://localhost:8000/tasks', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
        });
        if (response.ok) {
          this.tasks = await response.json();
        } else {
          console.error("Ошибка загрузки заданий");
        }
      } catch (error) {
        console.error("Ошибка сети:", error);
      }
    },
    openTask(taskId) {
      if (!taskId) {
        console.error("ID задания отсутствует");
        return;
      }
      this.$router.push({ name: "task-details", params: { id: taskId } }); // Имя маршрута исправлено
    },

    toggleMenu() {
      this.showMenu = !this.showMenu;
    },
    goToAddTaskPage(type) {
      this.$router.push({ name: 'add-task', query: { type: type } });
    },
    formatTime(dateString) {
      const date = new Date(dateString);
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      return `${hours}:${minutes}`;
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
  border-radius: 20px;
  margin-left: 20px; /* Отступ от бокового меню */
}

/* Заголовок */
h2 {
  font-size: 24px;
  margin-bottom: 20px;
  color: #333;
  text-align: center; /* Центрирование заголовка */
}

/* Контейнер для блоков с заданиями */
/* Контейнер для блоков с заданиями */
.task-container {
  margin-bottom: 30px; /* Отступ снизу для кнопки с плюсом */
}

.task-block {
  display: flex;
  flex-direction: row; /* Горизонтальное расположение */
  padding: 20px;
  margin-bottom: 15px;
  justify-content: space-between; /* Равномерное распределение пространства */
  height: 100px; /* Увеличена высота блоков */
  cursor: pointer; /* Добавляем курсор "pointer", чтобы было видно, что на блок можно кликнуть */
}

/* Блок с текстом задания */
.task-left {
  flex: 0 1 60%; /* Занимает 60% ширины блока */
  display: flex;
  flex-direction: column;
  border: 2px solid #115544; /* Обводка зеленая */
  padding: 20px; /* Увеличены внутренние отступы */
  border-radius: 20px;
  transition: border 0.3s ease; /* Плавный переход для изменения обводки */
}

/* Изменение обводки при наведении */
.task-left:hover {
  border: 2px solid #1e9275; /* Изменение обводки на более светлый зеленый */
}

/* Тип задания */
.task-type {
  background-color: transparent;
  color: #115544;
  padding: 10px;
  text-align: center;
  font-size: 16px;
  font-weight: bold;
  border-radius: 20px;
  margin-bottom: 10px;
  border-bottom: 2px solid #115544;
}

/* Название задания */
.task-name {
  font-size: 20px; /* Размер шрифта для названия задания */
  color: #333;
  font-weight: light;
}

/* Время задания */
.task-time {
  flex: 0 1 15%; /* Занимает 25% ширины блока */
  background-color: transparent;
  color: #000000;
  padding: 20px; /* Увеличены внутренние отступы */
  font-size: 20px; /* Размер шрифта для времени */
  font-weight: light;
  border-radius: 20px;
  text-align: center;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-left: 20px; /* Отступ между блоками */
  border: 2px solid #115544; /* Обводка зеленая */
  transition: border 0.3s ease; /* Плавный переход для изменения обводки */
}

/* Изменение обводки у времени при наведении */
.task-time:hover {
  border: 2px solid #1e9275; /* Изменение обводки на более светлый зеленый */
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
  background-color: #115544; /* Зеленый фон, соответствующий обводке */
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  margin-top: 20px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.add-task-btn:hover {
  background-color: #1e9275; /* Легкая подсветка при наведении */
}

/* Белый символ плюса и выравнивание по центру */
.plus-icon {
  font-size: 28px;
  font-weight: bold;
  color: white; /* Белый цвет для плюса */
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 5px; /* Небольшой сдвиг вниз для плюса */
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


