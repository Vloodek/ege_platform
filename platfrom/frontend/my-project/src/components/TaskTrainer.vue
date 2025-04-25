<template>
  <div id="day-plan">
    <div class="container">
      <!-- Боковое меню -->
      <SideBar :isTestActive="false" />

      <!-- Основной контент -->
      <main class="main-content">
        <!-- Заголовок -->
        <h2>Тренажер</h2>

        <!-- Подзаголовок слева -->
        <div class="subheader">Банк заданий</div>

        <!-- Пронумерованный список типов заданий -->
        <ol class="task-list">
          <li
            v-for="(task, index) in examTasks"
            :key="task.id"
            @click="openTaskDetail(task)"
            :class="{ active: selectedTask?.id === task.id }"
          >
            <span class="task-info">
              {{ index + 1 }}. {{ task.name }}
            </span>
            <span class="task-count">
              {{ taskCounts[task.id] ?? 0 }} шт.
            </span>
          </li>
        </ol>

        <!-- Панель действий внизу -->
        <div class="action-buttons">
          <!-- Всегда видна -->
          <button class="random-btn" @click="randomVariant">
            Случайный вариант
          </button>

          <!-- Только для учителя -->
          <div
            v-if="isTeacher"
            class="add-task-btn"
            @click="openAddTaskModal"
          >
            <span class="plus-icon">+</span>
          </div>
        </div>
      </main>
    </div>

    <!-- Модальное окно для добавления нового задания — только для учителя -->
    <AddTrainTaskModal
      v-if="showAddTaskModal && isTeacher"
      :visible="showAddTaskModal"
      @close="closeAddTaskModal"
      @success="handleAddTaskSuccess"
    />
  </div>
</template>

<script>
import SideBar from "@/components/SideBar.vue";
import AddTrainTaskModal from "@/components/teacher/AddTrainTaskModal.vue";

export default {
  name: "TaskBank",
  components: {
    SideBar,
    AddTrainTaskModal,
  },

  data() {
    return {
      examTasks: [
        { id: 1,  name: "Анализ информационных моделей" },
        { id: 2,  name: "Построение таблиц истинности логических выражений" },
        { id: 3,  name: "Поиск информации в реляционных базах данных" },
        { id: 4,  name: "Кодирование и декодирование информации" },
        { id: 5,  name: "Анализ и построение алгоритмов для исполнителей" },
        { id: 6,  name: "Определение результатов работы простейших алгоритмов" },
        { id: 7,  name: "Кодирование и декодирование информации. Передача информации" },
        { id: 8,  name: "Перебор слов и системы счисления" },
        { id: 9,  name: "Работа с таблицами" },
        { id: 10, name: "Поиск символов в текстовом редакторе" },
        { id: 11, name: "Вычисление количества информации" },
        { id: 12, name: "Выполнение алгоритмов для исполнителей" },
        { id: 13, name: "Организация компьютерных сетей. Адресация" },
        { id: 14, name: "Кодирование чисел. Системы счисления" },
        { id: 15, name: "Преобразование логических выражений" },
        { id: 16, name: "Рекурсивные алгоритмы" },
        { id: 17, name: "Обработка числовой последовательности" },
        { id: 18, name: "Робот-сборщик монет" },
        { id: 19, name: "Выигрышная стратегия. Задание 1" },
        { id: 20, name: "Выигрышная стратегия. Задание 2" },
        { id: 21, name: "Выигрышная стратегия. Задание 3" },
        { id: 22, name: "Многопроцессорные системы" },
        { id: 23, name: "Оператор присваивания и ветвления. Перебор вариантов, построение дерева" },
        { id: 24, name: "Обработка символьных строк" },
        { id: 25, name: "Обработка целочисленной информации" },
        { id: 26, name: "Обработка целочисленной информации" },
        { id: 27, name: "Программирование" },
      ],
      selectedTask: null,
      showAddTaskModal: false,
      taskCounts: {},
    };
  },

  computed: {
    isTeacher() {
      try {
        const user = JSON.parse(localStorage.getItem("user"));
        return user?.role === "teacher";
      } catch {
        return false;
      }
    },
  },

  async created() {
    await this.fetchExamTaskCounts();
  },

  methods: {
    async fetchExamTaskCounts() {
      try {
        const { data } = await this.$axios.get("/exam_tasks/count_by_type");
        this.taskCounts = data.counts || {};
      } catch (error) {
        console.error("Ошибка загрузки количества заданий:", error);
        // Инициализируем нулями
        this.taskCounts = this.examTasks.reduce((acc, t) => {
          acc[t.id] = 0;
          return acc;
        }, {});
      }
    },

    openTaskDetail(task) {
      if (!this.taskCounts[task.id]) return;
      this.selectedTask = task;
      this.$router.push({
        name: "task-detail",
        params: { id: task.id },
        query: { name: task.name },
      });
    },

    openAddTaskModal() {
      this.showAddTaskModal = true;
    },
    closeAddTaskModal() {
      this.showAddTaskModal = false;
    },
    handleAddTaskSuccess(message) {
      alert(message);
      this.closeAddTaskModal();
      this.fetchExamTaskCounts();
    },

    async randomVariant() {
      try {
        const user = JSON.parse(localStorage.getItem("user") || "{}");
        if (!user.userId) throw new Error("Неавторизованный пользователь");

        const formData = new FormData();
        formData.append("test_type", "train");
        formData.append("user_id", user.userId);

        const { data } = await this.$axios.post("/testing/start", formData);
        this.$router.push({
          name: "test-session",
          params: { id: data.session_id },
          query: { test_type: "train" },
        });
      } catch (error) {
        console.error("Ошибка при запуске теста:", error);
        alert("Не удалось запустить случайный вариант.");
      }
    },
  },
};
</script>

<style scoped>
#day-plan {
  display: flex;
  min-height: 100vh;
  background-color: #f5f5f5;
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
  background-color: #fff;
  padding: 20px;
  border-radius: 20px;
  margin-left: 20px;
  position: relative;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

h2 {
  font-size: 28px;
  text-align: center;
  color: #333;
  margin-bottom: 20px;
}

.subheader {
  font-size: 20px;
  color: #56AEF6;
  padding-left: 10px;
  margin-bottom: 15px;
  border-left: 3px solid #56AEF6;
}

.task-list {
  list-style-type: decimal;
  padding-left: 40px;
  margin-bottom: 30px;
}

.task-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  margin-bottom: 8px;
  border: 2px solid #56AEF6;
  border-radius: 10px;
  cursor: pointer;
  transition: background-color 0.3s ease, border 0.3s ease;
}

.task-list li:hover {
  background-color: #b8dfff;
  border: 2px solid #b8dfff;
}

.task-list li.active {
  background-color: #d0f0e8;
}

.task-info {
  font-size: 16px;
  color: #333;
  flex: 1;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.task-count {
  font-size: 16px;
  color: #56AEF6;
  margin-left: 10px;
}

.action-buttons {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.random-btn {
  padding: 10px 20px;
  background-color: #56AEF6;
  color: #fff;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.random-btn:hover {
  background-color: #b8dfff;
}

.add-task-btn {
  width: 50px;
  height: 50px;
  background-color: #56AEF6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  transition: background-color 0.3s ease;
}

.add-task-btn:hover {
  background-color: #b8dfff;
}

.plus-icon {
  font-size: 28px;
  font-weight: bold;
  color: #fff;
}
</style>
