<template>
  <div id="test-session">
    <div class="container">
      <BuilderSidebar
        mode="session"
        :duration="Math.ceil(initialDuration / 60)"
        :count="taskIds.length"
        :current-index="currentTaskIndex"
        :answers="answersArray"
        :results="resultsArray"
        :test-finished="testFinished"
        :timer-display="formattedTimer"
        exit-label="Выйти"
        @select="goToTask"
        @prev="prevTask"
        @next="nextTask"
        @complete="finishTest"
        @exit="exitTest"
      />
      <main class="main-content">
        <div class="train-task-detail">
          <h2
            v-if="task"
            class="task-title"
          >
            Задание №{{ task.id }} (Тип {{ task.task_number }})
          </h2>
          <div
            v-if="loading"
            class="loading"
          >
            Загрузка задания...
          </div>
          <div
            v-else-if="!task"
            class="not-found"
          >
            Задание не найдено.
          </div>

          <div
            v-else
            class="task-container"
          >
            <div
              class="task-description ql-editor"
              v-html="task.description"
            />

            <div
              v-if="task.task_images?.length"
              class="task-images"
            >
              <img
                v-for="img in task.task_images"
                :key="img"
                :src="img"
                class="task-image"
              >
            </div>

            <div
              v-if="task.task_files?.length"
              class="task-files"
            >
              <div
                v-for="file in task.task_files"
                :key="file"
              >
                <a
                  :href="file"
                  target="_blank"
                  class="file-link"
                >
                  {{ getFileName(file) }}
                </a>
              </div>
            </div>

            <div class="answer-input">
              <label for="userAnswer">Ваш ответ:</label>
              <div
                v-if="isDynamicTable && dynamicTableConfig"
                class="dynamic-table"
              >
                <table>
                  <tr
                    v-for="(row, rIndex) in dynamicTableAnswers"
                    :key="rIndex"
                  >
                    <td
                      v-for="(cell, cIndex) in row"
                      :key="cIndex"
                    >
                      <input
                        v-model="dynamicTableAnswers[rIndex][cIndex]"
                        type="text"
                        :disabled="testFinished"
                        placeholder="Ответ"
                      >
                    </td>
                  </tr>
                </table>
              </div>
              <div v-else>
                <input
                  id="userAnswer"
                  v-model="userAnswer"
                  type="text"
                  :disabled="testFinished"
                  placeholder="Введите ваш ответ"
                >
              </div>
            </div>

            <button
              v-if="!testFinished"
              class="submit-answer-btn"
              @click="submitAnswer"
            >
              Отправить ответ
            </button>

            <button
              v-if="testFinished"
              class="solution-toggle-btn"
              @click="showSolution = !showSolution"
            >
              {{ showSolution ? 'Скрыть решение' : 'Показать решение' }}
            </button>

            <div
              v-if="testFinished && showSolution"
              class="solution-text"
            >
              <h3>Правильный ответ:</h3>
              <div
                class="ql-editor"
                v-html="task.correct_answer || 'Ответ отсутствует'"
              />
              <h3 style="margin-top: 15px;">
                Решение:
              </h3>
              <div
                class="ql-editor"
                v-html="solutions[task.id] || 'Решение отсутствует'"
              />
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
  name: "TestSession",
  components: { BuilderSidebar },
  data() {
    return {
      sessionId: null,
      taskIds: [],
      answers: {},
      results: {},
      score: 0,
      testFinished: false,
      currentTaskIndex: 0,
      remainingTime: 0,
      timerSource: null,
      task: null,
      loading: true,
      userAnswer: "",
      showSolution: false,
      solutions: {},
      dynamicTableAnswers: [],
      initialDuration: 0
    };
  },
  computed: {
    currentTaskId() {
      return this.taskIds[this.currentTaskIndex];
    },
    formattedTimer() {
      const hours = Math.floor(this.remainingTime / 3600);
      const minutes = Math.floor((this.remainingTime % 3600) / 60);
      return `${hours} ч ${minutes} мин`;
    },
    answersArray() {
      return this.taskIds.map(id => this.answers[id] || null);
    },
    resultsArray() {
      return this.taskIds.map(id => this.results[id]);
    },
    isDynamicTable() {
      return this.task && (
        Boolean(this.task.is_table_1x2) ||
        ["table2", "table10", "tableDyn1Col", "tableDyn2Col"].includes(this.task.answer_format)
      );
    },
    dynamicTableConfig() {
      if (!this.task) return null;
      try {
        if (["table2"].includes(this.task.answer_format) || [26, 27].includes(Number(this.task.task_number))) {
          return { rowsCount: 1, colCount: 2 };
        }
        if (["table10", "tableDyn1Col", "tableDyn2Col"].includes(this.task.answer_format)) {
          const parsed = JSON.parse(this.task.correct_answer || "[]");
          let colCount = 1;
          if (["table10", "tableDyn2Col"].includes(this.task.answer_format)) {
            colCount = 2;
          } else if (this.task.answer_format === "tableDyn1Col") {
            for (let row of parsed) {
              if (row.length >= 2 && row[1].trim()) {
                colCount = 2;
                break;
              }
            }
          }
          const extraRows = Math.floor(Math.random() * 5) + 3;
          return { colCount, rowsCount: parsed.length + extraRows };
        }
      } catch (e) {
        console.error(e);
      }
      return null;
    }
  },
  watch: {
    currentTaskId: {
      immediate: true,
      handler: 'loadTask'
    }
  },
  async created() {
    const savedId = localStorage.getItem("testSessionId");
    if (savedId) {
      try {
        const { data: session } = await this.$axios.get(`/testing/session/${savedId}`);
        this.sessionId = session.session_id;
        this.taskIds = session.task_ids;
        this.answers = { ...session.answers };
        this.initialDuration = session.total_time_seconds || this.initialDuration;
        if (!session.is_completed) {
          this.testFinished = false;
          this.startTimer();
        } else {
          this.testFinished = true;
          const { data: res } = await this.$axios.get(`/testing/results`, { params: { session_id: this.sessionId } });
          this.results = res.results || {};
          this.score = res.score || 0;
          const { data: sol } = await this.$axios.get(`/testing/solutions`, { params: { session_id: this.sessionId } });
          this.solutions = sol.solutions || {};
        }
        return;
      } catch {
        localStorage.removeItem("testSessionId");
      }
    }
    const userId = (JSON.parse(localStorage.getItem("user")) || {}).userId || 1;
    const formData = new FormData();
    formData.append("user_id", userId);
    formData.append("test_type", this.$route.query.test_type || "regular");
    const { data: res } = await this.$axios.post(`/testing/start`, formData);
    this.sessionId = res.session_id;
    this.taskIds = res.task_ids;
    this.initialDuration = res.total_time_seconds || this.initialDuration;
    localStorage.setItem("testSessionId", this.sessionId);
    this.startTimer();
  },
  mounted() {
    this.fixQuillCodeBlocks();
  },
  updated() {
    this.$nextTick(this.fixQuillCodeBlocks);
  },
  beforeUnmount() {
    if (this.timerSource) this.timerSource.close();
  },
  methods: {
    async loadTask() {
      this.loading = true;
      if (!this.currentTaskId) { this.loading = false; return; }
      try {
        const { data: taskData } = await this.$axios.get(`/exam_tasks/${this.currentTaskId}`);
        const base = window.location.origin;
        this.task = {
          ...taskData,
          task_images: taskData.attachments
            .filter(a => a.attachment_type === "task_image")
            .map(a => `${base}/${a.file_path.replace(/\\/g, "/")}`),
          task_files: taskData.attachments
            .filter(a => a.attachment_type === "task_file")
            .map(a => `${base}/${a.file_path.replace(/\\/g, "/")}`)
        };
        if (this.isDynamicTable && this.dynamicTableConfig) {
          const { rowsCount, colCount } = this.dynamicTableConfig;
          const parsed = JSON.parse(this.answers[this.currentTaskId] || "[]");
          this.dynamicTableAnswers = Array.from({ length: rowsCount }, (_, i) =>
            Array.from({ length: colCount }, (_, j) => (parsed[i]?.[j] || ""))
          );
        }
        this.userAnswer = this.answers[this.currentTaskId] || "";
      } catch {
        this.task = null;
      } finally {
        this.loading = false;
      }
    },
    startTimer() {
      const apiBase = this.$axios.defaults.baseURL;
      const source = new EventSource(`${apiBase}/sse/timer?session_id=${this.sessionId}`, { withCredentials: true });
      source.onmessage = e => {
        if (e.data === 'Test finished') {
          this.remainingTime = 0;
          source.close();
          this.finishTest();
        } else {
          this.remainingTime = parseInt(e.data, 10);
        }
      };
      this.timerSource = source;
    },
    goToTask(index) { this.currentTaskIndex = index; },
    prevTask() { if (this.currentTaskIndex > 0) this.currentTaskIndex--; },
    nextTask() { if (this.currentTaskIndex < this.taskIds.length - 1) this.currentTaskIndex++; },
    async submitAnswer() {
      if (this.testFinished) return;
      let answerToSend = "";
      if (this.isDynamicTable && this.dynamicTableConfig) {
        const filtered = this.dynamicTableAnswers
          .filter(row => row.some(cell => cell.trim()))
          .map(row => row.concat());
        answerToSend = JSON.stringify(this.dynamicTableConfig.rowsCount === 1 ? filtered[0] : filtered);
      } else {
        answerToSend = this.userAnswer;
      }
      await this.$axios.post(`/testing/submit_answer`, new URLSearchParams({
        session_id: this.sessionId,
        task_id: this.currentTaskId,
        answer: answerToSend
      }));
      this.answers = { ...this.answers, [this.currentTaskId]: answerToSend };
      this.userAnswer = "";
      this.nextTask();
    },
    async finishTest() {
      await this.$axios.post(`/testing/complete`, new URLSearchParams({ session_id: this.sessionId }));
      const { data: res } = await this.$axios.get(`/testing/results`, { params: { session_id: this.sessionId } });
      this.results = res.results || {};
      this.score = res.score || 0;
      const { data: sol } = await this.$axios.get(`/testing/solutions`, { params: { session_id: this.sessionId } });
      this.solutions = sol.solutions || {};
      this.testFinished = true;
    },
    exitTest() {
      localStorage.removeItem("testSessionId");
      this.$router.push("/trainer");
    },
    getFileName(path) {
      return path.split("/").pop();
    },
    fixQuillCodeBlocks() {
      document.querySelectorAll('.ql-editor pre, .ql-editor code').forEach(el => {
        el.style.overflowX = 'auto';
        el.style.whiteSpace = 'pre-wrap';
        el.style.wordBreak = 'break-all';
      });
    }
  }
};
</script>


