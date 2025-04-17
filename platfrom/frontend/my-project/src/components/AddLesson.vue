<template>
  <div class="add-lesson-page">
    <div class="container">
      <SideBar :isTestActive="false" />

      <div class="main-content">
        <h2 class="page-title">Добавление урока</h2>

        <form @submit.prevent="handleSubmit" class="lesson-form">
          <!-- Информация об уроке -->
          <div class="lesson-info">
            <!-- Название урока -->
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

            <!-- Описание урока обычным текстовым полем -->
            <div class="form-group">
              <label for="lessonDescription">Описание урока</label>
              <textarea
                id="lessonDescription"
                v-model="lesson.description"
                placeholder="Введите описание урока"
                required
              ></textarea>
            </div>

            <!-- Переключатель типа видео -->
            <div class="form-group toggle-group">
              <label>Тип видео</label>
              <div class="toggle-container" @click="toggleVideoType">
                <div
                  class="toggle-option"
                  :class="{ active: lesson.videoType === 'video' }"
                >
                  Видео
                </div>
                <div
                  class="toggle-option"
                  :class="{ active: lesson.videoType === 'stream' }"
                >
                  Стрим
                </div>
              </div>
            </div>

            <!-- Если выбран тип Видео -->
            <div class="form-group" v-if="lesson.videoType === 'video'">
              <label for="videoLink">Ссылка на видео</label>
              <input
                type="text"
                id="videoLink"
                v-model="lesson.videoLink"
                placeholder="Введите ссылку на видео"
                @blur="validateVideoLink"
              />
              <p v-if="videoLinkError" class="error-text">
                Пожалуйста, введите корректную ссылку на видео.
              </p>
            </div>

            <!-- Если выбран тип Стрим -->
            <div class="form-group" v-else>
              <label for="iframeEmbed">Embed-код стрима</label>
              <textarea
                id="iframeEmbed"
                v-model="lesson.iframeEmbed"
                placeholder="Вставьте HTML-код iframe стрима"

              ></textarea>
            </div>
          </div>

          <!-- Материалы к занятию -->
          <div class="lesson-materials">
            <h3>Материалы к занятию</h3>
            <!-- Текст занятия через Quill -->
            <div class="form-group">
              <label for="lessonText">Текст занятия</label>
              <div ref="textEditor" class="quill-editor"></div>
            </div>

            <!-- Загрузка файлов (с drag’n’drop) -->
            <div class="form-group">
              <label for="lessonFiles">Загрузить файлы</label>
              <div
                class="drag-drop-area"
                @drop.prevent="handleDrop"
                @dragover.prevent
                @dragenter.prevent
                @click="$refs.lessonFileInput.click()"
              >
                <input
                  type="file"
                  id="lessonFiles"
                  @change="handleFileUpload"
                  multiple
                  ref="lessonFileInput"
                  class="hidden-input"
                />
                <p>Перетащите файлы сюда или нажмите для выбора</p>
              </div>
            </div>
            <small class="helper-text">
              Поддерживаемые форматы: любые файлы
            </small>

            <!-- Превью прикрепленных файлов -->
            <div class="uploaded-files">
              <h4>Загруженные файлы</h4>
              <ul>
                <li v-for="(file, index) in lesson.files" :key="index">
                  {{ file.name }}
                  <button type="button" @click="removeFile(index)">
                    Удалить
                  </button>
                </li>
              </ul>
              <p v-if="lesson.files.length === 0">Нет загруженных файлов.</p>
            </div>
          </div>

          <!-- Дата занятия и группа -->
          <div class="form-group">
            <label for="lessonDate">Дата занятия</label>
            <input
              type="datetime-local"
              id="lessonDate"
              v-model="lesson.date"
              required
            />
          </div>
          <div class="form-group">
            <label for="groupSelect">Выберите группу</label>
            <select
              id="groupSelect"
              v-model="lesson.group_id"
              required
              @focus="fetchGroups"
            >
              <option v-if="!groupsLoaded" disabled>Загрузка...</option>
              <option
                v-for="group in groups"
                :key="group.id"
                :value="group.id"
              >
                {{ group.name }}
              </option>
            </select>
          </div>

          <button type="submit" class="submit-btn">Добавить урок</button>
        </form>

        <!-- Полноразмерное изображение -->
        <div v-if="fullImage" class="full-image-modal" @click="closeImage">
          <img :src="fullImage" alt="Полноразмерное изображение" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SideBar from "../components/SideBar.vue";
import Quill from "quill";
import "quill/dist/quill.snow.css";

