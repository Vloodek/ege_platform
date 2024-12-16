<template>
  <div id="materials-page">
    <div class="container">
      <!-- Боковое меню -->
      <SideBar :isTestActive="false" />

      <!-- Основной контент -->
      <main class="main-content">
        <div v-if="lesson">
          <!-- Стрелка назад и центрированный заголовок -->
          <div class="header-section">
            <div class="back-arrow" @click="goBack"></div>
            <h1 class="lesson-title centered">{{ lesson.name }}</h1>
          </div>

          <!-- Описание занятия -->
          <div v-if="lesson.text" class="lesson-description">
            <p>{{ lesson.text }}</p>
          </div>

          <!-- Отображение изображений -->
          <div v-if="images.length" class="images-container">
            <div class="images">
              <img v-for="image in images" :src="image" :alt="lesson.name" :key="image" @click="openImage(image)" />
            </div>
          </div>

          <!-- Список файлов -->
          <div v-if="files.length" class="files-section">
            <ul>
              <li v-for="file in files" :key="file">
                <a :href="file" download @click.prevent="downloadFile(file)">
                  <img src="@/assets/svg/files.svg" alt="file icon" class="file-icon" />
                  {{ getFileName(file) }}
                </a>
              </li>
            </ul>
          </div>
        </div>
        <div v-else>
          <p>Загрузка материалов...</p>
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
      lesson: null,
      images: [],
      files: [],
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
        const response = await fetch(`http://localhost:8000/lessons/${lessonId}`, {
            headers: {
                Authorization: `Bearer ${localStorage.getItem('access_token')}`,
            },
        });
        if (response.ok) {
            this.lesson = await response.json();
            console.log("Ответ от сервера:", this.lesson); // Печатаем весь ответ
            console.log("Изображения из ответа:", this.lesson.images); // Печатаем изображения
            console.log("Файлы из ответа:", this.lesson.files); // Печатаем файлы

            this.processMaterials();
        } else {
            console.error("Ошибка загрузки материалов");
        }
    } catch (error) {
        console.error("Ошибка сети:", error);
    }
},

processMaterials() {
    const baseUrl = "http://localhost:8000"; // Базовый URL сервера

    console.log("Обработка изображений и файлов:", this.lesson);

    // Обработка изображений
    if (this.lesson.image_links && this.lesson.image_links.length > 0) {
        const allImages = Array.isArray(this.lesson.image_links)
            ? this.lesson.image_links
            : this.lesson.image_links.split(",");
        console.log("Обработанные пути изображений:", allImages);
        this.images = allImages.map(image => {
            image = image.replace(/\\/g, "/");  // Заменяем обратные слэши на прямые
            return `${baseUrl}/${image}`;       // Формируем полный URL
        });
    } else {
        console.log("Изображения отсутствуют.");
    }

    // Обработка файлов
    if (this.lesson.files && this.lesson.files.length > 0) {
        const allFiles = Array.isArray(this.lesson.files)
            ? this.lesson.files
            : this.lesson.files.split(",");
        console.log("Обработанные пути файлов:", allFiles);
        this.files = allFiles.map(file => {
            file = file.replace(/\\/g, "/"); // Заменяем обратные слэши на прямые
            return `${baseUrl}/${file}`;     // Формируем полный URL
        });
    } else {
        console.log("Файлы отсутствуют.");
    }
}

,


    getFileName(file) {
      const lastIndex = file.lastIndexOf('/');
      return file.slice(lastIndex + 1);
    },

    openImage(imageUrl) {
      window.open(imageUrl, '_blank');
    },

    downloadFile(fileUrl) {
      // Имитация скачивания файла
      const link = document.createElement('a');
      link.href = fileUrl;
      link.download = this.getFileName(fileUrl);
      link.click();
    },

    completeHomework() {
      this.$router.push(`/homework/${this.lesson.id}`);
    },
  },
};
</script>

<style scoped>
#materials-page {
  padding: 20px;
}

.container {
  display: flex;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}
.lesson-description {
  margin: 20px 0;
  font-size: 16px;
  line-height: 1.6;
  color: #333;
}
.main-content {
  flex: 1;
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  margin-left: 20px;
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

.lesson-title {
  flex: 1;
  font-size: 24px;
  color: #115544;
  font-weight: 500;
  text-align: center; /* Центрируем заголовок */
  margin: 0;
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
.files-section ul {
  list-style: none; /* Убираем маркеры списка */
  padding: 0;
  margin: 20px 0 0;
}
.files-section ul li {
  display: flex; /* Включаем Flexbox */
  align-items: center; /* Центрируем содержимое по вертикали */
  margin-bottom: 10px;
}

.files-section ul li a {
  display: flex; /* Включаем Flexbox для ссылки */
  align-items: center; /* Центрируем содержимое по вертикали */
  text-decoration: none; /* Убираем подчеркивание ссылки */
  color: inherit; /* Используем цвет по умолчанию */
  font-size: 16px; /* Настраиваем размер текста */
}
ul {
  list-style-type: none;
  padding: 0;
}

ul li {
  margin-bottom: 10px;
}

.file-icon {
  width: 42px;
  height: 42px;
  margin-right: 10px; /* Расстояние между иконкой и текстом */
  flex-shrink: 0; /* Иконка не сжимается */
}
.right-column {
  margin-top: 20px;
  text-align: right;
}

.lesson-button {
  padding: 10px;
  font-size: 16px;
  border: 2px solid #115544;
  border-radius: 20px;
  cursor: pointer;
  text-align: center;
  height: 54px;
  font-weight: 300;
}

.lesson-button.green {
  background-color: #115544;
  color: #fff;
}

.lesson-button:hover {
  opacity: 0.8;
}
</style>