<style scoped>
/* Основная верстка */
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

/* Заголовки и тип задания */
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

/* Описание задания, изображения и файлы */
.task-description {
  margin-bottom: 10px;
  line-height: 1.5;
  word-break: break-word;
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

.file-link {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: #56AEF6;
  font-size: 16px;
}

.file-link::before {
  content: "";
  display: inline-block;
  width: 16px;
  height: 16px;
  background-image: url("@/assets/svg/files.svg");
  background-size: contain;
  background-repeat: no-repeat;
  margin-right: 5px;
}

/* Ввод ответа */
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

/* Стили таблицы для динамического ввода */
.dynamic-table {
  overflow-x: auto;
}

.dynamic-table table {
  border-collapse: collapse;
  margin: 0 auto;
}

.dynamic-table td {
  padding: 5px;
  border: none;
}

.dynamic-table input[type="text"] {
  width: 80px;
  max-width: 80px;
  padding: 4px;
  text-align: center;
  border: 1px solid #ccc;
  border-radius: 3px;
}

/* Кнопки */
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

.solution-toggle-btn {
  background-color: #337ab7;
  color: #fff;
  padding: 10px 15px;
  border: none;
  border-radius: 8px;
  margin-top: 15px;
  cursor: pointer;
}

/* Блок решения */
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

/* Таблица кода внутри Quill */
.ql-editor pre,
.ql-editor code {
  max-width: 100%;
  overflow-x: auto !important;
  white-space: pre-wrap !important;
  word-break: break-all !important;
}

/* Прочие элементы */
</style>
