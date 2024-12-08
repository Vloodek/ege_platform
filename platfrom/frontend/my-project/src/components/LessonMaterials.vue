<template>
  <div id="materials-page">
    <div class="container">
      <!-- Боковое меню -->
      <SideBar :isTestActive="false" />

      <!-- Основной контент с деталями занятия -->
      <main class="main-content">
        <div v-if="lesson">
          <h1>{{ lesson.name }}</h1>
          <p><strong>Текст занятия:</strong></p>
          <p>{{ lesson.text }}</p> <!-- Здесь отображается текст занятия -->

          <!-- Отображение изображений -->
          <div v-if="images.length" class="images-container">
            <h3>Изображения:</h3>
            <div class="images">
              <img v-for="image in images" :src="image" :alt="lesson.name" :key="image" />
            </div>
          </div>

          <!-- Список файлов -->
          <div v-if="files.length">
            <h3>Файлы:</h3>
            <ul>
              <li v-for="file in files" :key="file">
                <a :href="file" target="_blank">{{ file }}</a>
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
      lesson: null, // Данные занятия
      images: [], // Для хранения ссылок на изображения
      files: [], // Для хранения файлов
    };
  },
  created() {
    this.fetchLesson();
  },
  methods: {
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
          this.processMaterials();
        } else {
          console.error("Ошибка загрузки материалов");
        }
      } catch (error) {
        console.error("Ошибка сети:", error);
      }
    },

    // Обработка материалов
    processMaterials() {
      if (this.lesson.files) {
        const baseUrl = "http://localhost:8000";
        const allFiles = Array.isArray(this.lesson.files)
          ? this.lesson.files
          : this.lesson.files.split(",");

        this.images = allFiles
          .filter((file) => /\.(jpg|jpeg|png|gif)$/i.test(file))
          .map(file => file.startsWith(baseUrl) 
            ? file 
            : `${baseUrl}/${file.replace(/\\/g, "/")}`); // Убираем дублирование и заменяем \ на /

        this.files = allFiles
          .filter((file) => !/\.(jpg|jpeg|png|gif)$/i.test(file))
          .map(file => file.startsWith(baseUrl) 
            ? file 
            : `${baseUrl}/${file.replace(/\\/g, "/")}`);
      }
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

.main-content {
  flex: 1;
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  margin-left: 20px;
  overflow: hidden; /* Ограничивает переполнение контента */
}

.main-content p {
  word-wrap: break-word; /* Перенос длинных слов */
  overflow-wrap: break-word; /* Перенос текста */
  white-space: normal; /* Разрешает перенос строк */
  word-break: break-all; /* Принудительный перенос длинных слов на новую строку */
  max-width: 100%; /* Убедитесь, что блок не превышает ширину родителя */
}


.images-container {
  display: flex;
  flex-direction: column;
  align-items: center; /* Центрирование по горизонтали */
  justify-content: center; /* Центрирование по вертикали, если нужно */
  margin-top: 20px; /* Отступ сверху */
}

.images {
  display: flex;
  flex-wrap: wrap;
  gap: 20px; /* Расстояние между изображениями */
  justify-content: center; /* Центрирует изображения в строке */
}

.images img {
  max-width: 90%; /* Изображение занимает до 90% ширины контейнера */
  max-height: 500px; /* Ограничение по высоте */
  border-radius: 8px; /* Скругление углов */
  object-fit: cover; /* Сохраняет пропорции изображения */
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2); /* Добавляет тень для красоты */
  transition: transform 0.3s ease; /* Анимация при наведении */
}

.images img:hover {
  transform: scale(1.05); /* Увеличение изображения при наведении */
}


ul {
  list-style-type: none;
  padding: 0;
}

ul li {
  margin-bottom: 10px;
}

ul li a {
  text-decoration: none;
  color: #007bff;
}

ul li a:hover {
  text-decoration: underline;
}
</style>
