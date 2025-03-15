<template>
  <div class="edit-homework-page">
    <div class="container">
      <SideBar :isTestActive="false" />

      <div class="main-content">
        <div class="header">
          <button @click="cancelEdit" class="back-button">Вернуться</button>
          <h1 class="edit-title">Редактирование домашнего задания</h1>
        </div>

        <form @submit.prevent="handleSubmit">
          <!-- Название задания -->
          <div class="form-group">
            <label for="homeworkTitle">Название задания</label>
            <input type="text" id="homeworkTitle" v-model="homework.description" required />
          </div>

          <!-- Текст задания -->
          <div class="form-group">
            <label for="homeworkDescription">Текст задания</label>
            <textarea id="homeworkDescription" v-model="homework.text"></textarea>
          </div>

          <!-- Картинки -->
          <div class="form-group">
            <label for="homeworkImages">Картинки</label>
            <input type="file" id="homeworkImages" @change="handleImageUpload" multiple accept="image/*" />

            <div v-if="homework.images.length">
              <p>Предпросмотр изображений:</p>
              <div class="preview-container">
                <div
                  v-for="(image, index) in homework.images"
                  :key="index"
                  class="image-preview"
                >
                  <a :href="image.url || image.preview" target="_blank">
                    <img :src="image.url || image.preview" alt="Изображение" />
                  </a>
                  <button @click="removeImage(index)" type="button" class="remove-btn">❌</button>
                </div>
              </div>
            </div>
          </div>

          <!-- Файлы -->
          <div class="form-group">
            <label for="homeworkFiles">Файлы</label>
            <input type="file" id="homeworkFiles" @change="handleFileUpload" multiple accept="application/pdf" />

            <div v-if="homework.files.length">
              <p>Прикрепленные файлы:</p>
              <ul>
                <li v-for="(file, index) in homework.files" :key="index">
                  <a :href="file.url || file.preview" target="_blank">
                    {{ file.url ? file.url.split('/').pop() : file.file.name }}
                  </a>
                  <button @click="removeFile(index)" type="button" class="remove-btn">
                    ❌
                  </button>
                </li>
              </ul>
            </div>
          </div>

          <!-- Дедлайн -->
          <div class="form-group">
            <label for="homeworkDate">Дедлайн</label>
            <input type="datetime-local" id="homeworkDate" v-model="homework.date" required />
          </div>

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
        id: "",
        lesson_id: "",
        description: "",
        text: "",
        images: [],
        files: [],
        date: "",
      },
      existingFiles: [],
      existingImages: [],
    };
  },
  async created() {
    const homeworkId = this.$route.params.id;
    if (homeworkId) {
      try {
        await this.fetchHomeworkDetails(homeworkId);
      } catch (error) {
        console.error("Ошибка загрузки домашнего задания:", error);
      }
    }
  },
  methods: {
    // Функция для получения домашнего задания
    async fetchHomeworkDetails(homeworkId) {
      try {
        const response = await axios.get(`/homework/${homeworkId}`);
        this.homework = response.data;
        this.existingFiles = [...this.homework.files];
        this.existingImages = [...this.homework.images];

        // Преобразуем пути для отображения
        this.homework.images = this.existingImages.map(image => ({
          url: `${axios.defaults.baseURL}${image.replace("./", "/").replace(/\\/g, "/")}`,
          original: image,
          isLocal: false,
        }));

        this.homework.files = this.existingFiles.map(file => ({
          url: `${axios.defaults.baseURL}${file.replace("./", "/").replace(/\\/g, "/")}`,
          original: file,
          isLocal: false,
        }));
      } catch (error) {
        console.error("Ошибка получения данных с сервера:", error);
      }
    },

    // Обработчик для загрузки изображений
    handleImageUpload(event) {
      const files = Array.from(event.target.files);
      files.forEach(file => {
        if (file.type.startsWith("image/")) {
          const reader = new FileReader();
          reader.onload = e => {
            this.homework.images.push({
              file,
              preview: e.target.result,
              isLocal: true,
            });
          };
          reader.readAsDataURL(file);
        } else {
          alert("Можно загружать только изображения.");
        }
      });
    },

    // Обработчик для удаления изображений
    removeImage(index) {
      const image = this.homework.images[index];
      if (!image.isLocal) {
        this.existingImages = this.existingImages.filter(img => img !== image.original);
      }
      this.homework.images.splice(index, 1);
      console.log("Изображение удалено локально (отложенное удаление).");
    },

    // Обработчик для загрузки файлов
    handleFileUpload(event) {
      const files = Array.from(event.target.files);
      files.forEach(file => {
        if (file.type === "application/pdf") {
          this.homework.files.push({
            file,
            preview: URL.createObjectURL(file),
            isLocal: true,
          });
        } else {
          alert("Можно загружать только PDF.");
        }
      });
    },

    // Обработчик для удаления файлов
    removeFile(index) {
      const file = this.homework.files[index];
      if (!file.isLocal) {
        this.existingFiles = this.existingFiles.filter(f => f !== file.original);
      }
      this.homework.files.splice(index, 1);
      console.log("Файл удален локально (отложенное удаление).");
    },

    // Отправка данных на сервер
    async handleSubmit() {
      const formData = new FormData();
      formData.append("lesson_id", this.homework.lesson_id);
      formData.append("description", this.homework.description);
      formData.append("text", this.homework.text);
      formData.append("date", this.homework.date);

      // Передача существующих файлов и изображений
      formData.append("existing_files", JSON.stringify(this.existingFiles));
      formData.append("existing_images", JSON.stringify(this.existingImages));

      // Добавление новых изображений и файлов
      this.homework.files.forEach(file => {
        if (file.isLocal) {
          formData.append("files", file.file);
        }
      });

      this.homework.images.forEach(image => {
        if (image.isLocal) {
          formData.append("images", image.file);
        }
      });

      try {
        await axios.put(`/homeworks/${this.homework.id}`, formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        this.$router.push(`/lesson/${this.homework.lesson_id}/details`);
      } catch (error) {
        console.error("Ошибка при сохранении домашнего задания:", error);
      }
    },

    cancelEdit() {
      this.$router.push(`/lesson/${this.homework.lesson_id}/details`);
    },
  },
};
</script>


<style scoped>
/* Стили остаются без изменений */
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
/* Кнопка удаления для изображений – позиционируется поверх, без фонового цвета */
.remove-btn {
  position: absolute;
  top: 2px;
  right: 2px;
  background: transparent; /* без заливки */
  color: red;             /* красный символ крестика */
  border: none;
  cursor: pointer;
  font-size: 16px;
  padding: 0;
  line-height: 1;
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
  position: relative; /* Чтобы позиционировать кнопку относительно картинки */
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
