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

          <!-- Отображение отформатированного текста занятия (Quill) -->
          <div
            v-if="lesson.text"
            class="lesson-description ql-editor"
            v-html="lesson.text"
          ></div>

          <!-- Список файлов -->
          <div v-if="files.length" class="files-section">
            <ul>
              <li v-for="file in files" :key="file">
                <a :href="file" download @click.prevent="downloadFile(file)">
                  <img
                    src="@/assets/svg/files.svg"
                    alt="file icon"
                    class="file-icon"
                  />
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
  components: { SideBar },
  data() {
    return {
      lesson: null,
      files: [],
    };
  },
  created() {
    this.fetchLesson();
  },
  updated() {
    // Подправляем стили img внутри Quill-контента
    this.$nextTick(this.applyImageStyles);
  },
  methods: {
    goBack() {
      this.$router.go(-1);
    },
    async fetchLesson() {
      const lessonId = this.$route.params.id;
      try {
        const { data } = await this.$axios.get(`/lessons/${lessonId}`);
        this.lesson = data;
        this.processMaterials();
      } catch (error) {
        console.error("Ошибка загрузки материалов", error);
      }
    },
    processMaterials() {
      const baseUrl = this.$axios.defaults.baseURL.replace(/\/$/, "");

      // Обработка файлов
      if (this.lesson.files && this.lesson.files.length > 0) {
        const allFiles = Array.isArray(this.lesson.files)
          ? this.lesson.files
          : this.lesson.files.split(",");
        this.files = allFiles.map((file) => {
          file = file.replace(/\\/g, "/");
          return `${baseUrl}/${file}`;
        });
      } else {
        this.files = [];
      }
    },
    getFileName(file) {
      return file.substring(file.lastIndexOf("/") + 1);
    },
    downloadFile(fileUrl) {
      const link = document.createElement("a");
      link.href = fileUrl;
      link.download = this.getFileName(fileUrl);
      link.click();
    },
    applyImageStyles() {
  document.querySelectorAll(".ql-editor img").forEach((img) => {
    // Стили
    img.style.maxWidth = "300px";
    img.style.width = "auto";
    img.style.height = "auto";
    img.style.objectFit = "contain";
    img.style.display = "block";
    img.style.margin = "10px auto";

    // Обернуть в ссылку, если ещё не обёрнуто
    if (!img.parentElement || img.parentElement.tagName.toLowerCase() !== "a") {
      const link = document.createElement("a");
      link.href = img.src;
      link.target = "_blank";
      link.rel = "noopener noreferrer";

      img.parentNode.insertBefore(link, img);
      link.appendChild(img);
    }
  });
}
,
  },
};
</script>

<style scoped>
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

.lesson-title {
  flex: 1;
  font-size: 24px;
  color: #115544;
  font-weight: 500;
  text-align: center;
  margin: 0;
}

.lesson-description {
  margin: 20px 0;
  font-size: 16px;
  line-height: 1.6;
  color: #333;
}

/* Стили для файлов */
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

/* Стили Quill для изображений внутри текста */
.ql-editor img {
  max-width: 300px !important;
  width: auto !important;
  height: auto !important;
  object-fit: contain !important;
  display: block !important;
  margin: 10px auto !important;
}
</style>
