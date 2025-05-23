<template>
  <div id="create-homework-test">
    <div class="container">
      <BuilderSidebar
        v-model:duration="duration"
        v-model:count="questionCount"
        :current-index="currentQuestion"
        @select="handleSelectQuestion"

        @prev="prevQuestion"
        @next="nextQuestion"
      />

      <main class="main-content">
        <h2>Создание теста для занятия «{{ lessonName || homeworkId }}»</h2>

        <div
          v-if="currentTask"
          class="question-editor"
        >
          <h3>Вопрос {{ currentQuestion + 1 }} из {{ questionCount }}</h3>

          <div class="form-group">
            <label>Название</label>
            <input
              v-model="currentTask.title"
              type="text"
              placeholder="Заголовок вопроса"
            >
          </div>

          <div class="form-group">
            <label>Описание</label>
            <div
              ref="editor"
              class="quill-editor"
            />
          </div>

          <div class="form-group">
            <label>Правильный ответ</label>
            <input
              v-model="currentTask.correct_answer"
              type="text"
              placeholder="Введите правильный ответ"
            >
          </div>

          <div class="form-group">
            <label>Вложения (любой файл, кроме изображений)</label>
            <input
              type="file"
              multiple
              @change="onFilesChange"
            >
            <ul class="file-list">
              <li
                v-for="(f, i) in currentTask.files"
                :key="i"
              >
                <img
                  src="@/assets/svg/files.svg"
                  class="file-icon"
                >
                {{ f.name }}
                <button @click="currentTask.files.splice(i, 1)">
                  ×
                </button>
              </li>
            </ul>
          </div>
        </div>

        <div class="actions">
          <button
            class="cancel-test"
            @click="requestLeave"
          >
            Назад
          </button>
          <button
            class="save-test"
            @click="submitTest"
          >
            Сохранить тест
          </button>
        </div>

        <ConfirmModal
          :show="showLeaveModal"
          title="Покинуть страницу?"
          message="Все несохранённые изменения будут потеряны. Вы уверены, что хотите уйти?"
          cancel-text="Остаться"
          confirm-text="Уйти"
          @cancel="cancelLeave"
          @confirm="confirmLeave"
        />
      </main>
    </div>
  </div>
</template>

<script>
import BuilderSidebar from "@/components/testing/BuilderSideBar.vue";
import ConfirmModal from "@/components/UI/ConfirmModal.vue";

import Quill from "quill";
import "quill/dist/quill.snow.css";
import { nextTick } from "vue";

