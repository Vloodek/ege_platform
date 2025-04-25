<template>
    <div class="train-task-detail">
      <h2 class="task-title" v-if="task">Задание №{{ task.id }} (Тип {{ task.task_number }})</h2>
      <div v-if="loading" class="loading">Загрузка задания...</div>
      <div v-else-if="!task" class="not-found">Задание не найдено.</div>
      <div v-else class="task-container">
        <!-- Описание задания -->
        <div class="task-description ql-editor" v-html="task.description"></div>
  
        <!-- Изображения задания -->
        <div class="task-images" v-if="task.task_images && task.task_images.length">
          <img
            v-for="img in task.task_images"
            :key="img"
            :src="img"
            alt="Изображение задания"
            class="task-image"
          />
        </div>
  
        <!-- Файлы задания -->
        <div class="task-files" v-if="task.task_files && task.task_files.length">
          <div v-for="file in task.task_files" :key="file">
            <a :href="file" target="_blank">📎 {{ getFileName(file) }}</a>
          </div>
        </div>
  
        <!-- Поле ввода ответа -->
        <div class="answer-input">
          <label for="userAnswer">Ваш ответ:</label>
          <input
            type="text"
            id="userAnswer"
            v-model="userAnswer"
            placeholder="Введите ваш ответ"
          />
        </div>
  
        <!-- Кнопка отправки ответа -->
        <button class="submit-answer-btn" @click="submitAnswer">
          Отправить ответ
        </button>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: "TrainTaskDetail",
    props: ['id'], // ID задания передаётся из родительского компонента
    data() {
      return {
        task: null,
        loading: true,
        userAnswer: ""
      };
    },
    created() {
      this.loadTask();
    },
    methods: {
      async loadTask() {
        try {
          const res = await this.$axios.get(`/exam_tasks/${this.id}`);
          console.log("Ответ API:", res.data);
          const taskFromApi = res.data;
          if (!taskFromApi) {
            console.error("Данные о задании отсутствуют!");
            return;
          }
          const base = window.location.origin;
  
          // Парсинг вложений для задания
          const task_images = taskFromApi.attachments
            .filter(a => a.attachment_type === "task_image")
            .map(a => `${base}/${a.file_path.replace(/\\/g, "/")}`);
          const task_files = taskFromApi.attachments
            .filter(a => a.attachment_type === "task_file")
            .map(a => `${base}/${a.file_path.replace(/\\/g, "/")}`);
  
          // Формируем объект задания без данных решения
          this.task = {
            ...taskFromApi,
            task_images,
            task_files,
          };
        } catch (err) {
          console.error("Ошибка при загрузке задания:", err);
        } finally {
          this.loading = false;
        }
      },
      getFileName(path) {
        return path.split("/").pop();
      },
      async submitAnswer() {
        console.log("Отправка ответа:", this.userAnswer);
        try {
          const formData = new URLSearchParams({
            session_id: this.$route.query.session_id || "",
            task_id: this.id,
            answer: this.userAnswer
          });
          const res = await this.$axios.post("/testing/submit_answer", formData, {
            headers: {
              "Content-Type": "application/x-www-form-urlencoded"
            }
          });
          console.log("Ответ отправлен:", res.data);
          alert("Ваш ответ сохранён");
        } catch (error) {
          console.error("Ошибка отправки ответа:", error);
          alert("Ошибка отправки ответа");
        }
      }
    }
  };
  </script>
  
  <style scoped>
  .train-task-detail {
    padding: 20px;
  }
  
  .task-title {
    font-size: 24px;
    color: #56AEF6;
    margin-bottom: 15px;
    text-align: center;
  }
  
  .loading,
  .not-found {
    text-align: center;
    font-size: 18px;
    color: #888;
  }
  
  .task-container {
    background-color: #fff;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  }
  
  .task-description {
    margin-bottom: 10px;
    line-height: 1.5;
  }
  
  .task-images {
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
  
  .answer-input {
    margin-top: 20px;
  }
  
  .answer-input label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
  }
  
  .answer-input input[type="text"] {
    width: 100%;
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 5px;
  }
  
  .submit-answer-btn {
    background-color: #56AEF6;
    color: #fff;
    padding: 10px 20px;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    margin-top: 15px;
  }
  
  .submit-answer-btn:hover {
    background-color: #1e9275;
  }
  </style>
  