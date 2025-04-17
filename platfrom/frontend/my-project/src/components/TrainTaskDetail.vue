<template>
  <div id="exam-task-detail">
    <div class="container">
      <SideBar :isTestActive="false" />

      <main class="main-content">
        <div class="header-section" v-if="task">
          <div class="header-top">
            <div class="back-arrow" @click="goBack"></div>
            <h2 class="header-title">
              Задание №{{ task.id }} (Тип {{ task.task_number }})
            </h2>
          </div>
        </div>

        <div v-if="loading">Загрузка задания...</div>
        <div v-else-if="!task">Задание не найдено.</div>

        <div v-else>
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

          <BaseButton class="solution-toggle" color="green" @click="toggleSolution">
            {{ showSolution ? 'Скрыть' : 'Показать' }} решение
          </BaseButton>

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
      </main>
    </div>
  </div>
</template>

<script>
import SideBar from "@/components/SideBar.vue";
import BaseButton from "@/components/UI/BaseButton.vue";
import axios from "axios";

export default {
  name: "ExamTaskDetail",
  components: { SideBar, BaseButton },
  props: ["id"],
  data() {
    return {
      task: null,
      loading: true,
      showSolution: false
    };
  },
  async created() {
    await this.loadTask();
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
        const task = res.data;
        const base = window.location.origin;
        console.log("Решение:", task.solution_text);

        this.task = {
  ...task,
  solution_text: task.solution_text, // 🔥 ДОБАВЬ ЭТУ СТРОКУ
  task_images: task.attachments
    .filter(a => a.attachment_type === "task_image")
    .map(a => `${base}/${a.file_path.replace(/\\/g, "/")}`),
  task_files: task.attachments
    .filter(a => a.attachment_type === "task_file")
    .map(a => `${base}/${a.file_path.replace(/\\/g, "/")}`),
  solution_images: task.attachments
    .filter(a => a.attachment_type === "solution_image")
    .map(a => `${base}/${a.file_path.replace(/\\/g, "/")}`),
};

      } catch (err) {
        console.error("Ошибка при загрузке задания:", err);
      } finally {
        this.loading = false;
      }
      
    },
    
    toggleSolution() {
      this.showSolution = !this.showSolution;
      this.$nextTick(() => {
        this.applyImageStyles();
        setTimeout(() => this.applyImageStyles(), 100);
      });
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
    getFileName(path) {
      return path.split("/").pop();
    },
    goBack() {
      this.$router.back();
    }
  }
};

</script>

<style scoped>
/* Оформление аналогично списку */

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
.header-title {
  font-size: 28px;
  color: #333;
  text-align: center;
  width: 100%;
  margin: 0;
  
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

/* Стили для изображений внутри HTML-описания */
.ql-editor img {
  width: 20% !important;
  max-width: 20% !important;
  height: auto !important;
  object-fit: contain !important;
  display: block !important;
  margin: 10px auto !important;
}
</style>
