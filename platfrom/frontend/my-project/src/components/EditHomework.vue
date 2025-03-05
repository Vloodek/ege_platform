<template>
    <div class="edit-homework-page">
      <div class="container">
        <!-- Боковое меню -->
        <SideBar :isTestActive="false" />
  
        <!-- Основной контент для редактирования домашнего задания -->
        <div class="main-content">
          <!-- Заголовок с кнопкой для возврата -->
          <div class="header">
            <button @click="cancelEdit" class="back-button">Вернуться</button>
            <h1 class="edit-title">Редактирование домашнего задания</h1>
          </div>
  
          <!-- Форма редактирования домашнего задания -->
          <form @submit.prevent="handleSubmit">
            <!-- Название задания -->
            <div class="form-group">
              <label for="homeworkTitle">Название задания</label>
              <input
                type="text"
                id="homeworkTitle"
                v-model="homework.description"
                placeholder="Введите название задания"
                required
              />
            </div>
  
            <!-- Текст задания -->
            <div class="form-group">
              <label for="homeworkDescription">Текст задания</label>
              <textarea
                id="homeworkDescription"
                v-model="homework.text"
                placeholder="Введите текст задания"
              ></textarea>
            </div>
  
            <!-- Картинки (при необходимости можно добавить предпросмотр) -->
            <div class="form-group">
              <label for="homeworkImages">Картинки</label>
              <input
                type="file"
                id="homeworkImages"
                @change="handleImageUpload"
                multiple
                accept="image/*"
              />
              <div v-if="homework.images && homework.images.length">
                <p>Предпросмотр изображений:</p>
                <div class="preview-container">
                  <div
                    v-for="(image, index) in homework.images"
                    :key="index"
                    class="image-preview"
                  >
                    <img :src="image.preview || image" alt="Изображение" />
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
              <div v-if="homework.files && homework.files.length">
                <p>Прикрепленные файлы:</p>
                <ul>
                  <li v-for="(file, index) in homework.files" :key="index">
                    {{ file.name || file.split('/').pop() }}
                  </li>
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
    components: {
      SideBar,
    },
    data() {
      return {
        homework: {
          // Предполагается, что сервер вернёт все необходимые поля
          id: "",
          lessonId: "",
          description: "",
          text: "",
          images: [],
          files: [],
          date: ""
        },
        // Дополнительно можно хранить временные данные для новых файлов, если требуется
      };
    },
    created() {
      // Загружаем данные домашнего задания по id, полученному из маршрута
      const homeworkId = this.$route.params.id;
      if (homeworkId) {
        this.fetchHomeworkDetails(homeworkId);
      } else {
        console.error("ID домашнего задания не найден в маршруте!");
      }
    },
    methods: {
        async fetchHomeworkDetails(homeworkId) {
  try {
    const response = await axios.get(`http://localhost:8000/homework/${homeworkId}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` }
    });

    this.homework = response.data;

    // Запрашиваем lesson_id отдельно, если его нет в ответе
    if (!this.homework.lesson_id) {
      await this.fetchLessonId(homeworkId);
    }

    // Преобразуем пути изображений
    this.homework.images = this.homework.images.map(image => {
      if (image.startsWith("./uploads")) {
        return `http://localhost:8000${image.replace("./", "/")}`;
      }
      return image;
    });

  } catch (error) {
    console.error("Ошибка при загрузке домашнего задания:", error);
  }
}

,
async fetchLessonId(homeworkId) {
  try {
    const response = await axios.get(`http://localhost:8000/homework/${homeworkId}/lesson_id`, {
      headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` }
    });

    this.homework.lesson_id = response.data.lesson_id;
    console.log("📌 lesson_id найден:", this.homework.lesson_id);
  } catch (error) {
    console.error("❌ Ошибка при получении lesson_id:", error);
  }
},
      handleImageUpload(event) {
        const files = Array.from(event.target.files);
        files.forEach(file => {
          if (file.type.startsWith("image/")) {
            const reader = new FileReader();
            reader.onload = (e) => {
              // Если в homework.images уже массив URL, можно заменить их или добавить новые файлы
              this.homework.images.push({
                file, // Новый файл для загрузки
                preview: e.target.result
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
      async handleSubmit() {
  console.log("🟡 Отправка формы обновления домашнего задания...");

  if (!this.homework.lesson_id) {
    console.error("❌ lesson_id отсутствует!");
    alert("Ошибка: отсутствует lesson_id!");
    return;
  }

  const homeworkData = {
    lesson_id: this.homework.lesson_id, // <-- Теперь точно есть!
    description: this.homework.description,
    text: this.homework.text,
    date: this.homework.date,
    files: this.homework.files.length ? this.homework.files.join(";") : "",
    images: this.homework.images.length ? this.homework.images.join(";") : ""
  };

  try {
    const response = await axios.put(`http://localhost:8000/homeworks/${this.homework.id}`, homeworkData, {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("access_token")}`
      }
    });

    console.log("✅ Домашнее задание успешно обновлено", response.data);
    this.$router.push(`/lesson/${this.homework.lesson_id}/details`);
  } catch (error) {
    console.error("❌ Ошибка при обновлении домашнего задания", error);
  }
}


,
      cancelEdit() {
        this.$router.push(`/lesson/${this.homework.lessonId}/details`);
      }
    }
  };
  </script>
  
  <style scoped>
  /* Стили можно скопировать из AddHomework, адаптируя под дизайн */
  .edit-homework-page {
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
  .submit-btn {
    padding: 10px 20px;
    background-color: #115544;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    position: absolute;
    right: 20px;
    bottom: 20px;
  }
  .submit-btn:hover {
    background-color: #1e9275;
  }
  </style>
  