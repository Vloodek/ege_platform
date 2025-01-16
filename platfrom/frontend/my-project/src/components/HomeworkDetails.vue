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
            <h1 class="homework-title centered">Детали домашнего задания</h1>
          </div>

          <!-- Дедлайн -->
          <div class="homework-deadline">
            <strong>Дедлайн: </strong>{{ formatDate(homework.date) }}
          </div>

          <!-- Описание задания -->
          <div v-if="homework.description" class="homework-description">
            <p>{{ homework.description }}</p>
          </div>

          <!-- Отображение изображений -->
          <div v-if="homeworkImages.length" class="images-container">
            <div class="images">
              <img 
                v-for="(image, index) in homeworkImages" 
                :key="index" 
                :src="getFileUrl(image)" 
                alt="Homework Image" 
                @click="window.open(getFileUrl(image), '_blank')"
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
        </div>

        <div v-else>
          <p>Загрузка задания...</p>
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
    formatDate(dateString) {
  try {
    // Заменяем избыточные точки после секунд
    const cleanedDateString = dateString.split('.')[0]; 
    const date = new Date(cleanedDateString);

    // Проверяем, что дата корректная
    if (isNaN(date.getTime())) {
      console.error("Некорректная дата:", dateString);
      return "Неверный формат даты";
    }

    // Форматируем дату и время
    const options = {
      day: "2-digit",
      month: "long",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    };

    return date.toLocaleDateString("ru-RU", options);
  } catch (error) {
    console.error("Ошибка форматирования даты:", error);
    return "Ошибка даты";
  }
}


  },
};
</script>

  
<style scoped>
#homework-details {
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

.homework-deadline,
.homework-description {
  margin: 20px 0;
  font-size: 16px;
  line-height: 1.6;
  color: #333;
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


  