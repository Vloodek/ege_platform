<template>
    <div id="exam-task-detail">
      <div class="container">
        <SideBar :isTestActive="false" />
  
        <main class="main-content">
          <h2>Детальное задание</h2>
          <!-- Вывод заголовка только если task уже загружен -->
          <div v-if="task" class="subheader">
            Задание №{{ task.id }} (Тип {{ task.task_number }})
          </div>
  
          <div v-if="loading">Загрузка задания...</div>
          <div v-else-if="!task">Задание не найдено.</div>
          <div v-else>
            <!-- Отображение задания без рамки карточки -->
            <div class="task-detail">
              <div class="task-description ql-editor" v-html="task.description"></div>
              <div class="task-images">
                <img
                  v-for="img in task.task_images"
                  :key="img"
                  :src="img"
                  alt="Task image"
                  class="task-image"
                />
              </div>
              <div class="task-files" v-if="task.task_files.length">
                <div v-for="file in task.task_files" :key="file">
                  <a :href="file" target="_blank">📎 {{ getFileName(file) }}</a>
                </div>
              </div>
  
              <button class="solution-toggle" @click="toggleSolution">
                {{ showSolution ? 'Скрыть' : 'Показать' }} решение
              </button>
  
              <div v-if="showSolution" class="solution-section">
                <div class="solution-text" v-html="task.solution_text"></div>
                <div class="solution-images">
                  <img
                    v-for="img in task.solution_images"
                    :key="img"
                    :src="img"
                    alt="Solution image"
                    class="task-image"
                  />
                </div>
                <div class="solution-answer">
                  Ответ: <strong>{{ task.correct_answer }}</strong>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  </template>
  
  
  <script>
  import SideBar from '@/components/SideBar.vue'
  import axios from 'axios'
  import "quill/dist/quill.snow.css"
  
  export default {
    name: "ExamTaskDetail",
    components: { SideBar },
    props: ['id'],
    data() {
      return {
        task: null,
        showSolution: false,
        loading: true
      }
    },
    created() {
      this.loadTask()
    },
    mounted() {
      this.applyImageStyles();
    },
    updated() {
      this.$nextTick(() => {
        this.applyImageStyles();
      });
    },
    methods: {
        async loadTask() {
  try {
    const res = await axios.get(`/exam_tasks/${this.id}`);
    console.log("Ответ API:", res.data);
    const taskFromApi = res.data.task; // Проверьте, что в ответе действительно есть ключ task
    if (!taskFromApi) {
      console.error("Данные о задании отсутствуют!");
      return;
    }
    const base = window.location.origin;

    // Парсинг вложений
    const task_images = taskFromApi.attachments
      .filter(a => a.attachment_type === "task_image")
      .map(a => `${base}/${a.file_path.replace(/\\/g, "/")}`);

    const task_files = taskFromApi.attachments
      .filter(a => a.attachment_type === "task_file")
      .map(a => `${base}/${a.file_path.replace(/\\/g, "/")}`);

    const solution_images = taskFromApi.attachments
      .filter(a => a.attachment_type === "solution_image")
      .map(a => `${base}/${a.file_path.replace(/\\/g, "/")}`);

    this.task = {
      ...taskFromApi,
      task_images,
      task_files,
      solution_images,
    }
  } catch (err) {
    console.error("Ошибка при загрузке задания:", err);
  } finally {
    this.loading = false;
  }
}
,
  
      applyImageStyles() {
        document.querySelectorAll('.task-description img, .solution-section img, .solution-text img').forEach(img => {
          img.style.maxWidth = '70%';
          img.style.width = 'auto';
          img.style.height = 'auto';
          img.style.objectFit = 'contain';
          img.style.display = 'block';
          img.style.margin = '10px auto';
        });
      },
  
      toggleSolution() {
        this.showSolution = !this.showSolution;
        this.$nextTick(() => {
          this.applyImageStyles();
          setTimeout(() => this.applyImageStyles(), 100);
        });
      },
  
      getFileName(path) {
        return path.split("/").pop();
      },
    },
  }
  </script>
  
  <style scoped>
  /* Основной контейнер и стили похожи, как в ExamTaskList.vue */
  #exam-task-detail {
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
  
  .main-content {
    flex: 1;
    background-color: #fff;
    padding: 20px;
    border-radius: 20px;
    margin-left: 20px;
    position: relative;
  }
  
  h2 {
    font-size: 28px;
    text-align: center;
    color: #333;
    margin-bottom: 20px;
  }
  
  .subheader {
    font-size: 20px;
    color: #115544;
    padding-left: 10px;
    margin-bottom: 15px;
    border-left: 3px solid #115544;
  }
  
  /* Стили задания без «карточной» обводки */
  .task-detail {
    margin-top: 20px;
  }
  
  .task-description {
    margin-bottom: 10px;
    line-height: 1.5;
  }
  
  .task-images,
  .solution-images {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 10px;
  }
  
  .task-image {
    max-width: 100%;
    max-height: 200px;
    border-radius: 5px;
    border: 1px solid #ccc;
  }
  
  .task-files {
    margin-bottom: 10px;
  }
  
  .solution-toggle {
    background-color: #115544;
    color: #fff;
    padding: 8px 15px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    margin-top: 10px;
  }
  
  .solution-toggle:hover {
    background-color: #1e9275;
  }
  
  .solution-section {
    margin-top: 10px;
    background-color: #eefaf7;
    padding: 10px;
    border-radius: 8px;
  }
  
  .solution-answer {
    margin-top: 10px;
    font-weight: bold;
  }
  
  /* Если хотите, чтобы ссылки выглядели как обычный текст, задайте нужное оформление */
  .task-link {
    color: inherit;
    text-decoration: none;
    cursor: pointer;
  }
  
  .task-link:hover {
    text-decoration: underline;
  }
  </style>
  