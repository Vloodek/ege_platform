<template>
  <div class="edit-homework-page">
    <div class="container">
      <SideBar :isTestActive="false" />

      <div class="main-content">
        <div class="header">
          <div class="back-arrow" @click="confirmExit"></div>
          <h1 class="edit-title">Редактирование домашнего задания</h1>
        </div>

        <form @submit.prevent="handleSubmit" class="homework-form">
          <div class="form-group">
            <label for="homeworkTitle">Название задания</label>
            <input
              type="text"
              id="homeworkTitle"
              v-model="homework.title"
              placeholder="Введите название задания"
              required
            />
          </div>

          <div class="form-group">
            <label for="homeworkText">Текст задания</label>
            <div ref="homeworkEditor" class="quill-editor"></div>
          </div>

          <div class="form-group">
            <label for="homeworkFiles">Файлы</label>
            <input
              type="file"
              id="homeworkFiles"
              @change="handleFileUpload"
              multiple
              accept="application/pdf"
            />
            <div v-if="homework.files.length">
              <p>Прикрепленные файлы:</p>
              <ul>
                <li v-for="(file, index) in homework.files" :key="index">
                  {{ file.name || file }}
                  <button type="button" @click="removeFile(index)">Удалить</button>
                </li>
              </ul>
            </div>
          </div>

          <div class="form-group">
            <label for="homeworkDate">Дедлайн</label>
            <input
              type="datetime-local"
              id="homeworkDate"
              v-model="homework.date"
              required
            />
          </div>

          <button type="submit" class="submit-btn">Сохранить изменения</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import SideBar from "./SideBar.vue";
import Quill from "quill";
import "quill/dist/quill.snow.css";

export default {
  name: "EditHomeworkPage",
  components: { SideBar },
  data() {
    return {
      homework: {
        id: "",
        lessonId: "",
        title: "",
        text: "",
        date: "",
        files: [],
      },
      existingFiles: [],
      homeworkEditor: null,
    };
  },
  async created() {
  const homeworkId = this.$route.params.id;
  try {
    const { data } = await this.$axios.get(`/homework/${homeworkId}`);

    this.homework.id = data.id;
    this.homework.lessonId = data.lesson_id;
    this.homework.title = data.description;
    this.homework.text = data.text;
    this.homework.date = data.date;
    this.existingFiles = data.files || [];
    this.homework.files = [...this.existingFiles];

    // Инициализируем редактор только после загрузки данных
    if (!this.homeworkEditor) {
      this.initEditor();
    }
  } catch (err) {
    console.error("Ошибка загрузки ДЗ:", err);
  }
},
  methods: {
    initEditor() {
      this.$nextTick(() => {
        const toolbarOptions = [
          [{ header: "1" }, { header: "2" }],
          [{ list: "ordered" }, { list: "bullet" }],
          ["bold", "italic", "underline"],
          [{ align: [] }],
          ["link", "image"],
        ];
        const editor = new Quill(this.$refs.homeworkEditor, {
          theme: "snow",
          modules: {
            toolbar: {
              container: toolbarOptions,
              handlers: {
                image: this.imageUploadHandler,
              },
            },
          },
        });
        editor.root.innerHTML = this.homework.text || "";
        editor.on("text-change", () => {
          this.homework.text = editor.root.innerHTML;
        });
        this.homeworkEditor = editor;
      });
    },
    async imageUploadHandler() {
      const input = document.createElement("input");
      input.type = "file";
      input.accept = "image/*";
      input.click();
      input.onchange = async () => {
        const file = input.files[0];
        const formData = new FormData();
        formData.append("image", file);
        try {
          const res = await this.$axios.post("/upload_temp_image", formData);

          const imageUrl = res.data.image_url;
          const range = this.homeworkEditor.getSelection();
          this.homeworkEditor.clipboard.dangerouslyPasteHTML(
            range.index,
            `<img src="${imageUrl}" alt="img"/>`
          );
        } catch (err) {
          alert("Ошибка загрузки изображения");
        }
      };
    },
    handleFileUpload(event) {
      const files = Array.from(event.target.files);
      files.forEach(file => {
        if (file.type === "application/pdf") {
          this.homework.files.push(file);
        } else {
          alert("Только PDF файлы.");
        }
      });
    },
    removeFile(index) {
      this.homework.files.splice(index, 1);
    },
    confirmExit() {
      if (confirm("Вы уверены, что хотите выйти без сохранения?")) {
        this.$router.push(`/lesson/${this.homework.lessonId}/details`);
      }
    },
    async handleSubmit() {
      const formData = new FormData();
      formData.append("lesson_id", this.homework.lessonId);
      formData.append("description", this.homework.title);
      formData.append("text", this.homework.text);
      formData.append("date", this.homework.date);
      formData.append("existing_files", JSON.stringify(this.existingFiles));

      this.homework.files.forEach(file => {
        if (typeof file !== "string") {
          formData.append("files", file);
        }
      });

      try {
        await this.$axios.put(`/homeworks/${this.homework.id}`, formData, {

          headers: { "Content-Type": "multipart/form-data" },
        });
        this.$router.push(`/lesson/${this.homework.lessonId}/details`);
      } catch (err) {
        console.error("Ошибка при сохранении ДЗ:", err);
        alert("Ошибка при сохранении");
      }
    },
  },
};
</script>

<style scoped>
.edit-homework-page {
  display: flex;
  max-width: 1200px;
  margin: 0 auto;
  background-color: #f3f3f3;
  width: 100%;
}
.container {
  display: flex;
  flex-wrap: wrap;
  width: 100%;
  padding: 20px;
  background-color: #f3f3f3;
}
.main-content {
  flex: 1;
  margin-left: 20px;
  background-color: #ffffff;
  border-radius: 8px;
  padding: 20px;
  box-sizing: border-box;
  position: relative;
}
.header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  position: relative;
}
.back-arrow {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  background-color: #115544;
  clip-path: polygon(100% 0, 0 50%, 100% 100%);
  cursor: pointer;
}
.edit-title {
  flex: 1;
  text-align: center;
  font-size: 24px;
  color: #115544;
  font-weight: 500;
  margin: 0;
}
.form-group {
  margin-bottom: 15px;
}
.form-group label {
  display: block;
  font-size: 16px;
  margin-bottom: 5px;
  color: #333;
}
.form-group input,
.quill-editor {
  width: 100%;
  padding: 10px;
  font-size: 14px;
  border: 1px solid #ddd;
  border-radius: 5px;
  box-sizing: border-box;
}
.quill-editor {
  min-height: 200px;
}
.submit-btn {
  padding: 10px 20px;
  background-color: #115544;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  right: 20px;
  bottom: 20px;
}
.submit-btn:hover {
  background-color: #1e9275;
}
</style>
