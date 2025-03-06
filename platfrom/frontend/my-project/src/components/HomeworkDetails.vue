<template>
  <div id="homework-details">
    <div class="container">
      <!-- Боковое меню -->
      <SideBar :isTestActive="false" />

      <!-- Основной контент -->
      <main class="main-content">
        <div v-if="homework">
          <!-- Заголовок и стрелка назад -->
          <div class="header-section">
            <div class="back-arrow" @click="$router.go(-1)"></div>
            <h1 class="homework-title centered">
              {{ homework.description || "Детали домашнего задания" }}
            </h1>
          </div>

          <!-- Дедлайн -->
          <div class="homework-deadline">
            <strong>Дедлайн: </strong>{{ formatDate(homework.date) }}
          </div>

          <!-- Текст задания -->
          <div v-if="homework.text" class="homework-description">
            <p>{{ homework.text }}</p>
          </div>

          <!-- Отображение изображений -->
          <div v-if="homeworkImages.length" class="images-container">
            <div class="images">
              <img 
                v-for="(image, index) in homeworkImages" 
                :key="index" 
                :src="getFileUrl(image)" 
                alt="Homework Image" 
                @click="openImage(getFileUrl(image))"
              />
            </div>
          </div>

          <!-- Отображение прикрепленных файлов -->
          <div v-if="otherFiles.length" class="files-section">
            <ul>
              <li v-for="(file, index) in otherFiles" :key="index">
                <a :href="getFileUrl(file)" target="_blank">
                  <img src="@/assets/svg/files.svg" alt="file icon" class="file-icon" />
                  {{ getFileName(file) }}
                </a>
              </li>
            </ul>
          </div>

          <!-- Если преподаватель, кнопка редактирования ДЗ -->
          <div v-if="isTeacher" style="display: flex; justify-content: space-between; margin-top: 20px;">
  <BaseButton color="green" @click="goToEditHomework">
    Изменить ДЗ
  </BaseButton>
  <BaseButton color="white" @click="goToResponses">
    Отклики студентов
  </BaseButton>
</div>

          <!-- Для студентов: если ответ уже отправлен, показываем его -->
          <div v-if="!isTeacher && submission && !showResponseForm" style="margin-top: 20px;">
            <h2>Ваш ответ:</h2>
            <p>{{ submission.comment }}</p>
            <div class="uploaded-files">
              <div 
                v-for="(file, index) in submission.files" 
                :key="index" 
                class="uploaded-file"
              >
                📄 <a :href="getFileUrl(file)" target="_blank">{{ getFileName(file) }}</a>
              </div>
            </div>
            <BaseButton color="green" @click="editSubmission">
              Редактировать ответ
            </BaseButton>
          </div>

          <!-- Форма ответа (создание/редактирование) для студента -->
          <div v-if="showResponseForm" class="response-form">
            <h2>Редактирование ответа</h2>
            <!-- Отображение уже загруженных файлов с возможностью удаления -->
            <div v-if="existingSubmissionFiles.length">
              <p>Прикрепленные файлы:</p>
              <ul>
                <li v-for="(file, index) in existingSubmissionFiles" :key="index">
                  <a :href="getFileUrl(file)" target="_blank">{{ getFileName(file) }}</a>
                  <button type="button" class="remove-btn" @click="removeSubmissionFile(index)">❌</button>
                </li>
              </ul>
            </div>
            <!-- Отображение новых добавленных файлов -->
            <div v-if="uploadedFiles.length">
              <p>Новые файлы:</p>
              <ul>
                <li v-for="(file, index) in uploadedFiles" :key="index">
                  📄 {{ file.name }}
                  <button type="button" class="remove-btn" @click="removeUploadedFile(index)">❌</button>
                </li>
              </ul>
            </div>
            <h3>Комментарий или ответ:</h3>
            <textarea v-model="responseText" placeholder="Введите ваш ответ..."></textarea>
            <h3>Прикрепить файлы:</h3>
            <div class="file-drop-zone" @dragover.prevent @drop="handleDrop">
              <p>Перетащите файлы сюда или <span @click="selectFile">выберите файл</span></p>
              <input type="file" multiple ref="fileInput" @change="handleFileUpload" hidden />
            </div>
            <form @submit.prevent="submitResponse" class="response-form">
              <BaseButton type="submit" color="green">Отправить</BaseButton>
            </form>
          </div>
        </div>

        <div v-else>
          <p>Загрузка задания...</p>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import SideBar from "../components/SideBar.vue";
