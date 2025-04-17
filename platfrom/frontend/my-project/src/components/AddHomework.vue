<template>
  <div class="add-homework-page">
    <div class="container">
      <!-- Боковое меню -->
      <SideBar :isTestActive="false" />

      <!-- Основной контент для редактирования домашнего задания -->
      <div class="main-content">
        <!-- Заголовок с кнопкой-стрелочкой для возврата -->
        <div class="header">
          <div class="back-arrow" @click="confirmExit"></div>
          <h1 class="edit-title">Добавление домашнего задания</h1>
        </div>

        <!-- Форма для редактирования домашнего задания -->
        <form @submit.prevent="handleSubmit" class="homework-form">
          <!-- Название задания -->
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

          <!-- Текст задания через Quill -->
          <div class="form-group">
            <label for="homeworkText">Текст задания</label>
            <div ref="homeworkEditor" class="quill-editor"></div>
          </div>

          <!-- Файлы (только PDF) -->
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
                <li v-for="(file, index) in homework.files" :key="index">
                  {{ file.name }}
                  <button type="button" @click="removeFile(index)">Удалить</button>
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

          <button type="submit" class="submit-btn">Добавить ДЗ</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import SideBar from "./SideBar.vue";
import Quill from "quill";
import "quill/dist/quill.snow.css";

export default {
  name: "AddHomeworkPage",
  components: { SideBar },
  data() {
    return {
      homework: {
        lessonId: this.$route.params.id || "", // ID урока из URL
        title: "",
        text: "",
        files: [],
        date: "",
      },
      // Ссылка на Quill-редактор для текста задания
      homeworkEditor: null,
    };
  },
  methods: {
    handleFileUpload(event) {
      const files = Array.from(event.target.files);
      files.forEach((file) => {
        if (file.type === "application/pdf") {
          this.homework.files.push(file);
        } else {
          alert("Можно загружать только PDF файлы.");
        }
      });
    },
    removeFile(index) {
      this.homework.files.splice(index, 1);
    },
    confirmExit() {
      if (confirm("Вы уверены, что не сохранили изменения?")) {
        this.$router.push(`/lesson/${this.homework.lessonId}/details`);
      }
    },
    async handleSubmit() {
      // Проверка обязательных полей
      if (!this.homework.title) {
        alert("Заполните название задания");
        return;
      }
      // Обратите внимание, что текст задания берется из Quill,
      // но если он не введён, используем пустую строку.
      if (this.homework.text === undefined) {
        this.homework.text = "";
      }
      // Отладка: выводим объект с данными перед отправкой
      console.log("Отправляемые данные:", this.homework);

      const formData = new FormData();
      formData.append("lesson_id", this.homework.lessonId);
      // Добавляем поле "description" – возьмём его равным названию задания или можно добавить отдельное поле
      formData.append("description", this.homework.title);
      formData.append("text", this.homework.text);
      formData.append("date", this.homework.date);

      this.homework.files.forEach((file) => {
        formData.append("files", file);
      });

      try {
        // Изменяем URL на /homeworks/ в соответствии с FastAPI
        const response = await this.$axios.post("/homeworks/", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        console.log("✅ Домашнее задание успешно добавлено", response.data);
        this.$router.push(`/lesson/${this.homework.lessonId}/details`);
      } catch (error) {
        console.error("❌ Ошибка при добавлении домашнего задания", error);
        alert("Ошибка при добавлении домашнего задания");
      }
    },
    // Инициализация Quill-редактора для текста задания
    initEditor() {
      this.$nextTick(() => {
        const editorEl = this.$refs.homeworkEditor;
        if (!editorEl) {
          console.error("Элемент для Quill-редактора не найден");
          return;
        }
        // Тулбар без смены шрифта
        const toolbarOptions = [
          [{ header: "1" }, { header: "2" }],
          [{ list: "ordered" }, { list: "bullet" }],
          ["bold", "italic", "underline"],
          [{ align: [] }],
          ["link", "image"],
        ];
        const self = this;
        const customImageHandler = async function () {
          const quill = this.quill;
          if (!quill) return;
          const input = document.createElement("input");
          input.setAttribute("type", "file");
          input.setAttribute("accept", "image/*");
          input.click();
          input.onchange = async () => {
            const file = input.files[0];
            if (file) {
              await self.uploadAndInsertImage(quill, file);
            }
          };
        };

        this.homeworkEditor = new Quill(editorEl, {
          theme: "snow",
          modules: {
            toolbar: {
              container: toolbarOptions,
              handlers: { image: customImageHandler },
            },
          },
        });
        this.homeworkEditor.on("text-change", () => {
          this.homework.text = this.homeworkEditor.root.innerHTML;
        });
      });
    },
    async uploadAndInsertImage(quill, file) {
      const formData = new FormData();
      formData.append("image", file);
      try {
        const response = await this.$axios.post("/upload_temp_image", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        const imageUrl = response.data.image_url;
        const range = quill.getSelection();
        if (range) {
          const imgHtml = `<img src="${imageUrl}" alt="${file.name}" />`;
          quill.clipboard.dangerouslyPasteHTML(range.index, imgHtml);
        }
      } catch (error) {
        console.error("Ошибка загрузки изображения:", error);
        alert("Ошибка загрузки изображения");
      }
    },
  },
  mounted() {
    this.initEditor();
  },
};
</script>

<style scoped>
.add-homework-page {
  display: flex;
  max-width: 1200px;
  margin: 0 auto;
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
  box-sizing: border-box;
  position: relative;
}
.header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  position: relative;
}
.back-arrow {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  background-color: #115544;
  clip-path: polygon(100% 0, 0 50%, 100% 100%);
  cursor: pointer;
}
.edit-title {
  flex: 1;
  text-align: center;
  font-size: 24px;
  color: #115544;
  font-weight: 500;
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
.form-group select {
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
  background-color: #115544;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  right: 20px;
  bottom: 20px;
  margin-bottom: 60px; /* Добавьте этот отступ */
}

.submit-btn:hover {
  background-color: #1e9275;
}
/* Стили Quill-редактора */
.quill-editor {
  height: 200px;
  border: 1px solid #ccc;
  border-radius: 5px;
  background-color: #fafafa;
  margin-bottom: 15px;
}
.ql-editor img {
  max-width: 300px !important;
  width: auto !important;
  height: auto !important;
  object-fit: contain !important;
  display: block !important;
  margin: 10px auto !important;
}
</style>
