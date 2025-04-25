<template>
  <div id="homework-test-session">
    <div class="container">
      <BuilderSidebar
        mode="session"
        :duration="duration"
        :count="taskIds.length"
        :currentIndex="currentTaskIndex"
        :timerDisplay="formattedTime"
        :answers="answers"
        :results="results"
        :testFinished="testFinished"
        exitLabel="Выйти"
        @select="goToTask"
        @prev="prevTask"
        @next="nextTask"
        @exit="exitTest"
        @complete="finishTest"
      />

      <main class="main-content">
        <div class="task-detail">
          <h2 v-if="currentTask" class="task-title">Задание №{{ currentTask.id }}</h2>
          <div v-if="loading" class="loading">Загрузка задания...</div>
          <div v-else-if="!currentTask" class="not-found">Задание не найдено.</div>

          <div v-else class="task-container">
            <div class="task-description ql-editor" v-html="currentTask.description"></div>

            <div class="task-files" v-if="currentTask.files?.length">
              <div v-for="file in currentTask.files" :key="file">
                <a :href="file" target="_blank" class="file-link">{{ getFileName(file) }}</a>
              </div>
            </div>

            <div class="answer-input">
              <label for="userAnswer">Ваш ответ:</label>
              <input
                id="userAnswer"
                type="text"
                v-model="userAnswer"
                :disabled="testFinished"
                placeholder="Введите ваш ответ"
              />
            </div>

            <button v-if="!testFinished" class="submit-answer-btn" @click="submitAnswer">
              Отправить ответ
            </button>
            <button v-else class="solution-toggle-btn" @click="showSolution = !showSolution">
              {{ showSolution ? "Скрыть решение" : "Показать решение" }}
            </button>

            <div v-if="testFinished && showSolution" class="solution-text">
              <h3>Правильный ответ:</h3>
              <div class="ql-editor" v-html="getCorrectAnswerHtml(currentTask.id)"></div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import BuilderSidebar from "@/components/testing/BuilderSideBar.vue";

