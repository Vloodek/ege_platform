<template>
  <div id="test-session">
    <div class="container">
      <!-- Сайдбар в режиме тестирования:
           Передаём туда список заданий, индекс текущего задания, объект ответов, оставшееся время и общее количество -->
      <SideBar 
        :isTestActive="true" 
        :taskIds="taskIds"
        :currentTaskIndex="currentTaskIndex"
        :answers="answers"
        @selectTask="goToTask"
        @prevTask="prevTask"
        @nextTask="nextTask"
        @exitTest="finishTest"
        :timerDisplay="remainingTime" 
        :totalQuestions="taskIds.length" 
      />
      
      <main class="main-content">
        <!-- Встроенный блок отображения задания (бывший TrainTaskDetail) -->
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
      </main>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import SideBar from "../SideBar.vue";

export default {
  name: "TestSession",
  components: { SideBar },
  data() {
    return {
      sessionId: null,
      taskIds: [],        // Массив ID заданий (например, 27 штук)
      answers: {},        // Объект с ответами: ключ – номер задания, значение – ответ пользователя
      currentTaskIndex: 0,
      remainingTime: 0,
      timerSource: null,
      // Состояние отображения задания (интегрированное из TrainTaskDetail)
      task: null,
      loading: true,
      userAnswer: ""
    };
  },
  computed: {
  testType() {
    return this.$route.query.test_type || "regular";
  },
  currentTaskId() {
    return this.taskIds[this.currentTaskIndex];
  }
},

watch: {
  currentTaskId: {
    handler(newVal) {
      if (newVal) {
        this.loadTask();
        this.userAnswer = "";
      }
    },
    immediate: true
  }
},

  async created() {
  const savedSessionId = localStorage.getItem("testSessionId");
  if (savedSessionId) {
    try {
      const res = await axios.get(`http://localhost:8000/testing/session/${savedSessionId}`);
      const session = res.data;
      const now = new Date();
      const expires = new Date(session.expires_at);

      if (!session.is_completed && expires > now) {
        // Если сессия активна — восстанавливаем её
        this.sessionId = session.session_id;
        this.taskIds = session.task_ids;
        this.answers = session.answers || {};
        this.startTimer();
        this.loadTask(); // 👈 нужно добавить

        return;
      } else {
        // Сессия истекла или завершена — удаляем и запускаем новую
        localStorage.removeItem("testSessionId");
      }
    } catch (err) {
      console.error("Ошибка восстановления сессии:", err);
      localStorage.removeItem("testSessionId");
    }
  }

  // Если нет сессии или она неактивна — запускаем новую
  const userData = JSON.parse(localStorage.getItem("user")) || {};
  const userId = userData.userId || 1;

  try {
    const formData = new FormData();
    formData.append("user_id", userId);
    formData.append("test_type", this.testType);

    const res = await axios.post("http://localhost:8000/testing/start", formData);

    this.sessionId = res.data.session_id;
    this.taskIds = res.data.task_ids;
    localStorage.setItem("testSessionId", this.sessionId); // ← сохраняем новую сессию
    this.startTimer();
  } catch (error) {
    console.error("Ошибка запуска тестовой сессии:", error);
    alert("Не удалось запустить тестовую сессию.");
  }
}

,
  methods: {
    startTimer() {
      const eventSource = new EventSource(`http://localhost:8000/sse/timer?session_id=${this.sessionId}`);

  eventSource.onmessage = (event) => {
    if (event.data === "Test finished") {
      this.remainingTime = 0;
      eventSource.close();
      // Автоматически завершить тест, не показывая модальные окна:
      this.finishTest();
    } else {
      this.remainingTime = parseInt(event.data);
    }
  };
  this.timerSource = eventSource;
},
    goToTask(index) {
      this.currentTaskIndex = index;
    },
    prevTask() {
      if (this.currentTaskIndex > 0) {
        this.currentTaskIndex--;
      }
    },
    nextTask() {
      if (this.currentTaskIndex < this.taskIds.length - 1) {
        this.currentTaskIndex++;
      }
    },
    async loadTask() {
      this.loading = true;
      try {
        const res = await axios.get(`/exam_tasks/${this.currentTaskId}`);
        const taskFromApi = res.data;
        if (!taskFromApi) {
          console.error("Данные о задании отсутствуют!");
          this.task = null;
          return;
        }
        const base = window.location.origin;
        // Парсинг изображений и файлов
        const task_images = taskFromApi.attachments
          .filter(a => a.attachment_type === "task_image")
          .map(a => `${base}/${a.file_path.replace(/\\/g, "/")}`);
        const task_files = taskFromApi.attachments
          .filter(a => a.attachment_type === "task_file")
          .map(a => `${base}/${a.file_path.replace(/\\/g, "/")}`);
  
        this.task = {
          ...taskFromApi,
          task_images,
          task_files,
        };
      } catch (error) {
        console.error("Ошибка при загрузке задания:", error);
        this.task = null;
      } finally {
        this.loading = false;
      }
    },
    getFileName(path) {
      return path.split("/").pop();
    },
    async submitAnswer() {
  try {
    const formData = new URLSearchParams({
      session_id: this.sessionId,
      task_id: this.currentTaskId,
      answer: this.userAnswer
    });
    await axios.post("/testing/submit_answer", formData, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" }
    });
    // Обновляем объект ответов без использования this.$set (Vue 3)
    this.answers[this.currentTaskIndex + 1] = this.userAnswer;
    // Автоматически переключаемся на следующее задание, если оно существует
    if (this.currentTaskIndex < this.taskIds.length - 1) {
      this.nextTask();
    }
    // Обнуляем поле ввода ответа
    this.userAnswer = "";
  } catch (error) {
    console.error("Ошибка отправки ответа:", error);
  }
}
,
    async finishTest() {
      try {
        await axios.post("http://localhost:8000/testing/complete", new URLSearchParams({ session_id: this.sessionId }));
        localStorage.removeItem("testSessionId");
        alert("Тест завершён! Результаты теста сохранены на сервере.");
        this.$router.push("/trainer");
      } catch (error) {
        console.error("Ошибка завершения теста:", error);
        alert("Ошибка при завершении теста.");
      }
    },
  },
  beforeUnmount() {
    if (this.timerSource) this.timerSource.close();
  },
};
</script>

<style scoped>
#test-session {
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
  background-color: #ffffff;
  padding: 20px;
  border-radius: 20px;
  margin-left: 20px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

/* Стили, перенятые из TrainTaskDetail */
.train-task-detail {
  padding: 20px;
}

.task-title {
  font-size: 24px;
  color: #115544;
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
  background-color: #115544;
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
