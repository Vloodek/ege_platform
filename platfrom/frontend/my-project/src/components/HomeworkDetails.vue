<template>
  <div id="homework-details">
    <div class="container">
      <!-- Боковое меню -->
      <SideBar :isTestActive="false" />

      <!-- Основной контент -->
      <main class="main-content">
        <div v-if="homework">
          <!-- Стрелка назад и центрированный заголовок -->
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

          <!-- Текст задания (description) -->
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


          <!-- Прикрепленные файлы -->
          <div v-if="otherFiles.length" class="files-section">
            <ul>
              <li v-for="(file, index) in otherFiles" :key="index">
                <a :href="getFileUrl(file)" target="_blank">
                  <img src="@/assets/svg/files.svg" alt="file icon" class="file-icon" />
                  {{ file.split('/').pop() }}
                </a>
              </li>
            </ul>
          </div>

          <!-- Если пользователь преподаватель, отображаем кнопку "Изменить ДЗ" -->
          <div v-if="isTeacher" style="margin-top: 20px;">
            <BaseButton color="green" @click="goToEditHomework">
              Изменить ДЗ
            </BaseButton>
          </div>

          <!-- Если пользователь студент, отображается кнопка "Добавить ответ" (оставляем как есть) -->
          <div v-else>
            <BaseButton color="green" @click="showResponseForm = true" v-if="!showResponseForm">
              Добавить ответ
            </BaseButton>
          </div>

          <!-- Форма ответа (для студента) -->
          <div v-if="showResponseForm" class="response-form">
            <h2>Ваш ответ:</h2>
            <div class="uploaded-files">
              <div v-for="(file, index) in uploadedFiles" :key="index" class="uploaded-file">
                📄 {{ file.name }}
              </div>
            </div>
            <h3>Комментарий или ответ к домашней работе:</h3>
            <textarea v-model="responseText" placeholder="Введите ваш ответ..."></textarea>
            <h3>Прикрепление файлов к домашней работе:</h3>
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

export default {
  components: {
    SideBar,
    BaseButton
  },
  data() {
    return {
      homework: null,
      showResponseForm: false,
      responseText: "",
      uploadedFiles: [],
      isTeacher: false
    };
  },
  computed: {
  // Получаем изображения из `homework.images`, если они есть
  homeworkImages() {
    return Array.isArray(this.homework?.images) ? this.homework.images : [];
  },

  // Фильтруем файлы, исключая изображения
  otherFiles() {
    return Array.isArray(this.homework?.files)
      ? this.homework.files.filter(file => !/\.(jpg|jpeg|png|gif)$/i.test(file))
      : [];
  }
}

,
  created() {
    this.fetchHomeworkDetails();
    const userData = JSON.parse(localStorage.getItem("user"));
    if (userData && userData.role === "teacher") {
      this.isTeacher = true;
    }
  },
  methods: {
    async fetchHomeworkDetails() {
      const homeworkId = this.$route.params.id;
      try {
        const response = await fetch(`http://localhost:8000/homeworks/${homeworkId}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
        });
        if (response.ok) {
          const data = await response.json();
          console.log("Ответ от сервера:", data);  // <-- Смотрим, что приходит
          // Предположим, что возвращается массив, берем первый элемент
          this.homework = data[0];
        } else {
          console.error("Ошибка загрузки домашнего задания");
        }
      } catch (error) {
        console.error("Ошибка сети:", error);
      }
    },
    getFileUrl(file) {
    if (!file) return "";
    return `http://localhost:8000/${file.replace(/\\/g, "/")}`;
  },
    openImage(imageUrl) {
      window.open(imageUrl, '_blank');
    },
    formatDate(dateString) {
      try {
        const cleanedDateString = dateString.split('.')[0]; 
        const date = new Date(cleanedDateString);
        if (isNaN(date.getTime())) {
          return "Неверный формат даты";
        }
        return date.toLocaleDateString("ru-RU", { 
          day: "2-digit", month: "long", year: "numeric", 
          hour: "2-digit", minute: "2-digit" 
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
    async submitResponse() {
      if (!this.responseText && !this.uploadedFiles.length) {
        alert("Добавьте ответ или прикрепите файлы!");
        return;
      }
      const formData = new FormData();
      formData.append("homework_id", this.$route.params.id);
      const userData = JSON.parse(localStorage.getItem('user'));
      if (userData && userData.userId) {
        formData.append("user_id", userData.userId);
      } else {
        alert("Ошибка: Не найден userId в localStorage");
        return;
      }
      formData.append("comment", this.responseText);
      formData.append("client_submission_time", new Date().toISOString());
      this.uploadedFiles.forEach(file => {
        formData.append("files", file);
      });
      try {
        const response = await fetch("http://localhost:8000/submit_homework", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
          body: formData,
        });
        if (response.ok) {
          console.log("Ответ успешно отправлен!");
          alert("Ответ отправлен!");
          this.showResponseForm = false;
          this.responseText = "";
          this.uploadedFiles = [];
        } else {
          const errorData = await response.json();
          console.error("Ошибка при отправке ответа:", errorData);
          alert("Ошибка при отправке ответа");
        }
      } catch (error) {
        console.error("Ошибка сети при отправке ответа:", error);
        alert("Ошибка сети при отправке ответа");
      }
    },
    goToEditHomework() {
  this.$router.push({ name: "EditHomework", params: { id: this.homework.id } });
},

    toggleEditForm() {
      this.showEditForm = true;
    },
    handleHomeworkUpdated(updatedHomework) {
      this.homework = updatedHomework;
      this.showEditForm = false;
      alert("Домашнее задание успешно обновлено");
    },
    confirmExit() {
      const confirmed = confirm("Вы уверены, что не сохранили изменения?");
      if (confirmed) {
        this.$router.push(`/lesson/${this.homework.lessonId}/details`);
      }
    }
  },
};
</script>

<style scoped>
/* Основной контейнер и стили, адаптируйте под свой дизайн */
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
.response-form, .edit-form {
  margin-top: 30px;
}
textarea {
  width: 100%;
  height: 100px;
  border: 1px solid #ddd;
  padding: 10px;
  border-radius: 8px;
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
</style>
