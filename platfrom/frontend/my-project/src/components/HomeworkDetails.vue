<template>
  <div id="homework-details">
    <div class="container">
      <!-- Боковое меню -->
      <SideBar :isTestActive="false" />
  
      <!-- Основной контент с деталями домашнего задания -->
      <main class="main-content">
        <h2>Детали домашнего задания</h2>
  
        <div v-if="homework">
          <!-- Дедлайн -->
          <div class="homework-deadline">
            <strong>Дедлайн: </strong>{{ homework.deadline }}
          </div>
  
          <!-- Описание задания -->
          <div v-if="homework.description" class="homework-description">
            <strong>Описание:</strong>
            <p>{{ homework.description }}</p>
          </div>
  
          <!-- Отображение изображений -->
          <div v-if="homeworkImages.length > 0" class="homework-photos">
            <strong>Фотографии:</strong>
            <div class="photo-slider">
              <button @click="prevImage" :disabled="currentIndex === 0">←</button>
              <img :src="getFileUrl(homeworkImages[currentIndex])" alt="Homework Photo" class="homework-photo" />
              <button @click="nextImage" :disabled="currentIndex === homeworkImages.length - 1">→</button>
            </div>
          </div>
  
          <!-- Прикрепленные файлы -->
          <div v-if="otherFiles.length > 0" class="homework-files">
            <strong>Прикрепленные файлы:</strong>
            <ul>
              <li v-for="(file, index) in otherFiles" :key="index">
                <a :href="getFileUrl(file)" target="_blank">{{ file.split('/').pop() }}</a>
              </li>
            </ul>
          </div>
        </div>
  
        <div v-else>
          <p>Задание не найдено.</p>
        </div>
      </main>
    </div>
  </div>
</template>

  
<script>
import SideBar from "../components/SideBar.vue"; // Импортируем Sidebar

export default {
  components: {
    SideBar, // Регистрируем Sidebar как компонент
  },
  data() {
    return {
      homework: null, // Данные домашнего задания
      currentIndex: 0, // Текущий индекс изображения в слайдере
    };
  },
  computed: {
    // Получаем только изображения для слайдера
    homeworkImages() {
      return this.homework?.files.filter(file =>
        /\.(jpg|jpeg|png|gif)$/i.test(file)
      ) || [];
    },
    // Получаем все другие файлы (не изображения)
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
    // Метод для получения деталей домашнего задания
    async fetchHomeworkDetails() {
      const homeworkId = this.$route.params.id; // Получаем id задания из параметров маршрута
      console.log(homeworkId);
      try {
        const response = await fetch(`http://localhost:8000/homeworks/${homeworkId}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
        });
        if (response.ok) {
          const data = await response.json();
          this.homework = data[0]; // Полагаем, что возвращается массив, и берем первый элемент
          console.log("Детали домашнего задания:", this.homework);
        } else {
          console.error("Ошибка загрузки домашнего задания");
        }
      } catch (error) {
        console.error("Ошибка сети:", error);
      }
    },

    // Метод для получения правильного URL файла
    getFileUrl(file) {
      return `http://localhost:8000/${file.replace(/\\/g, '/')}`;
    },

    // Переключение на следующее изображение
    nextImage() {
      if (this.currentIndex < this.homeworkImages.length - 1) {
        this.currentIndex++;
      }
    },

    // Переключение на предыдущее изображение
    prevImage() {
      if (this.currentIndex > 0) {
        this.currentIndex--;
      }
    },
  },
};
</script>

  
<style scoped>
/* Стили для контейнера деталей домашки */
#homework-details {
  display: flex;
  min-height: 100vh;
  background-color: #f5f5f5;
}

/* Основной контейнер для контента */
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
  border-radius: 20px;
  margin-left: 20px;
}

/* Заголовок */
h2 {
  font-size: 24px;
  margin-bottom: 20px;
  color: #333;
  text-align: center;
}

/* Контейнер для данных домашки */
.homework-details-container {
  margin-bottom: 30px;
}

/* Описание задания */
.homework-description {
  margin-bottom: 20px;
  font-size: 16px;
  color: #333;
}

/* Стили для слайдера */
.photo-slider {
  display: flex;
  justify-content: center;
  align-items: center;
}

.homework-photo {
  max-width: 700px; /* Ограничиваем размер изображения */
  max-height: 600px;
  object-fit: cover;
  margin: 0 10px;
}

button {
  background-color: #115544;
  color: white;
  border: none;
  padding: 10px;
  font-size: 16px;
  cursor: pointer;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.homework-files a {
  color: #115544;
  text-decoration: none;
}

.homework-files a:hover {
  text-decoration: underline;
}

/* Дедлайн */
.homework-deadline {
  margin-bottom: 20px;
  font-size: 16px;
  font-weight: bold;
  color: #333;
}
</style>

  