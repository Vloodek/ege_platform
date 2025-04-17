<template>
  <div id="test-session">
    <div class="container">
      <SideBar :isTestActive="true" :taskIds="taskIds" :currentTaskIndex="currentTaskIndex" :answers="answers"
        :results="results" :score="score" :testFinished="testFinished" :timerDisplay="remainingTime"
        :totalQuestions="taskIds.length" @selectTask="goToTask" @prevTask="prevTask" @nextTask="nextTask"
        @finishTest="finishTest" @exitTest="exitTest" @goBack="goBack" />

      <main class="main-content">
        <div class="train-task-detail">
          <h2 class="task-title" v-if="task">Задание №{{ task.id }} (Тип {{ task.task_number }})</h2>
          <div v-if="loading" class="loading">Загрузка задания...</div>
          <div v-else-if="!task" class="not-found">Задание не найдено.</div>

          <div v-else class="task-container">
            <!-- Описание задания -->
            <div class="task-description ql-editor" v-html="task.description"></div>

            <!-- Картинки задания -->
            <div class="task-images" v-if="task.task_images?.length">
              <img v-for="img in task.task_images" :key="img" :src="img" class="task-image" />
            </div>

            <!-- Файлы задания с иконкой -->
            <div class="task-files" v-if="task.task_files?.length">
              <div v-for="file in task.task_files" :key="file">
                <a :href="file" target="_blank" class="file-link">
                  {{ getFileName(file) }}
                </a>
              </div>
            </div>

            <!-- Ввод ответа -->
            <div class="answer-input">
              <label for="userAnswer">Ваш ответ:</label>
              <!-- Если задание динамическое (табличка) -->
              <div v-if="isDynamicTable && dynamicTableConfig" class="dynamic-table">
                <table>
                  <tr v-for="(row, rIndex) in dynamicTableAnswers" :key="rIndex">
                    <td v-for="(cell, cIndex) in row" :key="cIndex">
                      <input type="text" v-model="dynamicTableAnswers[rIndex][cIndex]" :disabled="testFinished"
                        placeholder="Ответ" />
                    </td>
                  </tr>
                </table>
              </div>
              <!-- Иначе обычный ввод -->
              <div v-else>
                <input type="text" id="userAnswer" v-model="userAnswer" :disabled="testFinished"
                  placeholder="Введите ваш ответ" />
              </div>
            </div>

            <!-- Кнопка отправки ответа -->
            <button v-if="!testFinished" class="submit-answer-btn" @click="submitAnswer">
              Отправить ответ
            </button>

            <!-- Кнопка показать решение -->
            <button v-if="testFinished" class="solution-toggle-btn" @click="showSolution = !showSolution">
              {{ showSolution ? "Скрыть решение" : "Показать решение" }}
            </button>

            <!-- Отображение решения -->
            <div v-if="testFinished && showSolution" class="solution-text">
              <h3>Правильный ответ:</h3>
              <div class="ql-editor" v-html="task.correct_answer || 'Ответ отсутствует'"></div>
              <h3 style="margin-top: 15px;">Решение:</h3>
              <div class="ql-editor" v-html="solutions[task.id] || 'Решение отсутствует'"></div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import SideBar from "../SideBar.vue";

