<template>
  <div id="exam-task-list">
    <div class="container">
      <SideBar :isTestActive="false" />

      <main class="main-content">
        <h2>Тренажер</h2>
        <div class="subheader">{{ taskName }} (Тип {{ taskId }})</div>

        <div v-if="tasks.length === 0">Нет заданий для этого типа.</div>

        <div v-for="(task, index) in tasks" :key="task.id" class="task-card">
          <div class="task-header">
            <strong>{{ index + 1 }}. Задание №{{ task.id }}</strong>
            <span v-if="!noPoints(task.task_number)">
              — {{ getPoints(task.task_number) }} балла
            </span>
          </div>

          <div class="task-description ql-editor" v-html="task.description" />

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

          <button class="solution-toggle" @click="toggleSolution(task.id)">
            {{ showSolution[task.id] ? 'Скрыть' : 'Показать' }} решение
          </button>

          <div v-if="showSolution[task.id]" class="solution-section">
            <div class="solution-text" v-html="task.solution_text" />
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
      </main>
    </div>
  </div>
</template>


<script>
import SideBar from "@/components/SideBar.vue";
import axios from "axios";
import "quill/dist/quill.snow.css";

export default {
  name: "ExamTaskList",
  components: { SideBar },
  data() {
    return {
      taskId: this.$route.params.id,
      taskName: this.$route.params.name,
      tasks: [],
      showSolution: {},
    };
  },
  async created() {
    await this.loadTasks();
  },
  mounted() {
    this.applyImageStyles(); // Применяем стили сразу после монтирования
  },
  updated() {
    this.$nextTick(() => {
      this.applyImageStyles(); // Применяем стили после обновления DOM
    });
  },
  methods: {
  async loadTasks() {
    try {
      const res = await axios.get(`/exam_tasks/by_type/${this.taskId}`);
      const rawTasks = res.data.tasks;

      // Парсим вложения
      this.tasks = rawTasks.map((task) => {
        const base = window.location.origin;

        const task_images = task.attachments
          .filter((a) => a.attachment_type === "task_image")
          .map((a) => `${base}/${a.file_path.replace(/\\/g, "/")}`);

        const task_files = task.attachments
          .filter((a) => a.attachment_type === "task_file")
          .map((a) => `${base}/${a.file_path.replace(/\\/g, "/")}`);

        const solution_images = task.attachments
          .filter((a) => a.attachment_type === "solution_image")
          .map((a) => `${base}/${a.file_path.replace(/\\/g, "/")}`);

        return {
          ...task,
          task_images,
          task_files,
          solution_images,
        };
      });
    } catch (err) {
      console.error("Ошибка при загрузке заданий:", err);
    }
  },

  // Добавляем стили для изображений внутри .task-description и .solution-images
  applyImageStyles() {
  // Для основного контента заданий
  document.querySelectorAll('.task-description img, .solution-section img, .solution-text img').forEach(img => {
    img.style.maxWidth = '70%';
    img.style.width = 'auto';
    img.style.height = 'auto';
    img.style.objectFit = 'contain';
    img.style.display = 'block';
    img.style.margin = '10px auto';
  });
},

toggleSolution(id) {
  this.showSolution[id] = !this.showSolution[id];
  this.$nextTick(() => {
    this.applyImageStyles();
    // Принудительно обновляем стили для вновь отображенных изображений
    setTimeout(() => this.applyImageStyles(), 100);
  });
},

  getPoints(taskNumber) {
    if ([26, 27].includes(taskNumber)) return null;
    if ([19, 20, 21].includes(taskNumber)) return 2;
    if ([16].includes(taskNumber)) return 3;
    return 1;
  },

  noPoints(taskNumber) {
    return [26, 27].includes(taskNumber);
  },

  getFileName(path) {
    return path.split("/").pop();
  },
}
};
</script>


<style scoped>
#exam-task-list {
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

/* Карточка задания */
.task-card {
  border: 2px solid #115544;
  border-radius: 10px;
  padding: 15px;
  margin-bottom: 20px;
  background: #f9f9f9;
}

.task-header {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 10px;
  color: #222;
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



/* Уменьшаем изображения внутри Quill */
.ql-editor img {
  width: 20% !important;         /* Устанавливаем максимальную ширину */
  max-width: 20% !important;      /* Устанавливаем максимальную ширину на 80% */
  height: auto !important;        /* Сохраняем пропорции */
  object-fit: contain !important; /* Изображение вмещается в блок */
  display: block !important;      /* Делаем картинку блочным элементом */
  margin: 10px auto !important;   /* Центрируем картинку */
  box-sizing: border-box !important; /* Учитываем padding */
  overflow: hidden !important;    /* Обрезаем лишнюю часть */
}

/* Для картинок в .task-description */
.task-description img {
  width: 20% !important;
  max-width: 20% !important;      /* Уменьшаем максимальную ширину на 80% */
  height: auto !important;
  object-fit: contain !important;
  display: block !important;
  margin: 10px auto !important;
  box-sizing: border-box !important;
}

::v-deep(.solution-section) img {
  max-width: 100% !important;
  width: auto !important;
  height: auto !important;
  object-fit: contain !important;
  display: block !important;
  margin: 10px auto !important;
}

::v-deep(.solution-text) img {
  max-width: 100% !important;
  width: auto !important;
  height: auto !important;
}


</style>
