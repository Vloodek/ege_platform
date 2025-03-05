<template>
  <div class="add-lesson-page">
    <div class="container">
      <SideBar :isTestActive="false" />

      <div class="main-content">
        <h2 class="page-title">Добавление урока</h2>

        <form @submit.prevent="handleSubmit" class="lesson-form">
          <div class="lesson-info">
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
              <label for="lessonFiles">Загрузить файлы</label>
              <div
                class="drag-drop-area"
                @drop.prevent="handleDrop"
                @dragover.prevent
                @dragenter.prevent
              >
                <input
                  type="file"
                  id="lessonFiles"
                  @change="handleFileUpload"
                  multiple
                   style="display: none;"
                />
                <p>Перетащите файлы сюда или выберите</p>
              </div>
            </div>
            <small class="helper-text">Поддерживаемые форматы: любые файлы</small>

            <div class="uploaded-images">
              <h4>Загруженные изображения</h4>
              <div v-if="lesson.images.length > 0" class="images-preview">
                <div v-for="(image, index) in lesson.images" :key="index" class="image-preview">
                  <img :src="image.preview" alt="Загруженное изображение" @click="openImage(image.preview)" />
                  <button type="button" class="delete-btn" @click="removeImage(index)">&times;</button>
                </div>
              </div>
              <p v-else>Нет загруженных изображений.</p>
            </div>

            <div class="uploaded-files">
              <h4>Загруженные файлы</h4>
              <ul>
                <li v-for="(file, index) in lesson.files" :key="index">
                  {{ file.name }}
                  <button type="button" @click="removeFile(index)">Удалить</button>
                </li>
              </ul>
              <p v-if="lesson.files.length === 0">Нет загруженных файлов.</p>
            </div>
          </div>

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
  <select id="groupSelect" v-model="lesson.group_id" required @focus="fetchGroups">
    <option v-if="!groupsLoaded" disabled>Загрузка...</option>
    <option v-for="group in groups" :key="group.id" :value="group.id">
      {{ group.name }}
    </option>
  </select>
</div>


          <button type="submit" class="submit-btn">Добавить урок</button>
        </form>

        <div v-if="fullImage" class="full-image-modal" @click="closeImage">
          <img :src="fullImage" alt="Полноразмерное изображение" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SideBar from "../components/SideBar.vue";
import axios from "axios";

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
        group_id: "",  // Добавляем выбор группы
      },
      groups: [], // Список групп
      groupsLoaded: false, // Флаг, загружены ли группы
      videoLinkError: false,
      fullImage: null,
    };
  },
  methods: {
    handleFileUpload(event) {
      const files = Array.from(event.target.files);
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
    async fetchGroups() {
  if (this.groupsLoaded) return; // Чтобы не загружать снова, если уже загружено

  console.log("🔵 Загрузка списка групп...");
  try {
    const response = await axios.get("http://localhost:8000/groups/");
    console.log("✅ Группы загружены:", response.data);
    this.groups = response.data;
    this.groupsLoaded = true; // Отмечаем, что загрузили
  } catch (error) {
    console.error("❌ Ошибка при загрузке групп", error);
  }
}
,
    removeImage(index) {
      this.lesson.images.splice(index, 1);
    },
    removeFile(index) {
      this.lesson.files.splice(index, 1);
    },
    validateVideoLink() {
      const regex = /https?:\/\/.*/;
      this.videoLinkError = !regex.test(this.lesson.videoLink);
    },
    handleSubmit() {
      console.log("🟡 Отправка формы урока...");
  const formData = new FormData();
  formData.append("name", this.lesson.name);
  formData.append("description", this.lesson.description);
  formData.append("videoLink", this.lesson.videoLink);
  formData.append("text", this.lesson.text);
  formData.append("date", this.lesson.date);
  formData.append("group_id", this.lesson.group_id); // Добавляем ID группы

  this.lesson.images.forEach((imageObj) => {
    formData.append("images", imageObj.file);
  });

  this.lesson.files.forEach((file) => {
    formData.append("files", file);
  });

  axios
    .post("http://localhost:8000/lessons/", formData, {
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
mounted() {
  console.log("🔵 AddLessonPage.vue загружен!");
  console.log("🔵 mounted() вызван");
    this.fetchGroups(); // Вызываем метод при загрузке страницы
  },

    openImage(preview) {
      this.fullImage = preview;
    },
    closeImage() {
      this.fullImage = null;
    },
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
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  width: auto;
}

.submit-btn:hover {
  background-color: #45a049;
}

.images-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.image-preview {
  position: relative;
  cursor: pointer;
}

.image-preview img {
  max-width: 100px;
  max-height: 100px;
  border: 1px solid #ddd;
  border-radius: 5px;
  object-fit: cover;
}

.image-preview .delete-btn {
  position: absolute;
  top: 5px;
  right: 5px;
  background: rgba(255, 255, 255, 0.8);
  color: #ff0000;
  border: none;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  line-height: 16px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.image-preview .delete-btn:hover {
  background: rgba(255, 0, 0, 0.8);
  color: #fff;
}

.full-image-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.full-image-modal img {
  max-width: 90%;
  max-height: 90%;
  border-radius: 10px;
}

/* Drag and Drop area */
.drag-drop-area {
  border: 2px dashed #4caf50;
  padding: 20px;
  background-color: #e8f5e9;
  text-align: center;
  border-radius: 5px;
  cursor: pointer;
}

.drag-drop-area p {
  font-size: 16px;
  color: #4caf50;
}

.hidden-input {
  display: none;
}
.page-title, h3, h4 {
  font-weight: 500; /* Было 700 */
}

</style>
