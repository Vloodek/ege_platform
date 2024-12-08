<template>
  <div id="lesson-detail">
    <div class="container">
      <!-- Боковое меню -->
      <SideBar :isTestActive="false" />

      <!-- Основной контент с деталями занятия -->
      <main class="main-content">
        <div class="lesson-detail" v-if="lesson">
          <!-- Заголовок по центру -->
          <h1 class="lesson-title">{{ lesson.name }}</h1>

          <!-- Вставка видео через iframe -->
          <div v-if="lesson.videoLink" class="video-container">
            <h3>Видеоматериал:</h3>
            <div v-if="videoEmbedUrl">
              <iframe :src="videoEmbedUrl" width="100%" height="400" frameborder="0"
                allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen></iframe>
            </div>
            <div v-else>
              <p>Ошибка: видео не доступно.</p>
            </div>
          </div>

          <!-- Блок с датой и описанием слева -->
          <div class="lesson-details">
            <div class="lesson-info">
              <p><strong>Дата занятия:</strong> {{ lesson.date }}</p>
              <p><strong>Описание:</strong> {{ lesson.description }}</p>
            </div>

            <!-- Блок с кнопками справа -->
            <div class="lesson-actions">
              <button @click="completeHomework">Выполнить ДЗ</button>
              <button @click="viewMaterials">Посмотреть материалы</button>
              <button @click="editLesson">Редактировать занятие</button> <!-- Кнопка редактирования -->
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
import SideBar from "./SideBar.vue";

export default {
  components: {
    SideBar,
  },
  data() {
    return {
      lesson: null, // Здесь будут данные занятия
      videoEmbedUrl: null, // Для хранения преобразованного URL
    };
  },
  created() {
    this.fetchLesson();
  },
  methods: {
    viewMaterials() {
      this.$router.push(`/lesson/${this.lesson.id}/materials`);
    },
    async fetchLesson() {
      
      const lessonId = this.$route.params.id;
      try {
        const response = await fetch(`http://localhost:8000/lessons/${lessonId}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
        });
        if (response.ok) {
          this.lesson = await response.json();

          // Отладочный вывод структуры lesson.files
          console.log("lesson.files как объект:", this.lesson.files);
          console.log("lesson.files в JSON:", JSON.stringify(this.lesson.files));

          // Проверяем, что lesson.files существует и является массивом
          if (this.lesson.files) {
            // Если lesson.files это Proxy, пытаемся получить исходный массив или объект
            const files = this.lesson.files && this.lesson.files.e ? this.lesson.files.e : this.lesson.files;

            // Проверяем тип данных в lesson.files
            if (Array.isArray(files)) {
              // Если это массив, оставляем как есть
              this.lesson.files = files;
            } else if (typeof files === 'string') {
              // Если это строка, разделяем её на массив
              this.lesson.files = files.split(","); // Пример разделения по запятой
            } else {
              // Если данные не соответствуют ожиданиям
              console.error("Некорректный формат данных для files:", files);
              this.lesson.files = [];
            }
          }

          this.processVideoLink(this.lesson.videoLink); // Обрабатываем ссылку видео
        } else {
          console.error("Ошибка загрузки занятия");
        }
      } catch (error) {
        console.error("Ошибка сети:", error);
      }
    },
    editLesson() {
      this.$router.push(`/lesson/${this.lesson.id}/edit`);
    },

    // Метод для преобразования ссылки видео в формат встраивания
    processVideoLink(videoLink) {
      console.log("Полученная ссылка на видео:", videoLink); // Проверим, что приходит
      if (videoLink.includes('youtube.com') || videoLink.includes('youtu.be')) {
        const videoId = this.extractYouTubeId(videoLink);
        if (videoId) {
          this.videoEmbedUrl = `https://www.youtube.com/embed/${videoId}`;
        } else {
          console.error("Ошибка: Не удалось извлечь ID из YouTube ссылки.");
          this.videoEmbedUrl = null;
        }
      } else if (videoLink.includes('vk.com/video')) {
        const embedUrl = this.extractVKVideoEmbedUrl(videoLink);
        if (embedUrl) {
          this.videoEmbedUrl = embedUrl;
        } else {
          console.error("Ошибка: Не удалось обработать VK ссылку.");
          this.videoEmbedUrl = null;
        }
      } else {
        console.error("Ошибка: Неподдерживаемый формат видео.");
        this.videoEmbedUrl = null;
      }
    },

    // Извлечение ID видео из YouTube ссылки
    extractYouTubeId(url) {
      const match = url.match(
        /(?:youtube\.com\/(?:[^/]+\/.+\/|(?:v|e(?:mbed)?)\/|\S*\?v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/
      );
      return match ? match[1] : null;
    },

    // Извлечение параметров видео из ссылки VK
    extractVKVideoEmbedUrl(url) {
      const match = url.match(/vk\.com\/video(-?\d+)_(\d+)(?:\?t=\d+s)?/);
      if (match) {
        const ownerId = match[1];
        const videoId = match[2];
        // У VK может быть хэш в ссылке для доступа к видео
        const hashMatch = url.match(/hash=([a-zA-Z0-9]+)/);
        const hash = hashMatch ? `&hash=${hashMatch[1]}` : '';
        return `https://vk.com/video_ext.php?oid=${ownerId}&id=${videoId}${hash}`;
      }
      return null;
    },

    completeHomework() {
  if (this.lesson && this.lesson.id) {
    this.$router.push(`/homework/${this.lesson.id}`); // Переход на страницу с домашкой
  } else {
    alert("Домашка не назначена для этого занятия.");
  }
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

/* Контейнер для основного контента и бокового меню */
.container {
  display: flex;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* Стили для основного контента */
.main-content {
  flex: 1;
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  margin-left: 20px;
  /* Отступ от бокового меню */
}

/* Стили для заголовка, по центру */
.lesson-title {
  font-size: 28px;
  color: #333;
  text-align: center;
}

/* Стили для контейнера с видео */
.video-container {
  margin-bottom: 20px;
}

/* Стили для блока с датой и описанием */
.lesson-details {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.lesson-info {
  flex: 1;
}

.lesson-info p {
  font-size: 18px;
  color: #555;
}

.lesson-actions {
  flex: 1;
  padding-left: 20px;
}

.lesson-actions button {
  margin-top: 10px;
  background-color: #4CAF50;
  color: white;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  width: 100%;
}

.lesson-actions button:hover {
  background-color: #45a049;
}
</style>
