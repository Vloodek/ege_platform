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
          <!-- Номер домашнего задания -->
          <div class="form-group">
            <label for="homeworkNumber">Выберите номер задания</label>
            <div class="select-container">
              <select v-model="homework.number" id="homeworkNumber" required>
                <option disabled value="">Выберите номер задания</option>
                <option v-for="n in 27" :key="n" :value="n">{{ n }}</option>
              </select>
            </div>
          </div>

          <!-- Описание домашнего задания -->
          <div class="form-group">
            <label for="homeworkDescription">Текст задания</label>
            <textarea
              id="homeworkDescription"
              v-model="homework.text"
              placeholder="Введите текст задания"
              required
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
                <div v-for="(image, index) in homework.images" :key="index" class="image-preview">
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
            <button @click="addDeadline" class="add-btn">Добавить</button>
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
import axios from 'axios';

export default {
  components: {
    SideBar,
  },
  data() {
    return {
      homework: {
        // Значение ID урока должно быть извлечено из URL
        lessonId: "",  // это будет ID урока
        number: "",     // номер задания для справки
        text: "",
        images: [],
        files: [],
        date: "",
      },
    };
  },
  created() {
    // Извлекаем ID урока из параметров маршрута
    const lessonId = this.$route.params.id; // 'id' из URL
    if (lessonId) {
      this.homework.lessonId = lessonId; // Устанавливаем ID урока в поле lessonId
    } else {
      console.error("ID урока не найден в маршруте!");
    }
  },
  methods: {
    confirmExit() {
      const confirmed = confirm("Вы уверены, что не сохранили изменения?");
      if (confirmed) {
        this.$router.push(`/lesson/${this.homework.lessonId}/details`); // Переход на страницу деталей урока
      }
    },
    handleImageUpload(event) {
      const files = Array.from(event.target.files);
      files.forEach(file => {
        if (file.type.startsWith("image/")) {
          const reader = new FileReader();
          reader.onload = (e) => {
            this.homework.images.push({
              file,
              preview: e.target.result,
            });
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
    addDeadline(event) {
      event.preventDefault();
      alert("Дедлайн выбран: " + this.homework.date);
    },
    handleSubmit() {
      const formData = new FormData();
      // Используем lessonId для правильного поля ID урока
      formData.append("lesson_id", this.homework.lessonId);  // Устанавливаем правильный ID урока
      formData.append("description", this.homework.text); // описание
      formData.append("text", this.homework.text); // текст задания
      formData.append("date", this.homework.date); // дата

      // Добавляем файлы
      this.homework.images.forEach(image => {
        formData.append("files", image.file); // Изображения
      });

      this.homework.files.forEach(file => {
        formData.append("files", file); // Другие файлы (если они есть)
      });

      // Отправка запроса
      axios.post(`http://localhost:8000/homeworks/`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })
      .then(response => {
        console.log("Домашнее задание успешно добавлено", response.data);
        this.$router.push(`/lesson/${this.homework.lessonId}/details`); // Перенаправление на страницу деталей урока
      })
      .catch(error => {
        console.error("Ошибка при добавлении домашнего задания", error);
      });
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
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  font-size: 16px;
  margin-bottom: 5px;
  color: #333;
}

.select-container select {
  width: 100%;
  padding: 10px;
  font-size: 14px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px;
  font-size: 14px;
  border: 1px solid #ddd;
  border-radius: 5px;
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
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.submit-btn:hover,
.add-btn:hover {
  background-color: #45a049;
}

.error-text {
  color: red;
  font-size: 12px;
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