import BaseButton from "@/components/UI/BaseButton.vue";
import axios from "axios";

export default {
  components: { SideBar, BaseButton },
  data() {
    return {
      homework: null,
      submission: null,
      showResponseForm: false,
      responseText: "",
      uploadedFiles: [],
      // Для редактирования уже отправленного ответа
      existingSubmissionFiles: [],
      isTeacher: false,
      filesToDelete: [], // Добавьте это поле
    };
  },
  computed: {
    // Если homework.images – массив строк (пути)
    homeworkImages() {
      return Array.isArray(this.homework?.images) ? this.homework.images : [];
    },
    // Файлы, кроме изображений
    otherFiles() {
      return Array.isArray(this.homework?.files)
        ? this.homework.files.filter(file => !/\.(jpg|jpeg|png|gif)$/i.test(file))
        : [];
    },
  },
  async created() {
    await this.fetchHomeworkDetails();
    const userData = JSON.parse(localStorage.getItem("user"));
    if (userData && userData.role === "teacher") {
      this.isTeacher = true;
    } else {
      this.isTeacher = false;
      await this.fetchSubmission();
    }
  },
  methods: {
    async fetchHomeworkDetails() {
      const homeworkId = this.$route.params.id;
      try {
        const response = await fetch(`http://localhost:8000/homeworks/${homeworkId}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` },
        });
        if (response.ok) {
          const data = await response.json();
          // Предполагаем, что возвращается массив – берем первый элемент
          this.homework = data[0];
        } else {
          console.error("Ошибка загрузки домашнего задания");
        }
      } catch (error) {
        console.error("Ошибка сети:", error);
      }
    },
    async fetchSubmission() {
      const homeworkId = this.$route.params.id;
      const userData = JSON.parse(localStorage.getItem("user"));
      if (!userData || !userData.userId) return;
      try {
        const response = await axios.get(
          `http://localhost:8000/homeworks/${homeworkId}/submission?user_id=${userData.userId}`,
          { headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` } }
        );
        this.submission = response.data;
      } catch (error) {
        console.error("Ошибка загрузки отправленного ответа:", error);
      }
    },
    getFileUrl(file) {
      if (!file) return "";
      if (typeof file === "string") {
        return `http://localhost:8000/${file.replace(/\\/g, "/")}`;
      }
      return file.url || "";
    },
    getFileName(file) {
      if (!file) return "";
      if (typeof file === "string") {
        return file.split('/').pop();
      }
      return file.url ? file.url.split('/').pop() : (file.file ? file.file.name : "");
    },
    openImage(imageUrl) {
      window.open(imageUrl, "_blank");
    },
    formatDate(dateString) {
      try {
        const cleanedDateString = dateString.split(".")[0];
        const date = new Date(cleanedDateString);
        if (isNaN(date.getTime())) return "Неверный формат даты";
        return date.toLocaleDateString("ru-RU", {
          day: "2-digit",
          month: "long",
          year: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        });
      } catch (error) {
        return "Ошибка даты";
      }
    },
    selectFile() {
      this.$refs.fileInput.click();
    },
    handleFileUpload(event) {
      this.uploadedFiles.push(...event.target.files);
    },
    handleDrop(event) {
      event.preventDefault();
      if (event.dataTransfer.files.length) {
        this.uploadedFiles.push(...event.dataTransfer.files);
      }
    },
    goToEditHomework() {
      this.$router.push({ name: "EditHomework", params: { id: this.homework.id } });
    },
    editSubmission() {
      // Заполняем форму данными из существующего ответа
      this.responseText = this.submission.comment || "";
      // Копируем список файлов, полученных с сервера, для редактирования
      this.existingSubmissionFiles = [...this.submission.files];
      this.showResponseForm = true;
    },
    removeSubmissionFile(index) {
  const file = this.existingSubmissionFiles[index];
  this.filesToDelete.push(file); // Добавляем файл в массив для удаления
  this.existingSubmissionFiles.splice(index, 1); // Удаляем файл из списка прикрепленных
},
    removeUploadedFile(index) {
      this.uploadedFiles.splice(index, 1);
    },
    async submitResponse() {
  if (!this.responseText && !this.uploadedFiles.length && !this.existingSubmissionFiles.length) {
    alert("Добавьте ответ или прикрепите файлы!");
    return;
  }

  const formData = new FormData();
  formData.append("homework_id", this.$route.params.id);

  const userData = JSON.parse(localStorage.getItem("user"));
  if (userData && userData.userId) {
    formData.append("user_id", userData.userId);
  } else {
    alert("Ошибка: Не найден userId в localStorage");
    return;
  }

  formData.append("comment", this.responseText);
  formData.append("client_submission_time", new Date().toISOString());

  // Передаём обновлённый список оставшихся файлов
  formData.append("existing_files", JSON.stringify(this.existingSubmissionFiles));
  // Передаём список файлов, которые нужно удалить
  formData.append("files_to_delete", JSON.stringify(this.filesToDelete));

  // Добавляем новые файлы
  this.uploadedFiles.forEach(file => {
    formData.append("files", file);
  });

  try {
    let response;
    if (this.submission) {
      response = await axios.put(
        `http://localhost:8000/update_submission/${this.submission.id}`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
    } else {
      response = await axios.post(
        "http://localhost:8000/submit_homework",
        formData,
        { headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` } }
      );
    }

    if (response.status === 200 || response.status === 201) {
      alert("Ответ успешно отправлен!");
      this.showResponseForm = false;
      this.responseText = "";
      this.uploadedFiles = [];
      this.filesToDelete = []; // Очищаем список удалённых файлов
      await this.fetchSubmission();
    } else {
      alert("Ошибка при отправке ответа");
    }
  } catch (error) {
    console.error("Ошибка при отправке ответа:", error);
    alert("Ошибка при отправке ответа");
  }
}

,
    cancelEdit() {
      this.$router.push(`/lesson/${this.homework.lesson_id}/details`);
    },
    goToResponses() {
    this.$router.push({ name: "homework-submissions", params: { id: this.$route.params.id } });
  },
  },
};
</script>

<style scoped>
/* Основные стили */
#homework-details {
  padding: 20px;
}
.images-container {
  margin-top: 20px;
  text-align: center;
}
.images img {
  max-width: 150px;
  margin: 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.3s ease;
}
.images img:hover {
  transform: scale(1.5);
}
.container {
  display: flex;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}
.main-content {
  flex: 1;
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  margin-left: 20px;
  position: relative;
}
.header-section {
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
  width: 20px;
  height: 20px;
  background-color: #115544;
  clip-path: polygon(100% 0, 0 50%, 100% 100%);
  cursor: pointer;
}
.homework-title {
  flex: 1;
  font-size: 24px;
  color: #115544;
  font-weight: 500;
  text-align: center;
  margin: 0;
}
.homework-deadline {
  margin: 10px 0;
}
.homework-description {
  margin: 20px 0;
}
.uploaded-files {
  margin: 10px 0;
}
.uploaded-file {
  background: #eee;
  padding: 5px;
  border-radius: 5px;
  margin: 5px 0;
}
.files-section ul {
  list-style: none;
  padding: 0;
  margin: 20px 0 0;
}
.files-section ul li {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}
.files-section ul li a {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: inherit;
  font-size: 16px;
}
.file-icon {
  width: 42px;
  height: 42px;
  margin-right: 10px;
  flex-shrink: 0;
}
.homework-files a:hover {
  text-decoration: underline;
}
/* Кнопки */
.remove-btn {
  background: transparent;
  color: red;
  border: none;
  cursor: pointer;
  font-size: 16px;
  margin-left: 5px;
}
.submit-btn, .add-btn {
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
.submit-btn:hover, .add-btn:hover {
  background-color: #1e9275;
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
.page-title, h3, h4 {
  font-weight: 500;
}
.file-drop-zone {
  border: 2px dashed #115544;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  margin: 10px 0;
  border-radius: 10px;
}
.file-drop-zone p {
  margin: 0;
}
.file-drop-zone span {
  color: #115544;
  text-decoration: underline;
  cursor: pointer;
}
</style>