export default {
  name: "HomeworkTestSession",
  components: { BuilderSidebar },
  data() {
    return {
      testId: null,
      sessionId: null,
      storageKeyBase: null,

      duration: 0,
      taskIds: [],
      tasksMap: {},
      results: {},
      correctAnswers: {},
      answers: {},
      score: 0,
      testFinished: false,

      currentTaskIndex: 0,
      remainingTime: 0,
      timerSource: null,

      loading: true,
      userAnswer: "",
      showSolution: false,
    };
  },
  computed: {
    currentTask() {
      return this.tasksMap[this.taskIds[this.currentTaskIndex]] || null;
    },
    formattedTime() {
      const total = this.remainingTime;
      const hours = Math.floor(total / 3600);
      const minutes = Math.floor((total % 3600) / 60);
      return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}`;
    },
  },
  watch: {
    currentTask: {
      immediate: true,
      handler(task) {
        this.userAnswer = this.answers[task?.id] || "";
      },
    },
    answers: {
      deep: true,
      handler(val) {
        if (this.storageKeyBase) {
          localStorage.setItem(`${this.storageKeyBase}_answers`, JSON.stringify(val));
        }
      },
    },
    results: {
      deep: true,
      handler(val) {
        if (this.storageKeyBase) {
          localStorage.setItem(`${this.storageKeyBase}_results`, JSON.stringify(val));
        }
      },
    },
    correctAnswers: {
      deep: true,
      handler(val) {
        if (this.storageKeyBase) {
          localStorage.setItem(`${this.storageKeyBase}_correct_answers`, JSON.stringify(val));
        }
      },
    },
    testFinished(val) {
      if (this.storageKeyBase) {
        localStorage.setItem(`${this.storageKeyBase}_finished`, val ? "true" : "false");
      }
    },
  },
  async created() {
    const { id, lesson_id } = this.$route.params;
    if (id) this.testId = Number(id);
    else {
      const resByLesson = await this.$axios.get(`/homework_tests/by_lesson/${Number(lesson_id)}`);
      this.testId = resByLesson.data.id;
    }

    const resTest = await this.$axios.get(`/homework_tests/${this.testId}`);
    this.duration = resTest.data.duration;
    this.initTasks(resTest.data.tasks || []);

    const savedSession = localStorage.getItem("homeworkSessionId");
    if (savedSession) {
      this.sessionId = Number(savedSession);
    } else {
      const user = JSON.parse(localStorage.getItem("user")) || {};
      const form = new FormData();
      form.append("user_id", String(user.userId));
      const resStart = await this.$axios.post(`/homework_tests/${this.testId}/start`, form);
      this.sessionId = resStart.data.attempt_id;
      this.remainingTime = resStart.data.remaining_time;
      localStorage.setItem("homeworkSessionId", this.sessionId);
    }

    this.storageKeyBase = `homeworkSession_${this.sessionId}`;
    const sa = localStorage.getItem(`${this.storageKeyBase}_answers`);
    if (sa) this.answers = JSON.parse(sa);
    const sr = localStorage.getItem(`${this.storageKeyBase}_results`);
    if (sr) this.results = JSON.parse(sr);
    const sca = localStorage.getItem(`${this.storageKeyBase}_correct_answers`);
    if (sca) this.correctAnswers = JSON.parse(sca);
    const sf = localStorage.getItem(`${this.storageKeyBase}_finished`);
    if (sf === "true") this.testFinished = true;

    if (savedSession) {
      const resSess = await this.$axios.get(`/homework_tests/session/${this.sessionId}`);
      this.answers = resSess.data.answers || this.answers;
      this.testFinished = resSess.data.is_completed || this.testFinished;
      if (!this.testFinished) {
        this.remainingTime = resSess.data.remaining_time;
      }
    }

    if (!this.testFinished) {
      this.startTimer();
    }

    this.loading = false;
  },
  methods: {
    initTasks(tasks) {
      const base = window.location.origin;
      this.taskIds = tasks.map((t) => t.id);
      tasks.forEach((t) => {
        t.files = (t.files || []).map((p) => `${base}/${p.replace(/\\/g, "/")}`);
        this.tasksMap[t.id] = t;
      });
    },
    getCorrectAnswerHtml(taskId) {
      return this.correctAnswers[taskId] || "";
    },
    startTimer() {
      const apiBase = this.$axios.defaults.baseURL;
      this.timerSource = new EventSource(
        `${apiBase}/sse/timer?session_id=${this.sessionId}`,
        { withCredentials: true }
      );
      this.timerSource.onmessage = (e) => {
        if (e.data === "Test finished") {
          this.remainingTime = 0;
          this.finishTest();
        } else {
          const secs = parseInt(e.data, 10);
          if (!isNaN(secs)) this.remainingTime = secs;
        }
      };
      this.timerSource.onerror = console.error;
    },
    getFileName(path) {
      return path.split("/").pop();
    },
    async submitAnswer() {
  if (this.testFinished) return;

  const id = this.currentTask.id;
  this.answers = { ...this.answers, [id]: this.userAnswer };

  const form = new FormData();
  form.append("session_id", String(this.sessionId));
  form.append("task_id", String(id));
  form.append("answer", this.userAnswer);

  await this.$axios.post("/testing/submit_answer", form);

  // если не последний — идем дальше
  if (this.currentTaskIndex < this.taskIds.length - 1) {
    this.currentTaskIndex++;
  }

  // сбрасываем поле только если не последний
  if (this.currentTaskIndex < this.taskIds.length - 1) {
    this.userAnswer = this.answers[this.taskIds[this.currentTaskIndex]] || "";
  } else {
    // на последнем — оставить ответ, не сбрасывать
    this.userAnswer = this.answers[id];
  }
}
,
    goToTask(i) {
      this.currentTaskIndex = i;
    },
    prevTask() {
      if (this.currentTaskIndex > 0) this.currentTaskIndex--;
    },
    nextTask() {
      if (this.currentTaskIndex < this.taskIds.length - 1) {
        this.currentTaskIndex++;
      }
    },
    async finishTest() {
      if (this.timerSource) this.timerSource.close();
      this.testFinished = true;
      const form = new FormData();
      form.append("session_id", String(this.sessionId));
      await this.$axios.post("/testing/complete", form);
      const res = await this.$axios.get(`/homework_tests/session/${this.sessionId}/results`);
      this.score = res.data.score;
      this.results = res.data.results;
      this.correctAnswers = res.data.correct_answers;
    },
    exitTest() {
      if (this.timerSource) this.timerSource.close();
      localStorage.removeItem("homeworkSessionId");
      localStorage.removeItem(`${this.storageKeyBase}_answers`);
      localStorage.removeItem(`${this.storageKeyBase}_results`);
      localStorage.removeItem(`${this.storageKeyBase}_finished`);
      localStorage.removeItem(`${this.storageKeyBase}_correct_answers`);
      this.$router.push("/homework");
    },
  },
  beforeUnmount() {
    if (this.timerSource) this.timerSource.close();
  },
};
</script>


<style scoped>
#homework-test-session {
  display: flex;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.ql-editor img {
  max-width: 100%;
  height: auto;
}
::v-deep .ql-editor img {
  max-width: 100% !important;
  height: auto !important;
  display: block;
  margin: 0 auto;
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
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
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

.task-description {
  margin-bottom: 10px;
  line-height: 1.5;
  word-break: break-word;
}

.task-files {
  margin-bottom: 10px;
}

.file-link {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: #115544;
  font-size: 16px;
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
  max-width: 300px;
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

.solution-toggle-btn {
  background-color: #337ab7;
  color: #fff;
  padding: 10px 15px;
  border: none;
  border-radius: 8px;
  margin-top: 15px;
  cursor: pointer;
}

.solution-text {
  margin-top: 20px;
  background-color: #f0f9ff;
  padding: 15px;
  border: 1px solid #ccc;
  border-radius: 8px;
  max-width: 100%;
  box-sizing: border-box;
  overflow-wrap: break-word;
  word-break: break-word;
}
.solution-text .ql-editor {
  white-space: normal !important;
  overflow-x: auto !important;
  max-width: 100% !important;
  word-break: break-all !important;
}
</style>
