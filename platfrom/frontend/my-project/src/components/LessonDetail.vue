<template>
  <div id="lesson-detail">
    <div class="container">
      <!-- Боковое меню -->
      <SideBar :isTestActive="false" />

      <!-- Основной контент -->
      <main class="main-content">
        <div class="lesson-detail" v-if="lesson">
          <!-- Стрелка возврата и заголовок -->
<div class="header-section">
  <div class="back-arrow" @click="goBack"></div>
  <h1 class="lesson-title">{{ lesson.name }}</h1>
</div>


          <!-- Видео блок -->
          <div v-if="lesson.videoLink" class="video-container">
            <iframe :src="videoEmbedUrl" width="100%" height="400" frameborder="0" allowfullscreen></iframe>
          </div>

          <!-- Блок с описанием и кнопками -->
          <div class="content-section">
            <!-- Левая часть -->
            <div class="left-column">
              <!-- Иконка календаря и дата -->
              <div class="calendar">
  <img class="calendar-icon" src="@/assets/svg/TaskDetail/calendar.svg" alt="Calendar Icon" />
  <span class="lesson-date">{{ formatDateTime(lesson.date) }}</span>
</div>

              <!-- Описание занятия -->
              <p class="lesson-description">{{ lesson.description }}</p>
              <!-- Чекбокс "Просмотрено" -->
              <div class="checkbox-container">
                <input type="checkbox" id="watched" v-model="lesson.watched" />
                <label for="watched">Просмотрено</label>
              </div>
            </div>

            <!-- Правая часть -->
            <div class="right-column">
              <button class="lesson-button white" @click="viewMaterials">Материалы занятия</button>
              <button class="lesson-button green" @click="completeHomework">Выполнить ДЗ</button>
              <button class="lesson-button green" @click="editLesson">Редактировать</button>
            </div>
          </div>
        </div>

        <div v-else>
          <p>Загрузка...</p>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import SideBar from "./SideBar.vue";

export default {
  components: {
    SideBar,
  },
  data() {
    return {
      lesson: null,
      videoEmbedUrl: null,
    };
  },
  created() {
    this.fetchLesson();
  },
  methods: {
    goBack() {
      this.$router.go(-1);
    },
    async fetchLesson() {
      const lessonId = this.$route.params.id;
      try {
        const response = await axios.get(`/lessons/${lessonId}`);
        this.lesson = response.data;
        this.processVideoLink(this.lesson.videoLink);
      } catch (error) {
        console.error("Ошибка загрузки занятия", error);
      }
    },
    processVideoLink(videoLink) {
      if (videoLink.includes("youtube.com") || videoLink.includes("youtu.be")) {
        const videoId = this.extractYouTubeId(videoLink);
        this.videoEmbedUrl = videoId ? `https://www.youtube.com/embed/${videoId}` : null;
      } else {
        console.error("Неподдерживаемый формат видео.");
        this.videoEmbedUrl = null;
      }
    },
    extractYouTubeId(url) {
      const match = url.match(/(?:youtube\.com.*[?&]v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
      return match ? match[1] : null;
    },
    viewMaterials() {
      this.$router.push(`/lesson/${this.lesson.id}/materials`);
    },
    completeHomework() {
      this.$router.push(`/homework/${this.lesson.id}`);
    },
    editLesson() {
      this.$router.push(`/lesson/${this.lesson.id}/edit`);
    },
    formatDateTime(datetime) {
      const options = {
        day: "2-digit",
        month: "2-digit",
        year: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
      };
      return new Date(datetime).toLocaleString("ru-RU", options);
    },
  },
};
</script>



<style scoped>
#lesson-detail {
  display: flex;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.container {
  display: flex;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}
.body{
  font-family: 'Navigo', sans-serif;
}
.main-content {
  flex: 1;
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  margin-left: 20px;
}

.back-arrow {
  position: absolute; /* Размещаем стрелку независимо от потока */
  left: 0; /* Привязываем к левому краю контейнера */
  top: 50%; /* Центруем по вертикали */
  transform: translateY(-50%); /* Устраняем смещение */
  width: 20px;
  height: 20px;
  background-color: #115544;
  clip-path: polygon(100% 0, 0 50%, 100% 100%);
  cursor: pointer;
}

.lesson-title {
  font-size: 24px;
  color: #115544;
  margin: 0;
  font-weight: 500;
}

.video-container {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.content-section {
  display: flex;
  justify-content: space-between;
}

.left-column {
  flex: 1;
}

.calendar {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.calendar-icon {
  width: 24px;
  height: 24px;
  margin-right: 10px;
}

.lesson-date {
  font-size: 16px;
  color: #000000;
  padding-top: 6px;
}

.lesson-description {
  margin: 10px 0;
  font-size: 16px;
  color: #000000;
}

.checkbox-container {
  display: flex;
  align-items: center;
  margin-top: 10px;
}

.checkbox-container input[type="checkbox"] {
  appearance: none;
  width: 20px;
  height: 20px;
  border: 2px solid #115544;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 10px;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  background-color: transparent;
}

.checkbox-container input[type="checkbox"]:checked {
  background-color: #115544;
  border-color: #115544;
}

.checkbox-container input[type="checkbox"]:checked::after {
  content: "✔";
  color: #fff;
  font-size: 14px;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}


.checkbox-container label {
  font-size: 16px;
  color: #333;
}

.right-column {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.lesson-button {
  padding: 10px;
  font-size: 16px;
  border: 2px solid #115544;
  border-radius: 20px;
  cursor: pointer;
  text-align: center;
  height: 54px;
  font-family: 'Navigo', sans-serif;
  font-weight: 300;
  
}

.lesson-button.green {
  background-color: #115544;
  color: #fff;
}

.lesson-button.white {
  background-color: #fff;
  color: #000000;
}

.lesson-button:hover {
  opacity: 0.8;
}
.header-section {
  position: relative; /* Для позиционирования стрелки */
  display: flex;
  justify-content: center; /* Центруем заголовок */
  align-items: center; /* Выравниваем элементы по вертикали */
  margin-bottom: 20px;
}
</style>
