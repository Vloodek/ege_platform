<template>
  <div id="exam-task-list">
    <div class="container">
      <SideBar :isTestActive="false" />

      <main class="main-content">
        <!-- Header Section -->
        <div class="header-section">
          <div class="header-top">
            <div class="back-arrow" @click="goBack"></div>
            <h2 class="main-title">Тренажер</h2>
          </div>
          <!-- Информация о типе заданий под заголовком, выровненная по левому краю -->
          <div class="task-type">
            Тип {{ taskName }} ({{ taskId }})
          </div>
        </div>

        <!-- Отображение карточек заданий -->
        <div v-if="tasks.length === 0">Нет заданий для этого типа.</div>

        <div v-for="(task, index) in tasks" :key="task.id" class="task-card">
          <div class="task-header">
            <router-link :to="{ name: 'TrainTaskDetail', params: { id: task.id } }" class="task-link">
              {{ index + 1 }}. Задание №{{ task.id }}
            </router-link>
            <span v-if="!noPoints(task.task_number)">
              — {{ getPoints(task.task_number) }} балла
            </span>
            <!-- Кнопка удаления -->
            <button class="delete-task-btn" @click="confirmDelete(task.id)">&times;</button>
          </div>

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
              <a :href="file" target="_blank">{{ getFileName(file) }}</a>
            </div>
          </div>

          <!-- Кнопка показа/скрытия решения с использованием переиспользуемого компонента -->
          <BaseButton class="solution-toggle" color="green" @click="toggleSolution(task.id)">
            {{ showSolution[task.id] ? 'Скрыть' : 'Показать' }} решение
          </BaseButton>

          <div v-if="showSolution[task.id]" class="solution-section">
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
      </main>
    </div>

    <!-- Модальное окно подтверждения удаления -->
    <div v-if="showDeleteModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Подтверждение удаления</h3>
        <p>Вы точно хотите удалить задание №{{ taskToDelete }}?</p>
        <div class="modal-buttons">
          <button class="modal-btn confirm" @click="deleteTask">Удалить</button>
          <button class="modal-btn cancel" @click="cancelDelete">Отмена</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SideBar from "@/components/SideBar.vue";
import BaseButton from "@/components/UI/BaseButton.vue";
import axios from "axios";

export default {
  name: "ExamTaskList",
  components: { 
    SideBar,
    BaseButton
  },
  data() {
    return {
      taskId: this.$route.params.id,
      taskName: this.$route.params.name,
      tasks: [],
      showSolution: {},
      showDeleteModal: false,
      taskToDelete: null
    };
  },
  async created() {
    await this.loadTasks();
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
    async loadTasks() {
      try {
        const res = await axios.get(`/exam_tasks/by_type/${this.taskId}`);
        const rawTasks = res.data.tasks;
        const base = window.location.origin;
        this.tasks = rawTasks.map(task => {
          const task_images = task.attachments
            .filter(a => a.attachment_type === "task_image")
            .map(a => `${base}/${a.file_path.replace(/\\/g, "/")}`);
          const task_files = task.attachments
            .filter(a => a.attachment_type === "task_file")
            .map(a => `${base}/${a.file_path.replace(/\\/g, "/")}`);
          const solution_images = task.attachments
            .filter(a => a.attachment_type === "solution_image")
            .map(a => `${base}/${a.file_path.replace(/\\/g, "/")}`);
    
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
    applyImageStyles() {
      document.querySelectorAll('.task-description img, .solution-section img, .solution-text img')
        .forEach(img => {
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
    confirmDelete(taskId) {
      this.taskToDelete = taskId;
      this.showDeleteModal = true;
    },
    async deleteTask() {
      try {
        await axios.delete(`/exam_tasks/${this.taskToDelete}`);
        this.tasks = this.tasks.filter(task => task.id !== this.taskToDelete);
        this.cancelDelete();
      } catch (error) {
        console.error("Ошибка при удалении задания:", error);
        alert("Ошибка при удалении задания");
      }
    },
    cancelDelete() {
      this.taskToDelete = null;
      this.showDeleteModal = false;
    },
    goBack() {
      this.$router.back();
    }
  }
};
</script>

<style scoped>
/* Основная верстка */
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

/* Header Section */
.header-section {
  margin-bottom: 20px;
}
.header-top {
  display: flex;
  align-items: center;
  position: relative;
}
.back-arrow {
  width: 20px;
  height: 20px;
  background-color: #115544;
  clip-path: polygon(100% 0, 0 50%, 100% 100%);
  cursor: pointer;
  position: absolute;
  left: 0;
}
.main-title {
  font-size: 28px;
  color: #333;
  text-align: center;
  width: 100%;
  margin: 0;
}
.task-type {
  margin-top: 5px;
  font-size: 20px;
  color: #115544;
  padding-left: 30px;
  border-left: 3px solid #115544;
  display: inline-block;
}

/* Карточки заданий */
.task-card {
  border: 2px solid #115544;
  border-radius: 10px;
  padding: 15px;
  margin-bottom: 20px;
  /* Изменён фон карточек на белый */
  background: #fff;
  position: relative;
}
.task-header {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 10px;
  color: #222;
  position: relative;
  
}
.task-link {
  color: inherit;
  text-decoration: none;
  text-decoration:underline #115544;
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
.delete-task-btn {
  position: absolute;
  top: 5px;
  right: 5px;
  background: transparent;
  border: none;
  font-size: 24px;
  color: #dc3545;
  cursor: pointer;
}
.delete-task-btn:hover {
  color: #a71d2a;
}
.solution-toggle {
  margin-top: 10px;
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

/* Модальное окно */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-content {
  background: #e0f7e9;
  padding: 20px;
  border-radius: 10px;
  width: 300px;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}
.modal-buttons {
  margin-top: 20px;
  display: flex;
  justify-content: space-around;
}
.modal-btn {
  padding: 8px 12px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
}
.modal-btn.confirm {
  background-color: #28a745;
  color: #fff;
}
.modal-btn.cancel {
  background-color: #dc3545;
  color: #fff;
}

/* Стили для изображений, вставляемых через Quill */
.ql-editor img {
  width: 20% !important;
  max-width: 20% !important;
  height: auto !important;
  object-fit: contain !important;
  display: block !important;
  margin: 10px auto !important;
}
</style>
