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
          <div class="task-type">
            Тип {{ taskName }} ({{ taskId }})
          </div>
        </div>

        <div v-if="tasks.length === 0">Нет заданий для этого типа.</div>

        <div
          v-for="(task, index) in tasks"
          :key="task.id"
          class="task-card"
        >
          <div class="task-header">
            <router-link
              :to="{ name: 'TrainTaskDetail', params: { id: task.id } }"
              class="task-link"
            >
              {{ index + 1 }}. Задание №{{ task.id }}
            </router-link>
            <span v-if="!noPoints(task.task_number)">
              — {{ getPoints(task.task_number) }} балла
            </span>
            <!-- крестик удаления только для учителя -->
            <button
              v-if="isTeacher"
              class="delete-task-btn"
              @click="confirmDelete(task.id)"
            >&times;</button>
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
          <div
            class="task-files"
            v-if="task.task_files && task.task_files.length"
          >
            <div v-for="file in task.task_files" :key="file">
              <a :href="file" target="_blank">{{ getFileName(file) }}</a>
            </div>
          </div>

          <BaseButton
            class="solution-toggle"
            color="green"
            @click="toggleSolution(task.id)"
          >
            {{ showSolution[task.id] ? 'Скрыть' : 'Показать' }} решение
          </BaseButton>

          <div
            v-if="showSolution[task.id]"
            class="solution-section"
          >
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
            <div
              class="solution-files"
              v-if="task.solution_files && task.solution_files.length"
            >
              <div v-for="file in task.solution_files" :key="file">
                <a :href="file" target="_blank">{{ getFileName(file) }}</a>
              </div>
            </div>
            <div class="solution-answer">
              Ответ: <strong>{{ task.correct_answer }}</strong>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- Модальное окно подтверждения удаления — только для учителя -->
    <div
      v-if="showDeleteModal && isTeacher"
      class="modal-overlay"
    >
      <div class="modal-content">
        <h3>Подтверждение удаления</h3>
        <p>Вы точно хотите удалить задание №{{ taskToDelete }}?</p>
        <div class="modal-buttons">
          <button
            class="modal-btn confirm"
            @click="deleteTask"
          >Удалить</button>
          <button
            class="modal-btn cancel"
            @click="cancelDelete"
          >Отмена</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SideBar from "@/components/SideBar.vue";
import BaseButton from "@/components/UI/BaseButton.vue";

export default {
  name: "ExamTaskList",
  components: { SideBar, BaseButton },
  data() {
    return {
      taskId: this.$route.params.id,
      taskName: this.$route.params.name,
      tasks: [],
      showSolution: {},
      showDeleteModal: false,
      taskToDelete: null,
    };
  },
  computed: {
    isTeacher() {
      try {
        const user = JSON.parse(localStorage.getItem("user"));
        return user?.role === "teacher";
      } catch {
        return false;
      }
    },
  },
  async created() {
    await this.loadTasks();
  },
  mounted() {
    this.applyImageStyles();
  },
  updated() {
    this.$nextTick(this.applyImageStyles);
  },
  methods: {
    async loadTasks() {
      try {
        const res = await this.$axios.get(`/exam_tasks/by_type/${this.taskId}`);

        const base = window.location.origin;
        this.tasks = res.data.tasks.map(task => {
          const attachments = task.attachments || [];
          return {
            ...task,
            task_images: attachments
              .filter(a => a.attachment_type === "task_image")
              .map(a => `${base}/${a.file_path.replace(/\\/g, "/")}`),
            task_files: attachments
              .filter(a => a.attachment_type === "task_file")
              .map(a => `${base}/${a.file_path.replace(/\\/g, "/")}`),
            solution_images: attachments
              .filter(a => a.attachment_type === "solution_image")
              .map(a => `${base}/${a.file_path.replace(/\\/g, "/")}`),
            solution_files: attachments
              .filter(a => a.attachment_type === "solution_file")
              .map(a => `${base}/${a.file_path.replace(/\\/g, "/")}`),
          };
        });
      } catch (err) {
        console.error("Ошибка при загрузке заданий:", err);
      }
    },
    applyImageStyles() {
      document
        .querySelectorAll(
          ".task-description img, .solution-section img, .solution-text img"
        )
        .forEach(img => {
          Object.assign(img.style, {
            maxWidth: "70%",
            width: "auto",
            height: "auto",
            objectFit: "contain",
            display: "block",
            margin: "10px auto",
          });
        });
    },
    toggleSolution(id) {
  this.showSolution = {
    ...this.showSolution,
    [id]: !this.showSolution[id]
  };
  this.$nextTick(() => {
    this.applyImageStyles();
    setTimeout(this.applyImageStyles, 100);
  });
},

    getPoints(n) {
      if ([26, 27].includes(n)) return null;
      if ([19, 20, 21].includes(n)) return 2;
      if (n === 16) return 3;
      return 1;
    },
    noPoints(n) {
      return [26, 27].includes(n);
    },
    getFileName(path) {
      return path.split("/").pop();
    },
    confirmDelete(id) {
      this.taskToDelete = id;
      this.showDeleteModal = true;
    },
    async deleteTask() {
      try {
        await this.$axios.delete(`/exam_tasks/${this.taskToDelete}`);

        this.tasks = this.tasks.filter(t => t.id !== this.taskToDelete);
        this.cancelDelete();
      } catch (err) {
        console.error("Ошибка при удалении задания:", err);
        alert("Не удалось удалить задание");
      }
    },
    cancelDelete() {
      this.taskToDelete = null;
      this.showDeleteModal = false;
    },
    goBack() {
      this.$router.back();
    },
  },
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
  /* Ограничиваем максимальную ширину, чтобы не расползался при длинном содержимом */
  max-width: 100%;
  box-sizing: border-box;
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
  background: #fff;
  position: relative;
  box-sizing: border-box;
  /* Чтобы блок не расползался, ограничиваем его ширину */
  max-width: 100%;
  overflow-wrap: break-word;
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
  text-decoration: underline #115544;
}
.task-description {
  margin-bottom: 10px;
  line-height: 1.5;
  word-break: break-word;
}

/* Изображения */
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

/* Файлы */
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

/* Кнопка показа/скрытия решения */
.solution-toggle {
  margin-top: 10px;
}

/* Блок решения */
.solution-section {
  margin-top: 10px;
  background-color: #eefaf7;
  padding: 10px;
  border-radius: 8px;
  /* Ограничиваем максимальную ширину блока решения */
  max-width: 100%;
  box-sizing: border-box;
  /* Перенос слов и перенос строк */
  overflow-wrap: break-word;
  word-break: break-word;
}
.solution-text {
  white-space: normal;
  word-break: break-word;
}

/* Ответ решения */
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