export default {
  name: "TestSession",
  components: { SideBar },
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
      dynamicTableAnswers: [] // Массив для динамической таблицы, если задание динамическое
    };
  },
  computed: {
    currentTaskId() {
      return this.taskIds[this.currentTaskIndex];
    },
    testType() {
      return this.$route.query.test_type || "regular";
    },
    isDynamicTable() {
      return this.task && (
        Boolean(this.task.is_table_1x2) ||
        ["table2", "table10", "tableDyn1Col", "tableDyn2Col"].includes(this.task.answer_format)
      );
    },
    dynamicTableConfig() {
      if (!this.task) return null;

      if (["table2"].includes(this.task.answer_format) || [26, 27].includes(Number(this.task.task_number))) {
        return { rowsCount: 1, colCount: 2 };
      }

      if (["table10", "tableDyn1Col", "tableDyn2Col"].includes(this.task.answer_format)) {
        try {
          const parsed = JSON.parse(this.task.correct_answer || "[]");
          let colCount = 1;
          if (this.task.answer_format === "table10" || this.task.answer_format === "tableDyn2Col") {
            colCount = 2;
          } else if (this.task.answer_format === "tableDyn1Col") {
            for (let row of parsed) {
              if (row.length >= 2 && row[1].trim() !== "") {
                colCount = 2;
                break;
              }
            }
          }
          const expectedRows = parsed.length;
          const extraRows = Math.floor(Math.random() * 5) + 3;
          const totalRows = expectedRows + extraRows;
          return { colCount, rowsCount: totalRows };
        } catch (error) {
          console.error("Ошибка парсинга корректного ответа для динамической таблицы", error);
          return null;
        }
      }

      return null;
    }
  },
  watch: {
    currentTaskId: {
      immediate: true,
      handler() {
        this.loadTask();
      }
    }
  },
  async created() {
    const savedId = localStorage.getItem("testSessionId");
    if (savedId) {
      try {
        const res = await this.$axios.get(`/testing/session/${savedId}`);

        const session = res.data;
        this.sessionId = session.session_id;
        this.taskIds = session.task_ids;
        this.answers = { ...session.answers };

        if (!session.is_completed) {
          this.testFinished = false;
          this.startTimer();
        } else {
          this.testFinished = true;
          const resResults = await this.$axios.get(`/testing/results?session_id=${session.session_id}`);
          this.results = resResults.data.results || {};
          this.score = resResults.data.score || 0;
          const resSol = await this.$axios.get(`/testing/solutions?session_id=${session.session_id}`);
          this.solutions = resSol.data.solutions || {};
        }
        return;
      } catch (e) {
        console.warn("Ошибка восстановления сессии", e);
        localStorage.removeItem("testSessionId");
      }
    }
    const userId = (JSON.parse(localStorage.getItem("user")) || {}).userId || 1;
    const formData = new FormData();
    formData.append("user_id", userId);
    formData.append("test_type", this.testType);
    const res = await this.$axios.post(`/testing/start`, formData);
    this.sessionId = res.data.session_id;
    this.taskIds = res.data.task_ids;
    localStorage.setItem("testSessionId", this.sessionId);
    this.startTimer();
  },
  methods: {
    goBack() {
      this.$router.back();
    },
    fixQuillCodeBlocks() {
      // Находим все блоки кода в Quill-редакторе
      const codeBlocks = document.querySelectorAll('.ql-editor pre, .ql-editor code');
      codeBlocks.forEach(el => {
        // Задаём необходимые стили, перезаписывая встроенные стили
        el.style.overflowX = 'auto';
        el.style.whiteSpace = 'pre-wrap';
        el.style.wordBreak = 'break-all';
      });
    },
    startTimer() {
  const apiBase = this.$axios.defaults.baseURL; 
  // по-умолчанию 'http://localhost:8000'
  const source = new EventSource(
    `${apiBase}/sse/timer?session_id=${this.sessionId}`,
    { withCredentials: true }
  );

  source.onopen    = () => console.log('[SSE] connection opened');
  source.onerror   = err => console.error('[SSE] error', err);
  source.onmessage = event => {
    console.log('[SSE] message:', event.data);
    if (event.data === 'Test finished') {
      this.remainingTime = 0;
      source.close();
      this.finishTest();
    } else {
      this.remainingTime = parseInt(event.data, 10);
    }
  };

  this.timerSource = source;
},


    goToTask(index) {
      this.currentTaskIndex = index;
    },
    prevTask() {
      if (this.currentTaskIndex > 0) this.currentTaskIndex--;
    },
    nextTask() {
      if (this.currentTaskIndex < this.taskIds.length - 1) this.currentTaskIndex++;
    },
    async loadTask() {
      if (!this.currentTaskId) {
        this.loading = false;
        return;
      }
      this.loading = true;
      try {
        const res = await this.$axios.get(`/exam_tasks/${this.currentTaskId}`);

        const base = window.location.origin;
        const task = res.data;
        task.task_images = task.attachments
          .filter(a => a.attachment_type === "task_image")
          .map(a => `${base}/${a.file_path.replace(/\\/g, "/")}`);
        task.task_files = task.attachments
          .filter(a => a.attachment_type === "task_file")
          .map(a => `${base}/${a.file_path.replace(/\\/g, "/")}`);
        this.task = task;

        // Если задание должно отображаться как динамическая таблица
        if (this.isDynamicTable && this.dynamicTableConfig) {
          const { rowsCount, colCount } = this.dynamicTableConfig;
          this.dynamicTableAnswers = [];
          const saved = this.answers[String(this.currentTaskId)];
          let parsed = [];
          if (saved) {
            try {
              parsed = JSON.parse(saved);
            } catch (e) {
              console.warn("Не удалось распарсить сохранённый ответ", e);
            }
          }
          for (let i = 0; i < rowsCount; i++) {
            const row = [];
            for (let j = 0; j < colCount; j++) {
              row.push((parsed[i] && parsed[i][j]) || "");
            }
            this.dynamicTableAnswers.push(row);
          }
        }
        // Если обычный ввод – используем его
        this.userAnswer = this.answers[String(this.currentTaskId)] || "";
      } catch (e) {
        this.task = null;
      } finally {
        this.loading = false;
      }
    },
    getFileName(path) {
      return path.split("/").pop();
    },
    async submitAnswer() {
      if (this.testFinished) return;
      let answerToSend = "";
      if (this.isDynamicTable && this.dynamicTableConfig) {
        const { rowsCount, colCount } = this.dynamicTableConfig;
        const filteredRows = this.dynamicTableAnswers
          .filter(row => row.some(cell => cell.trim() !== ""))
          .map(row => {
            const filled = [...row];
            while (filled.length < colCount) filled.push("");
            return filled;
          });
        if (rowsCount === 1) {
          answerToSend = JSON.stringify(filteredRows[0] || []);
        } else {
          answerToSend = JSON.stringify(filteredRows);
        }
      } else {
        answerToSend = this.userAnswer;
      }
      const payload = new URLSearchParams({
        session_id: this.sessionId,
        task_id: this.currentTaskId,
        answer: answerToSend
      });
      await this.$axios.post(`/testing/submit_answer`, payload, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" }
      });

      this.answers[String(this.currentTaskId)] = answerToSend;
      this.userAnswer = "";
      if (this.currentTaskIndex < this.taskIds.length - 1) this.nextTask();
    },
    async finishTest() {
      await this.$axios.post(`/testing/complete`, new URLSearchParams({ session_id: this.sessionId }));
      try {
        const res = await this.$axios.get(`/testing/results?session_id=${this.sessionId}`);
        this.results = res.data.results || {};
        this.score = res.data.score || 0;
        const resSol = await this.$axios.get(`/testing/solutions?session_id=${this.sessionId}`);
        this.solutions = resSol.data.solutions || {};
      } catch (err) {
        console.warn("Не удалось получить результаты", err);
      }
      this.testFinished = true;
    },
    exitTest() {
      localStorage.removeItem("testSessionId");
      this.$router.push("/trainer");
    }
  },
  beforeUnmount() {
    if (this.timerSource) this.timerSource.close();
  },
  mounted() {
    // После монтирования компонента фиксируем стили блоков кода
    this.fixQuillCodeBlocks();
  },

  updated() {
    // После обновления компонента (например, при смене задания) вызываем этот метод, чтобы гарантировать обновление стилей
    this.$nextTick(() => {
      this.fixQuillCodeBlocks();
    });
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
  color: #115544;
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
