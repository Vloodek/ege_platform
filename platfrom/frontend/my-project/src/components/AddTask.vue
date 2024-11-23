<template>
  <div class="add-task-page">
    <div class="container">
      <!-- Боковое меню -->
      <SideBar :isTestActive="false" />
  
      <!-- Основной контент для редактирования задания -->
      <div class="main-content">
        <h2>Редактирование занятия</h2>
        
        <!-- Форма для добавления/редактирования занятия -->
        <form @submit.prevent="handleSubmit">
          <!-- Название занятия -->
          <div class="form-group">
            <label for="taskName">Название занятия</label>
            <input
              type="text"
              id="taskName"
              v-model="task.name"
              placeholder="Введите название занятия"
              required
            />
          </div>
    
          <!-- Описание занятия -->
          <div class="form-group">
            <label for="taskDescription">Описание занятия</label>
            <textarea
              id="taskDescription"
              v-model="task.description"
              placeholder="Введите описание занятия"
              required
            ></textarea>
          </div>
    
          <!-- Ссылка на видео -->
          <div class="form-group">
            <label for="taskVideo">Ссылка на видео</label>
            <input
              type="url"
              id="taskVideo"
              v-model="task.videoLink"
              placeholder="Введите ссылку на видео"
            />
          </div>
    
          <!-- Текст задания -->
          <div class="form-group">
            <label for="taskText">Текст задания</label>
            <textarea
              id="taskText"
              v-model="task.text"
              placeholder="Введите текст задания"
              required
            ></textarea>
          </div>
    
          <!-- Картинки -->
          <div class="form-group">
            <label for="taskFiles">Картинки/файлы</label>
            <input
              type="file"
              id="taskFiles"
              @change="handleFileUpload"
              multiple
            />
            <div v-if="task.files.length">
              <p>Прикрепленные файлы:</p>
              <ul>
                <li v-for="(file, index) in task.files" :key="index">{{ file.name }}</li>
              </ul>
            </div>
          </div>
    
          <!-- Выбор даты -->
          <div class="form-group">
            <label for="taskDate">Дата занятия</label>
            <input
              type="datetime-local"
              id="taskDate"
              v-model="task.date"
              required
            />
          </div>
    
          <!-- Кнопка для добавления -->
          <button type="submit" class="submit-btn">Добавить</button>
        </form>
      </div>
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
      task: {
        name: "",
        description: "",
        videoLink: "",
        text: "",
        files: [],
        date: "",
      },
    };
  },
  methods: {
    handleFileUpload(event) {
      this.task.files = Array.from(event.target.files);
    },
    handleSubmit() {
      console.log("Задание добавлено:", this.task);
      this.$router.push("/day-plan");
    },
  },
};
</script>

<style scoped>
.add-task-page {
  display: flex;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f3f3f3; /* Серый фон для страницы */
  width: 100%;
}

.container {
  display: flex;
  flex-wrap: wrap; /* Это поможет адаптировать элементы при сужении экрана */
  width: 100%;
  padding: 20px;
  background-color: #f3f3f3; /* Серый фон для контейнера */
}

.main-content {
  flex: 1;
  margin-left: 20px; /* Отступ от бокового меню */
  background-color: #ffffff; /* Белый фон для контента */
  border-radius: 8px;
  padding: 20px;
  max-width: 100%;
  box-sizing: border-box; /* Учитываем отступы и границы в общей ширине */
  overflow: hidden; /* Если что-то выйдет за пределы, это будет скрыто */
}

h2 {
  font-size: 24px;
  margin-bottom: 20px;
  color: #333;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  font-size: 16px;
  margin-bottom: 5px;
  color: #333;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px;
  font-size: 14px;
  border: 1px solid #ddd;
  border-radius: 5px;
  box-sizing: border-box; /* Учитываем отступы и границы в общей ширине */
}

.form-group textarea {
  resize: vertical;
  min-height: 120px;
}

.submit-btn {
  padding: 10px 20px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  width: auto;
  box-sizing: border-box; /* Учитываем отступы и границы в общей ширине */
}

.submit-btn:hover {
  background-color: #45a049;
}

/* Дополнительные стили для адаптивности */
@media (max-width: 768px) {
  .container {
    flex-direction: column;
  }

  .main-content {
    margin-left: 0;
    width: 100%;
  }
}

</style>
