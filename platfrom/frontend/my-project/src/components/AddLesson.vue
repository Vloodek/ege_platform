<template>
  <div class="add-lesson-page">
    <div class="container">
      <SideBar :isTestActive="false" />

      <div class="main-content">
        <h2>Добавление урока</h2>

        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label for="lessonTitle">Название урока</label>
            <input
              type="text"
              id="lessonTitle"
              v-model="lesson.title"
              placeholder="Введите название урока"
              required
            />
          </div>

          <div class="form-group">
            <label for="lessonDescription">Описание урока</label>
            <textarea
              id="lessonDescription"
              v-model="lesson.description"
              placeholder="Введите описание урока"
              required
            ></textarea>
          </div>

          <button type="submit" class="submit-btn">Добавить урок</button>
        </form>
      </div>
    </div>
  </div>
</template>


<script>
import SideBar from "../components/SideBar.vue";
import axios from 'axios';

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
      videoLinkError: false,  
    };
  },
  methods: {
    handleFileUpload(event) {
      const files = Array.from(event.target.files);
      files.forEach(file => {
        if (!file.type.startsWith("image/") && file.type !== "application/pdf") {
          alert("Только изображения и PDF файлы могут быть загружены.");
        } else {
          this.task.files.push(file);
        }
      });
    },
    validateVideoLink() {
      const regex = /https?:\/\/.*/;
      this.videoLinkError = !regex.test(this.task.videoLink);
    },
    handleSubmit() {
  this.validateVideoLink();
  if (this.videoLinkError) {
    alert("Пожалуйста, введите корректную ссылку на видео.");
    return;
  }

  const formData = new FormData();
  formData.append("name", this.task.name);
  formData.append("description", this.task.description);
  formData.append("videoLink", this.task.videoLink);
  formData.append("text", this.task.text);
  formData.append("date", this.task.date);  // Убедитесь, что формат даты соответствует требованиям FastAPI

  this.task.files.forEach(file => {
    formData.append("files", file);
  });

  axios.post("http://localhost:8000/tasks/", formData, {
    headers: {
      "Content-Type": "multipart/form-data"
    }
  })
  .then(response => {
    console.log("Задание успешно добавлено", response.data);
    this.$router.push("/day-plan");
  })
  .catch(error => {
    console.error("Ошибка при добавлении задания", error);
  });
}

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
  
  .error-text {
    color: red;
    font-size: 12px;
    margin-top: 5px;
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
  