<template>
  <div class="add-homework-page">
    <div class="container">
      <!-- Боковое меню -->
      <SideBar :isTestActive="false" />

      <!-- Основной контент для редактирования домашнего задания -->
      <div class="main-content">
        <!-- Заголовок с кнопкой для возврата -->
        <div class="header">
          <button @click="confirmExit" class="back-button">Вернуться</button>
          <h1 class="edit-title">Редактирование домашнего задания</h1>
        </div>

        <!-- Форма для редактирования домашнего задания -->
        <form @submit.prevent="handleSubmit">
          <!-- Название домашнего задания -->
          <div class="form-group">
            <label for="homeworkTitle">Название задания</label>
            <input
              type="text"
              id="homeworkTitle"
              v-model="homework.title"
              placeholder="Введите название задания"
              required
            />
          </div>

          <!-- Описание домашнего задания -->
          <div class="form-group">
            <label for="homeworkDescription">Текст задания</label>
            <textarea
              id="homeworkDescription"
              v-model="homework.text"
              placeholder="Введите текст задания"
            ></textarea>
          </div>

          <!-- Картинки -->
          <div class="form-group">
            <label for="homeworkImages">Картинки</label>
            <input
              type="file"
              id="homeworkImages"
              @change="handleImageUpload"
              multiple
              accept="image/*"
            />
            <div v-if="homework.images.length">
              <p>Предпросмотр изображений:</p>
              <div class="preview-container">
                <div
                  v-for="(image, index) in homework.images"
                  :key="index"
                  class="image-preview"
                >
                  <img :src="image.preview" :alt="'Изображение ' + (index + 1)" />
                </div>
              </div>
            </div>
          </div>

          <!-- Файлы -->
          <div class="form-group">
            <label for="homeworkFiles">Файлы</label>
            <input
              type="file"
              id="homeworkFiles"
              @change="handleFileUpload"
              multiple
              accept="application/pdf"
            />
            <div v-if="homework.files.length">
              <p>Прикрепленные файлы:</p>
              <ul>
                <li v-for="(file, index) in homework.files" :key="index">{{ file.name }}</li>
              </ul>
            </div>
          </div>

          <!-- Дедлайн -->
          <div class="form-group">
            <label for="homeworkDate">Дедлайн</label>
            <input
              type="datetime-local"
              id="homeworkDate"
              v-model="homework.date"
              required
            />
          </div>

          <!-- Кнопка отправки -->
          <button type="submit" class="submit-btn">Сохранить изменения</button>
        </form>
      </div>
    </div>
  </div>
</template>


<script>
import SideBar from "./SideBar.vue";
import axios from "axios";

export default {
  components: { SideBar },
  data() {
    return {
      homework: {
        lessonId: this.$route.params.id || "", // ID урока из URL
        title: "",
        text: "",
        images: [],
        files: [],
        date: "",
      },
    };
  },
  methods: {
    handleImageUpload(event) {
      const files = Array.from(event.target.files);
      files.forEach(file => {
        if (file.type.startsWith("image/")) {
          const reader = new FileReader();
          reader.onload = (e) => {
            this.homework.images.push({ file, preview: e.target.result });
          };
          reader.readAsDataURL(file);
        } else {
          alert("Можно загружать только изображения.");
        }
      });
    },
    handleFileUpload(event) {
      const files = Array.from(event.target.files);
      files.forEach(file => {
        if (file.type === "application/pdf") {
          this.homework.files.push(file);
        } else {
          alert("Можно загружать только PDF файлы.");
        }
      });
    },
    confirmExit() {
      if (confirm("Вы уверены, что не сохранили изменения?")) {
        this.$router.push(`/lesson/${this.homework.lessonId}/details`);
      }
    },
    async handleSubmit() {
      try {
        const formData = new FormData();
        formData.append("lesson_id", this.homework.lessonId);
        formData.append("description", this.homework.title);
        formData.append("text", this.homework.text);
        formData.append("date", this.homework.date);

        this.homework.images.forEach(image => formData.append("images", image.file));
        this.homework.files.forEach(file => formData.append("files", file));

        const response = await axios.post("/homeworks/", formData);
        console.log("✅ Домашнее задание успешно добавлено", response.data);
        this.$router.push(`/lesson/${this.homework.lessonId}/details`);
      } catch (error) {
        console.error("❌ Ошибка при добавлении домашнего задания", error);
      }
    },
  },
};
</script>


<style scoped>
.add-homework-page {
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
  position: relative;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.back-button {
  background-color: #ff4444;
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
}

.edit-title {
  color: #4CAF50;
  font-size: 24px;
  margin: 0;
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
.form-group textarea,
.select-container select {
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

.preview-container {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.image-preview {
  width: 100px;
  height: 100px;
  overflow: hidden;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.submit-btn,
.add-btn {
  padding: 10px 20px;
  background-color: #115544;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  /* Выравнивание кнопки справа */
  position: absolute;
  right: 20px;
  bottom: 20px;
}

.submit-btn:hover,
.add-btn:hover {
  background-color: #1e9275;
}

.error-text {
  color: red;
  font-size: 12px;
  margin-top: 5px;
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

.page-title,
h3,
h4 {
  font-weight: 500;
}
</style>
