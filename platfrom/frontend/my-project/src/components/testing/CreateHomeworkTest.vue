<template>
  <div id="create-homework-test">
    <div class="container">
      <BuilderSidebar
        v-model:duration="duration"
        v-model:count="questionCount"
        :currentIndex="currentQuestion"
        @select="currentQuestion = $event"
        @prev="prevQuestion"
        @next="nextQuestion"
      />

      <main class="main-content">
        <h2>Создание теста для ДЗ №{{ homeworkId }}</h2>

        <div class="question-editor" v-if="currentTask">
          <h3>Вопрос {{ currentQuestion + 1 }} из {{ questionCount }}</h3>

          <div class="form-group">
            <label>Название</label>
            <input type="text" v-model="currentTask.title" placeholder="Заголовок вопроса" />
          </div>

          <div class="form-group">
            <label>Описание</label>
            <div ref="editor" class="quill-editor"></div>
          </div>

          <div class="form-group">
            <label>Правильный ответ</label>
            <input type="text" v-model="currentTask.correct_answer" placeholder="Введите правильный ответ" />
          </div>

          <div class="form-group">
            <label>Вложения (любой файл, кроме изображений)</label>
            <input type="file" multiple @change="onFilesChange" />
            <ul class="file-list">
              <li v-for="(f, i) in currentTask.files" :key="i">
                <img src="@/assets/svg/files.svg" class="file-icon" />
                {{ f.name }}
                <button @click="currentTask.files.splice(i, 1)">×</button>
              </li>
            </ul>
          </div>
        </div>

        <div class="actions">
          <button @click="submitTest" class="save-test">Сохранить тест</button>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import BuilderSidebar from "@/components/testing/BuilderSideBar.vue";
import Quill from "quill";
import "quill/dist/quill.snow.css";
import { nextTick } from "vue";

export default {
  name: "CreateHomeworkTest",
  components: { BuilderSidebar },
  data() {
    return {
      homeworkId: this.$route.params.id,
      duration: 30,
      questionCount: 5,
      currentQuestion: 0,
      tasks: [],
      quill: null,
    };
  },
  computed: {
    currentTask() {
      return this.tasks[this.currentQuestion];
    },
  },
  watch: {
    questionCount(n) {
      while (this.tasks.length < n) {
        this.tasks.push({
          title: "",
          description: "",
          correct_answer: "",
          files: [],
        });
      }
      if (this.tasks.length > n) {
        this.tasks.splice(n);
        if (this.currentQuestion >= n) this.currentQuestion = n - 1;
      }
    },
    currentQuestion(newIdx, oldIdx) {
      if (this.quill) {
        this.tasks[oldIdx].description = this.quill.root.innerHTML;
        this.quill.root.innerHTML = this.tasks[newIdx].description || "";
      }
    },
  },
  mounted() {
    this.tasks = Array.from({ length: this.questionCount }).map(() => ({
      title: "",
      description: "",
      correct_answer: "",
      files: [],
    }));
    nextTick(this.initQuill);
  },
  methods: {
    initQuill() {
      const vm = this;
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
              image() {
                const input = document.createElement("input");
                input.type = "file";
                input.accept = "image/*";
                input.click();
                input.onchange = () => {
                  const file = input.files[0];
                  if (file) vm.uploadAndInsertImage(vm.quill, file);
                };
              },
            },
          },
        },
      });

      this.quill.root.innerHTML = this.currentTask.description || "";
      this.quill.on("text-change", () => {
        this.currentTask.description = this.quill.root.innerHTML;
      });

      this.quill.root.addEventListener("paste", (e) => this.handlePaste(e, this.quill));
    },

    async uploadAndInsertImage(quill, file) {
      const fd = new FormData();
      fd.append("image", file);
      try {
        const { data } = await this.$axios.post("/upload_temp_image", fd, {
          headers: { "Content-Type": "multipart/form-data" },
        });
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
      if (this.currentQuestion < this.questionCount - 1) this.currentQuestion++;
    },

    onFilesChange(e) {
      Array.from(e.target.files)
        .filter((f) => !f.type.startsWith("image/"))
        .forEach((f) => this.currentTask.files.push(f));
      e.target.value = null;
    },

    async submitTest() {
      this.currentTask.description = this.quill.root.innerHTML;

      const form = new FormData();
      form.append("lesson_id", this.homeworkId);
      form.append("duration", this.duration);
      form.append(
        "tasks_meta",
        JSON.stringify(
          this.tasks.map((t) => ({
            title: t.title,
            description: t.description,
            correct_answer: t.correct_answer,
            files: t.files.map((f) => f.name),
          }))
        )
      );
      this.tasks.forEach((t, idx) =>
  t.files.forEach(f =>
    form.append("task_files", f, `${idx}__${f.name}`)
  )
);
const meta = this.tasks.map((t, idx) => ({
  ...t,
  files: t.files.map(f => `${idx}__${f.name}`)
}));
form.append("tasks_meta", JSON.stringify(meta));


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
  background: #115544;
  color: white;
  padding: 10px 18px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
</style>