export default {
  name: "AddLessonPage",
  components: { SideBar },
  data() {
    return {
      lesson: {
        name: "",
        description: "",
        videoLink: "",
        iframeEmbed: "",
        videoType: "video", // "video" или "stream"
        text: "",
        files: [],
        images: [],
        date: "",
        group_id: "",
      },
      groups: [],
      groupsLoaded: false,
      videoLinkError: false,
      fullImage: null,
      // Ссылки на Quill-редакторы для текста занятия (описание урока остаётся обычным полем)
      textEditor: null,
    };
  },
  methods: {
    // Файловые операции
    handleFileUpload(event) {
      const files = Array.from(event.target.files);
      files.forEach((file) => {
        // Если изображение, сохраняем его для возможного предпросмотра (вы можете убрать, если не нужно)
        if (file.type.startsWith("image/")) {
          const reader = new FileReader();
          reader.onload = (e) => {
            this.lesson.images.push({
              file,
              preview: e.target.result,
            });
          };
          reader.readAsDataURL(file);
        } else {
          this.lesson.files.push(file);
        }
      });
    },
    handleDrop(event) {
      const files = Array.from(event.dataTransfer.files);
      files.forEach((file) => {
        if (file.type.startsWith("image/")) {
          const reader = new FileReader();
          reader.onload = (e) => {
            this.lesson.images.push({
              file,
              preview: e.target.result,
            });
          };
          reader.readAsDataURL(file);
        } else {
          this.lesson.files.push(file);
        }
      });
    },
    removeFile(index) {
      this.lesson.files.splice(index, 1);
    },
    removeImage(index) {
      this.lesson.images.splice(index, 1);
    },
    openImage(preview) {
      this.fullImage = preview;
    },
    closeImage() {
      this.fullImage = null;
    },
    async fetchGroups() {
      if (this.groupsLoaded) return;
      try {
        const response = await this.$axios.get("/groups/");
        this.groups = response.data;
        this.groupsLoaded = true;
      } catch (error) {
        console.error("Ошибка при загрузке групп", error);
      }
    },
    validateVideoLink() {
      if (this.lesson.videoType === "video") {
        const regex = /https?:\/\/.*/;
        this.videoLinkError = !regex.test(this.lesson.videoLink);
      } else {
        this.videoLinkError = false;
      }
    },
    // Красивый тоггл для типа видео
    toggleVideoType() {
      this.lesson.videoType =
        this.lesson.videoType === "video" ? "stream" : "video";
    },
    handleSubmit() {
      if (this.lesson.videoType === "stream") {
        this.lesson.videoLink = this.lesson.iframeEmbed;
      }
      const formData = new FormData();
      formData.append("name", this.lesson.name);
      formData.append("description", this.lesson.description);
      formData.append("videoLink", this.lesson.videoLink);
      formData.append("text", this.lesson.text);
      formData.append("date", this.lesson.date);
      formData.append("group_id", this.lesson.group_id);

      this.lesson.images.forEach((imgObj) => {
        formData.append("images", imgObj.file);
      });
      this.lesson.files.forEach((file) => {
        formData.append("files", file);
      });

      this.$axios
  .post("/lessons/", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  })

        .then((response) => {
          console.log("Урок успешно добавлен", response.data);
          this.$router.push("/day-plan");
        })
        .catch((error) => {
          console.error("Ошибка при добавлении урока", error);
        });
    },

    // Инициализация Quill-редактора для текста занятия
    initEditors() {
      this.$nextTick(() => {
        const textEl = this.$refs.textEditor;
        if (!textEl) {
          console.error("Не найден элемент для Quill-редактора");
          return;
        }
        // Опции тулбара без смены шрифта
        const toolbarOptions = [
          [{ header: "1" }, { header: "2" }],
          [{ list: "ordered" }, { list: "bullet" }],
          ["bold", "italic", "underline"],
          [{ align: [] }],
          ["link", "image"]
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

        this.textEditor = new Quill(textEl, {
          theme: "snow",
          modules: {
            toolbar: {
              container: toolbarOptions,
              handlers: { image: customImageHandler }
            }
          }
        });

        this.textEditor.root.addEventListener("paste", (e) => {
          this.handlePaste(e, this.textEditor);
        });

        this.textEditor.on("text-change", () => {
          this.lesson.text = this.textEditor.root.innerHTML;
        });
      });
    },
    async uploadAndInsertImage(quill, file) {
      const formData = new FormData();
      formData.append("image", file);
      try {
        const response =  await this.$axios.post("/upload_temp_image", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
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
    handlePaste(e, quill) {
      const clipboardData = e.clipboardData || window.clipboardData;
      if (!clipboardData) return;
      const items = clipboardData.items;
      if (!items) return;
      for (let i = 0; i < items.length; i++) {
        const item = items[i];
        if (item.type.indexOf("image") !== -1) {
          e.preventDefault();
          const file = item.getAsFile();
          if (file) {
            this.uploadAndInsertImage(quill, file);
          }
        }
      }
    }
  },
  mounted() {
    this.initEditors();
    this.fetchGroups();
  }
};
</script>

<style scoped>
/* Общий стиль страницы */
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
  width: auto;
}

.submit-btn:hover {
  background-color: #0f3f3b;
}

.uploaded-files {
  margin-top: 20px;
}

.uploaded-files ul {
  list-style: none;
  padding-left: 0;
}

.uploaded-files li {
  margin-bottom: 5px;
}

/* Стили для drag-n-drop, перекрашенные в зеленые тона */
.drag-drop-area {
  border: 2px dashed #115544;
  padding: 20px;
  background-color: #ffffff;
  text-align: center;
  border-radius: 5px;
  cursor: pointer;
}

.drag-drop-area p {
  font-size: 16px;
  color: #115544;
}

.hidden-input {
  display: none;
}

.helper-text {
  font-size: 12px;
  color: #115544;
}

.page-title,
h3,
h4 {
  font-weight: 500;
}

/* Стили Quill */
.quill-editor {
  height: 200px;
  border: 1px solid #ccc;
  border-radius: 5px;
  background-color: #fafafa;
}
.ql-editor img {
  max-width: 70% !important;
  height: auto !important;
  object-fit: contain !important;
  display: block !important;
  margin: 10px auto !important;
}
  
/* Переключатель типа видео */
.toggle-group {
  margin-bottom: 15px;
}
.toggle-container {
  display: flex;
  border: 1px solid #115544;
  border-radius: 25px;
  overflow: hidden;
  cursor: pointer;
  width: fit-content;
}
.toggle-option {
  padding: 8px 16px;
  background-color: #ffffff;
  color: #115544;
  transition: background 0.3s, color 0.3s;
}
.toggle-option.active {
  background-color: #115544;
  color: #fff;
}
</style>
