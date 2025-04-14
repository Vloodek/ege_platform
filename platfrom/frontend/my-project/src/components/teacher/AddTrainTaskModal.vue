<template>
  <div class="modal-overlay" v-if="visible">
    <div class="modal-content">
      <div class="modal-header">
        <h3>Добавить тестовое задание</h3>
        <button class="close-btn" @click="onClose">&times;</button>
      </div>

      <div class="modal-body">
        <!-- Номер задания -->
        <section class="section-input">
          <label for="taskNumber">Номер задания:</label>
          <select v-model="form.taskNumber">
            <option v-for="n in 27" :key="n" :value="n">Задание {{ n }}</option>
          </select>
        </section>

        <!-- Если задание №25, показываем выбор режима динамической таблицы -->
        <section class="section-input" v-if="isTableDynamic25">
          <label>Тип таблицы:</label>
          <select v-model="form.tableMode">
            <option value="list">Один столбец (список)</option>
            <option value="table">Два столбца (таблица)</option>
          </select>
        </section>

        <!-- Описание задания с использованием Quill -->
        <section class="section-input">
          <label for="description">Описание задания:</label>
          <div ref="descriptionEditor" class="quill-editor"></div>
        </section>

        <!-- Прикрепить файлы задания -->
        <section class="section-input">
          <label>Прикрепить файлы:</label>
          <input type="file" multiple @change="handleTaskFileUpload" ref="taskFileInput" />
          <ul v-if="form.taskFiles.length">
            <li v-for="(file, index) in form.taskFiles" :key="index">
              {{ file.name }} <button @click="removeTaskFile(index)">Удалить</button>
            </li>
          </ul>
        </section>

        <!-- Прикрепить картинки задания -->
        <section class="section-input">
          <label>Прикрепить картинки:</label>
          <input type="file" multiple accept="image/*" @change="handleTaskImageUpload" ref="taskImageInput" />
          <ul v-if="form.taskImages.length">
            <li v-for="(file, index) in form.taskImages" :key="index">
              {{ file.name }} <button @click="removeTaskImage(index)">Удалить</button>
            </li>
          </ul>
        </section>

        <hr />

        <!-- Текст решения с использованием Quill -->
        <section class="section-input">
          <label for="solutionText">Текст решения:</label>
          <div ref="solutionEditor" class="quill-editor"></div>
        </section>

        <!-- Прикрепить файлы решения -->
        <section class="section-input">
          <label>Прикрепить файлы решения:</label>
          <input type="file" multiple @change="handleSolutionFileUpload" ref="solutionFileInput" />
          <ul v-if="form.solution_files.length">
            <li v-for="(file, index) in form.solution_files" :key="index">
              {{ file.name }} <button @click="removeSolutionFile(index)">Удалить</button>
            </li>
          </ul>
        </section>

        <!-- Прикрепить картинки решения -->
        <section class="section-input">
          <label>Прикрепить картинки решения:</label>
          <input type="file" multiple accept="image/*" @change="handleSolutionImageUpload" ref="solutionImageInput" />
          <ul v-if="form.solution_images.length">
            <li v-for="(file, index) in form.solution_images" :key="index">
              {{ file.name }} <button @click="removeSolutionImage(index)">Удалить</button>
            </li>
          </ul>
        </section>

        <!-- Блок для ввода ответа -->
        <section class="section-input">
          <label>Ответ:</label>
          <!-- Для текстовых заданий: 1–16 и 18–24 -->
          <input v-if="isTextInput" type="text" v-model="form.answerText" />
          
          <!-- Для заданий с таблицей из двух ячеек (например, 17, 26, 27) -->
          <div v-if="isTableTwo">
            <input v-model="form.answerTableSimple[0]" type="text" placeholder="Ячейка 1" style="width: 60px;" />
            <input v-model="form.answerTableSimple[1]" type="text" placeholder="Ячейка 2" style="width: 60px;" />
          </div>
          
          <!-- Для задания 25 – динамическая таблица -->
          <div v-if="isTableDynamic25">
            <div 
              v-for="(row, rowIndex) in form.answerTable" 
              :key="rowIndex" 
              style="display: flex; gap: 10px; margin-bottom: 5px;">
              <input v-model="form.answerTable[rowIndex][0]" 
                     type="text" 
                     :placeholder="form.tableMode === 'list' ? 'Ответ' : 'Найденное число'" 
                     style="width: 120px;" />
              <input v-if="form.tableMode === 'table'" 
                     v-model="form.answerTable[rowIndex][1]" 
                     type="text" 
                     placeholder="Результат деления" 
                     style="width: 120px;" />
              <button @click="removeRow(rowIndex)">Удалить</button>
            </div>
            <button v-if="form.answerTable.length < 20" @click="addRow">Добавить строку</button>
          </div>
        </section>
      </div>

      <div class="modal-footer">
        <button class="save-btn" @click="submitTask" :disabled="isLoading">
          {{ isLoading ? 'Сохранение...' : 'Сохранить задание' }}
        </button>
        <button class="cancel-btn" @click="onClose">Закрыть</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import Quill from "quill";
