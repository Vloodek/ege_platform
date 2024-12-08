<template>
  <div class="add-lesson-page">
    <div class="container">
      <SideBar :isTestActive="false" />

      <div class="main-content">
        <!-- Заголовок страницы -->
        <h2 class="page-title">Добавление урока</h2>

        <!-- Основная форма для урока -->
        <form @submit.prevent="handleSubmit" class="lesson-form">
          <!-- Раздел "Информация о занятии" -->
          <div class="lesson-info">
            <h3>Информация о занятии</h3>
            <div class="form-group">
              <label for="lessonTitle">Название урока</label>
              <input
                type="text"
                id="lessonTitle"
                v-model="lesson.name"
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

            <div class="form-group">
              <label for="videoLink">Ссылка на видео</label>
              <input
                type="text"
                id="videoLink"
                v-model="lesson.videoLink"
                placeholder="Введите ссылку на видео"
                @blur="validateVideoLink"
              />
              <p v-if="videoLinkError" class="error-text">Пожалуйста, введите корректную ссылку на видео.</p>
            </div>
          </div>

          <!-- Раздел "Материалы к занятию" -->
          <div class="lesson-materials">
            <h3>Материалы к занятию</h3>
            <div class="form-group">
              <label for="lessonText">Текст занятия</label>
              <textarea
                id="lessonText"
                v-model="lesson.text"
                placeholder="Введите текст занятия"
              ></textarea>
            </div>

            <div class="form-group">
              <label for="lessonImages">Загрузить изображения</label>
              <input
                type="file"
                id="lessonImages"
                @change="handleFileUpload"
                multiple
                accept="image/*"
              />
            </div>

            <div class="form-group">
              <label for="lessonFiles">Загрузить прикрепленные файлы</label>
              <input
                type="file"
                id="lessonFiles"
                @change="handleFileUpload"
                multiple
              />
            </div>
          </div>

          <!-- Раздел "Дата занятия" -->
          <div class="form-group">
            <label for="lessonDate">Дата занятия</label>
            <input
              type="datetime-local"
              id="lessonDate"
              v-model="lesson.date"
              required
            />
          </div>

          <!-- Кнопка добавления -->
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
      lesson: {
        name: "",
        description: "",
        videoLink: "",
        text: "",
        files: [],
        images: [],
        date: "",
      },
      videoLinkError: false,  
    };
  },
  methods: {
    handleFileUpload(event) {
      const files = Array.from(event.target.files);
      files.forEach(file => {
        if (file.type.startsWith("image/")) {
          this.lesson.images.push(file);
        } else if (file.type === "application/pdf" || file.type.startsWith("application/")) {
          this.lesson.files.push(file);
        } else {
          alert("Только изображения и PDF файлы могут быть загружены.");
        }
      });
    },
    validateVideoLink() {
      const regex = /https?:\/\/.*/;
      this.videoLinkError = !regex.test(this.lesson.videoLink);
    },
    handleSubmit() {
      this.validateVideoLink();
      if (this.videoLinkError) {
        alert("Пожалуйста, введите корректную ссылку на видео.");
        return;
      }

      const formData = new FormData();
      formData.append("name", this.lesson.name);
      formData.append("description", this.lesson.description);
      formData.append("videoLink", this.lesson.videoLink);
      formData.append("text", this.lesson.text);
      formData.append("date", this.lesson.date);

      this.lesson.files.forEach(file => {
        formData.append("files", file);
      });

      this.lesson.images.forEach(file => {
        formData.append("images", file);
      });

      axios.post("http://localhost:8000/lessons/", formData, {
        headers: {
          "Content-Type": "multipart/form-data"
        }
      })
      .then(response => {
        console.log("Урок успешно добавлен", response.data);
        this.$router.push("/day-plan");
      })
      .catch(error => {
        console.error("Ошибка при добавлении урока", error);
      });
    }
  },
};
</script>

  
<style scoped>
.add-lesson-page {
  display: flex;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f3f3f3;
  width: 100%;
}

.container {
  display: flex;
  flex-wrap: wrap;
  width: 100%;
  padding: 20px;
  background-color: #f3f3f3;
}

.main-content {
  flex: 1;
  margin-left: 20px;
  background-color: #ffffff;
  border-radius: 8px;
  padding: 20px;
  max-width: 100%;
  box-sizing: border-box;
}

.page-title {
  text-align: center;
  font-size: 28px;
  margin-bottom: 20px;
  color: #333;
}

.lesson-form {
  width: 100%;
}

.lesson-info,
.lesson-materials {
  margin-bottom: 30px;
}

.lesson-info h3,
.lesson-materials h3 {
  font-size: 22px;
  margin-bottom: 10px;
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
  box-sizing: border-box;
}

.form-group textarea {
  resize: vertical;
  min-height: 120px;
}

.error-text {
  color: red;
  font-size: 12px;
  margin-top: 5px;
}

.submit-btn {
  padding: 10px 20px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  width: auto;
}

.submit-btn:hover {
  background-color: #45a049;
}

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

  