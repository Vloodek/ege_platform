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
            <h1 class="homework-title centered">{{ homework.description || "Детали домашнего задания" }}</h1>
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

          <!-- Кнопка "Добавить ответ" -->
          <BaseButton color="green" @click="showResponseForm = true" v-if="!showResponseForm">
            Добавить ответ
          </BaseButton>

          <!-- Форма ответа -->
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

            <!-- Кнопка "Отправить" -->
            <BaseButton color="green" @click="submitResponse">Отправить</BaseButton>
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
      uploadedFiles: []
    };
  },
  computed: {
    homeworkImages() {
      return this.homework?.files.filter(file =>
        /\.(jpg|jpeg|png|gif)$/i.test(file)
      ) || [];
    },
    otherFiles() {
      return this.homework?.files.filter(file =>
        !/\.(jpg|jpeg|png|gif)$/i.test(file)
      ) || [];
    },
  },
  created() {
    this.fetchHomeworkDetails();
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
          this.homework = data[0];
        } else {
          console.error("Ошибка загрузки домашнего задания");
        }
      } catch (error) {
        console.error("Ошибка сети:", error);
      }
    },
    getFileUrl(file) {
      return `http://localhost:8000/${file.replace(/\\/g, '/')}`;
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
        return date.toLocaleDateString("ru-RU", { day: "2-digit", month: "long", year: "numeric", hour: "2-digit", minute: "2-digit" });
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
  formData.append("homework_id", this.$route.params.id); // Убедитесь, что название параметра совпадает с тем, что на сервере
  
  // Извлекаем объект user из localStorage
  const userData = JSON.parse(localStorage.getItem('user')); // Преобразуем строку в объект
  
  if (userData && userData.userId) {
    formData.append("user_id", userData.userId); // Добавляем user_id из объекта
  } else {
    console.error("Не найден userId в localStorage");
    alert("Ошибка: Не найден userId в localStorage");
    return;
  }

  formData.append("comment", this.responseText);

  this.uploadedFiles.forEach((file, index) => {
    formData.append(`file_${index}`, file);
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
}




  },
};
</script>

<style scoped>
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
}

.response-form {
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
</style>