export default {
  name: "CreateHomeworkTest",
  components: { BuilderSidebar,
    ConfirmModal},
  data() {
    return {
      homeworkId: this.$route.params.id,
      lessonName: "",
      duration: 30,
      questionCount: 5,
      currentQuestion: 0,
      tasks: [],
      quill: null,
      showLeaveModal: false,
    };
  },
  computed: {
    currentTask() {
      // Защита от undefined
      return (
        this.tasks[this.currentQuestion] || {
          title: "",
          description: "",
          correct_answer: "",
          files: [],
        }
      );
    },
  },
  watch: {
    questionCount(n) {
      // Увеличиваем массив tasks до нужного размера
      while (this.tasks.length < n) {
        this.tasks.push({
          title: "",
          description: "",
          correct_answer: "",
          files: [],
        });
      }
      // Обрезаем лишние
      if (this.tasks.length > n) {
        this.tasks.splice(n);
        if (this.currentQuestion >= n) {
          this.currentQuestion = n - 1;
        }
      }
    },
    currentQuestion(newIdx, oldIdx) {
      if (!this.quill) return;
      // Сохраняем старое описание
      const old = this.tasks[oldIdx];
      if (old) {
        old.description = this.quill.root.innerHTML;
      }
      // Устанавливаем новое
      const next = this.tasks[newIdx];
      this.quill.root.innerHTML = next?.description || "";
    },
  },
  async created() {
    await this.fetchLessonName();
  },
  mounted() {
    // Инициализация массива задач
    this.tasks = Array.from({ length: this.questionCount }).map(() => ({
      title: "",
      description: "",
      correct_answer: "",
      files: [],
    }));
    nextTick(this.initQuill);
  },
  methods: {
    async fetchLessonName() {
      try {
        const { data } = await this.$axios.get(`/lessons/${this.homeworkId}`);
        // Эндпоинт может вернуть объект или массив
        this.lessonName = data.name ?? data[0]?.name ?? "";
      } catch (err) {
        console.error("Ошибка загрузки названия урока:", err);
      }
    },
    requestLeave() {
    this.showLeaveModal = true;
  },
  cancelLeave() {
    this.showLeaveModal = false;
  },
  confirmLeave() {
    this.showLeaveModal = false;
    this.$router.back();
  },
    handleSelectQuestion(index) {
  // Если передали событие случайно
  if (typeof index !== "number") return;
  this.currentQuestion = index;
}

,
    initQuill() {
      this.quill = new Quill(this.$refs.editor, {
        theme: "snow",
        modules: {
          toolbar: {
            container: [
              [{ header: [1, 2] }],
              [{ list: "ordered" }, { list: "bullet" }],
              ["bold", "italic", "underline"],
              [{ align: [] }],
              ["link", "image"],
            ],
            handlers: {
              image: () => {
                const input = document.createElement("input");
                input.type = "file";
                input.accept = "image/*";
                input.click();
                input.onchange = () => {
                  const file = input.files[0];
                  if (file) this.uploadAndInsertImage(this.quill, file);
                };
              },
            },
          },
        },
      });

      // Задаём первоначальное содержимое
      this.quill.root.innerHTML = this.currentTask.description || "";
      this.quill.on("text-change", () => {
        this.currentTask.description = this.quill.root.innerHTML;
      });
      this.quill.root.addEventListener("paste", (e) =>
        this.handlePaste(e, this.quill)
      );
    },

    async uploadAndInsertImage(quill, file) {
      const fd = new FormData();
      fd.append("image", file);
      try {
        const { data } = await this.$axios.post(
          "/upload_temp_image",
          fd,
          { headers: { "Content-Type": "multipart/form-data" } }
        );
        const range = quill.getSelection();
        if (range) quill.insertEmbed(range.index, "image", data.image_url);
      } catch (e) {
        console.error("Ошибка загрузки изображения:", e);
        alert("Ошибка загрузки изображения");
      }
    },

    handlePaste(e, quill) {
      const items = (e.clipboardData || window.clipboardData).items;
      for (const item of items) {
        if (item.type.startsWith("image")) {
          e.preventDefault();
          const file = item.getAsFile();
          if (file) this.uploadAndInsertImage(quill, file);
        }
      }
    },

    prevQuestion() {
      if (this.currentQuestion > 0) this.currentQuestion--;
    },

    nextQuestion() {
      if (this.currentQuestion < this.questionCount - 1)
        this.currentQuestion++;
    },

    onFilesChange(e) {
      Array.from(e.target.files)
        .filter((f) => !f.type.startsWith("image/"))
        .forEach((f) => this.currentTask.files.push(f));
      e.target.value = null;
    },

    async submitTest() {
      // Сохраняем текущее описание
      this.currentTask.description = this.quill.root.innerHTML;

      const form = new FormData();
      form.append("lesson_id", this.homeworkId);
      form.append("duration", this.duration);

      // Собираем мета
      const meta = this.tasks.map((t, idx) => ({
        title: t.title,
        description: t.description,
        correct_answer: t.correct_answer,
        files: t.files.map((f) => `${idx}__${f.name}`),
      }));
      form.append("tasks_meta", JSON.stringify(meta));

      // Прикладываем файлы
      this.tasks.forEach((t, idx) =>
        t.files.forEach((f) =>
          form.append("task_files", f, `${idx}__${f.name}`)
        )
      );

      try {
        await this.$axios.post("/homework_tests/", form, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        this.$router.push(`/homeworks/${this.homeworkId}/tests`);
      } catch (err) {
        console.error(err);
        alert("Не удалось сохранить тест");
      }
    },
  },
};
</script>

<style scoped>
.container {
  display: flex;
  max-width: 1200px;
  margin: 0 auto;
}
.main-content {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-left: 20px;
}
.form-group {
  margin-bottom: 16px;
}
.form-group label {
  display: block;
  margin-bottom: 4px;
}
.form-group input[type="text"] {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.quill-editor {
  height: 180px;
  background: #fafafa;
}
.file-list {
  margin-top: 8px;
  list-style: none;
  padding: 0;
}
.file-list li {
  display: flex;
  align-items: center;
  margin-bottom: 6px;
}
.file-icon {
  width: 20px;
  height: 20px;
  margin-right: 6px;
}
.file-list button {
  margin-left: auto;
  border: none;
  background: transparent;
  color: #900;
  cursor: pointer;
}
.actions {
  text-align: right;
  margin-top: 20px;
}
.save-test {
  background: #56AEF6;
  color: white;
  padding: 10px 18px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
.cancel-test {
  background: #ccc;
  color: #333;
  padding: 10px 18px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  margin-right: 10px;
}
.cancel-test:hover {
  background: #bbb;
}

</style>