import "quill/dist/quill.snow.css";

export default {
  name: "AddTrainTaskModal",
  props: {
    visible: { type: Boolean, default: true },
  },
  data() {
    return {
      form: {
        taskNumber: 1,
        description: "",
        taskFiles: [],
        taskImages: [],
        solution_text: "",
        solution_files: [],
        solution_images: [],
        answerText: "",
        // Для заданий 17,26,27 – простая таблица из 2 ячеек:
        answerTableSimple: ["", ""],
        // Для задания 25 – динамическая таблица (каждая строка — массив из 2 элементов)
        answerTable: [],
        tableMode: "list", // "list" (один столбец) или "table" (два столбца)
      },
      isLoading: false,
      descriptionEditor: null,
      solutionEditor: null,
    };
  },
  computed: {
    // Текстовый ответ для заданий: 1–16 и 18–24
    isTextInput() {
      return (
        (this.form.taskNumber >= 1 && this.form.taskNumber <= 16) ||
        (this.form.taskNumber >= 18 && this.form.taskNumber <= 24)
      );
    },
    // Таблица с 2 ячейками для заданий 17,26,27
    isTableTwo() {
      return [17, 26, 27].includes(this.form.taskNumber);
    },
    // Динамическая таблица для задания 25
    isTableDynamic25() {
      return this.form.taskNumber === 25;
    },
  },
  watch: {
    "form.taskNumber"() {
      if (this.isTableTwo) {
        this.form.answerText = "";
        this.form.answerTableSimple = ["", ""];
        this.form.answerTable = [];
      } else if (this.isTableDynamic25) {
        this.form.answerText = "";
        this.form.answerTable = [];
      } else {
        this.form.answerText = "";
        this.form.answerTable = [];
        this.form.answerTableSimple = ["", ""];
      }
    },
  },
  methods: {
    onClose() {
      this.$emit("close");
    },
    handleTaskFileUpload(event) {
      this.form.taskFiles.push(...event.target.files);
    },
    removeTaskFile(index) {
      this.form.taskFiles.splice(index, 1);
    },
    handleTaskImageUpload(event) {
      const files = event.target.files;
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const imageUrl = URL.createObjectURL(file);
        const range = this.descriptionEditor.getSelection();
        if (range) {
          this.descriptionEditor.insertEmbed(range.index, "image", imageUrl);
        }
        this.form.taskImages.push(file);
      }
    },
    removeTaskImage(index) {
      this.form.taskImages.splice(index, 1);
    },
    handleSolutionFileUpload(event) {
      this.form.solution_files.push(...event.target.files);
    },
    removeSolutionFile(index) {
      this.form.solution_files.splice(index, 1);
    },
    handleSolutionImageUpload(event) {
      const files = event.target.files;
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const imageUrl = URL.createObjectURL(file);
        const range = this.solutionEditor.getSelection();
        if (range) {
          this.solutionEditor.insertEmbed(range.index, "image", imageUrl);
        }
        this.form.solution_images.push(file);
      }
    },
    removeSolutionImage(index) {
      this.form.solution_images.splice(index, 1);
    },
    addRow() {
      this.form.answerTable.push(["", ""]);
    },
    removeRow(rowIndex) {
      this.form.answerTable.splice(rowIndex, 1);
    },
    async submitTask() {
      this.isLoading = true;
      const formData = new FormData();
      formData.append("task_number", this.form.taskNumber);
      formData.append("description", this.form.description);
      formData.append("solution_text", this.form.solution_text);

      let answer_format = "text";
      if (this.isTableTwo) {
        answer_format = "table2";
      } else if (this.isTableDynamic25) {
        answer_format = this.form.tableMode === "table" ? "tableDyn2Col" : "tableDyn1Col";
      }
      formData.append("answer_format", answer_format);

      if (this.isTextInput) {
        formData.append("answer", this.form.answerText);
      } else if (this.isTableTwo) {
        formData.append("answer", JSON.stringify(this.form.answerTableSimple));
      } else if (this.isTableDynamic25) {
        formData.append("answer", JSON.stringify(this.form.answerTable));
      }
      formData.append(
        "correct_answer",
        this.isTextInput
          ? this.form.answerText
          : JSON.stringify(this.isTableTwo ? this.form.answerTableSimple : this.form.answerTable)
      );

      this.form.taskFiles.forEach((file) => formData.append("taskFiles", file));
      this.form.taskImages.forEach((file) => formData.append("taskImages", file));
      this.form.solution_files.forEach((file) => formData.append("solution_files", file));
      this.form.solution_images.forEach((file) => formData.append("solution_images", file));

      try {
        const response = await axios.post("http://localhost:8000/exam_tasks/", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        });
        if (response.status === 200) {
          this.$emit("success", "Задание успешно добавлено");
          this.resetForm();
          this.$emit("close");
        }
      } catch (error) {
        console.error("Ошибка при сохранении задания:", error);
        alert("Ошибка при сохранении задания");
      } finally {
        this.isLoading = false;
      }
    },
    resetForm() {
      this.form = {
        taskNumber: 1,
        description: "",
        taskFiles: [],
        taskImages: [],
        solution_text: "",
        solution_files: [],
        solution_images: [],
        answerText: "",
        answerTableSimple: ["", ""],
        answerTable: [],
        tableMode: "list",
      };
    },
    async uploadAndInsertImage(quill, file) {
      const formData = new FormData();
      formData.append("image", file);
      try {
        const response = await axios.post("http://localhost:8000/upload_temp_image", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        });
        const imageUrl = response.data.image_url;
        const range = quill.getSelection();
        if (range) {
          const imgHtml = `<img src="${imageUrl}" alt="${file.name}" />`;
          quill.clipboard.dangerouslyPasteHTML(range.index, imgHtml);
        }
      } catch (error) {
        console.error("Ошибка загрузки изображения:", error);
        alert("Ошибка загрузки изображения");
      }
    },
    handlePaste(e, quill) {
      const clipboardData = e.clipboardData || window.clipboardData;
      if (!clipboardData) return;
      const items = clipboardData.items;
      if (!items) return;
      for (let i = 0; i < items.length; i++) {
        const item = items[i];
        if (item.type.indexOf("image") !== -1) {
          e.preventDefault();
          const file = item.getAsFile();
          if (file) {
            this.uploadAndInsertImage(quill, file);
          }
        }
      }
    },
    initEditors() {
      this.$nextTick(() => {
        const descriptionEditorElement = this.$refs.descriptionEditor;
        const solutionEditorElement = this.$refs.solutionEditor;
        if (!descriptionEditorElement || !solutionEditorElement) {
          console.error("Ошибка: не найдены элементы для Quill.");
          return;
        }
        const toolbarOptions = [
          [{ header: "1" }, { header: "2" }, { font: [] }],
          [{ list: "ordered" }, { list: "bullet" }],
          ["bold", "italic", "underline"],
          [{ align: [] }],
          ["link", "image"]
        ];

        const vm = this;
        const customImageHandler = async function () {
          const quill = this.quill;
          const input = document.createElement("input");
          input.setAttribute("type", "file");
          input.setAttribute("accept", "image/*");
          input.click();
          input.onchange = async () => {
            const file = input.files[0];
            if (file) {
              vm.uploadAndInsertImage(quill, file);
            }
          };
        };

        this.descriptionEditor = new Quill(descriptionEditorElement, {
          theme: "snow",
          modules: {
            toolbar: {
              container: toolbarOptions,
              handlers: { image: function () { customImageHandler.call(this); } }
            }
          }
        });

        this.solutionEditor = new Quill(solutionEditorElement, {
          theme: "snow",
          modules: {
            toolbar: {
              container: toolbarOptions,
              handlers: { image: function () { customImageHandler.call(this); } }
            }
          }
        });

        this.descriptionEditor.root.addEventListener("paste", (e) => {
          this.handlePaste(e, this.descriptionEditor);
        });
        this.solutionEditor.root.addEventListener("paste", (e) => {
          this.handlePaste(e, this.solutionEditor);
        });

        this.descriptionEditor.on("text-change", () => {
          this.form.description = this.descriptionEditor.root.innerHTML;
        });
        this.solutionEditor.on("text-change", () => {
          this.form.solution_text = this.solutionEditor.root.innerHTML;
        });
      });
    },
  },
  mounted() {
    this.initEditors();
  },
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}
.modal-content {
  background: #fff;
  border-radius: 10px;
  width: 95%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 20px;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.3);
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #ddd;
  margin-bottom: 10px;
}
.modal-body {
  padding: 10px 0;
}
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
}
.section-input {
  margin-bottom: 15px;
}
.quill-editor {
  height: 200px;
  border: 1px solid #ccc;
  border-radius: 5px;
}
.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}
.save-btn {
  padding: 8px 16px;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
.cancel-btn {
  padding: 8px 16px;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
.save-btn:disabled {
  background: #aaa;
  cursor: not-allowed;
}
</style>
