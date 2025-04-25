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

        <!-- Описание задания с использованием Quill (без выбора шрифта) -->
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

        

        <hr />

        <!-- Текст решения с использованием Quill (без смены шрифта) -->
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
              class="table-row">
              <input v-model="form.answerTable[rowIndex][0]" 
                     type="text" 
                     :placeholder="form.tableMode === 'list' ? 'Ответ' : 'Найденное число'" 
                     class="table-input" />
              <input v-if="form.tableMode === 'table'" 
                     v-model="form.answerTable[rowIndex][1]" 
                     type="text" 
                     placeholder="Результат деления" 
                     class="table-input" />
              <button class="remove-row-btn" @click="removeRow(rowIndex)">Удалить</button>
            </div>
            <button v-if="form.answerTable.length < 20" class="add-row-btn" @click="addRow">Добавить строку</button>
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
        solution_text: "",
        solution_files: [],
        answerText: "",
        answerTableSimple: ["", ""],
        answerTable: [],
        tableMode: "list",
      },
      isLoading: false,
      descriptionEditor: null,
      solutionEditor: null,
    };
  },
  computed: {
    isTextInput() {
      return (
        (this.form.taskNumber >= 1 && this.form.taskNumber <= 16) ||
        (this.form.taskNumber >= 18 && this.form.taskNumber <= 24)
      );
    },
    isTableTwo() {
      return [17, 26, 27].includes(this.form.taskNumber);
    },
    isTableDynamic25() {
      return this.form.taskNumber === 25;
    },
  },
  watch: {
    "form.taskNumber"() {
      // Сброс ответных полей при смене типа задания
      this.form.answerText = "";
      this.form.answerTable = [];
      this.form.answerTableSimple = ["", ""];
    },
  },
  methods: {
    onClose() {
      this.$emit("close");
    },
    handleTaskFileUpload(e) {
      this.form.taskFiles.push(...e.target.files);
    },
    removeTaskFile(i) {
      this.form.taskFiles.splice(i, 1);
    },
    handleSolutionFileUpload(e) {
      this.form.solution_files.push(...e.target.files);
    },
    removeSolutionFile(i) {
      this.form.solution_files.splice(i, 1);
    },
    addRow() {
      this.form.answerTable.push(["", ""]);
    },
    removeRow(i) {
      this.form.answerTable.splice(i, 1);
    },
    async submitTask() {
      this.isLoading = true;
      const formData = new FormData();
      formData.append("task_number", this.form.taskNumber);
      formData.append("description", this.form.description);
      formData.append("solution_text", this.form.solution_text);

      let format = "text";
      if (this.isTableTwo) format = "table2";
      if (this.isTableDynamic25) {
        format = this.form.tableMode === "table" ? "tableDyn2Col" : "tableDyn1Col";
      }
      formData.append("answer_format", format);

      if (this.isTextInput) {
        formData.append("answer", this.form.answerText);
      } else if (this.isTableTwo) {
        formData.append("answer", JSON.stringify(this.form.answerTableSimple));
      } else {
        formData.append("answer", JSON.stringify(this.form.answerTable));
      }
      formData.append(
        "correct_answer",
        this.isTextInput
          ? this.form.answerText
          : JSON.stringify(this.isTableTwo ? this.form.answerTableSimple : this.form.answerTable)
      );

      this.form.taskFiles.forEach((f) => formData.append("taskFiles", f));
      this.form.solution_files.forEach((f) => formData.append("solution_files", f));

      try {
        const response = await this.$axios.post(
          "/exam_tasks/",
          formData,
          { headers: { "Content-Type": "multipart/form-data" } }
        );
        if (response.status === 200) {
          this.$emit("success", "Задание успешно добавлено");
          this.resetForm();
          this.onClose();
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
        solution_text: "",
        solution_files: [],
        answerText: "",
        answerTableSimple: ["", ""],
        answerTable: [],
        tableMode: "list",
      };
      if (this.descriptionEditor) this.descriptionEditor.setContents([]);
      if (this.solutionEditor) this.solutionEditor.setContents([]);
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
        if (range) {
          quill.insertEmbed(range.index, 'image', data.image_url);
        }
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
          this.uploadAndInsertImage(quill, file);
        }
      }
    },
    initEditors() {
      this.$nextTick(() => {
        const toolbar = [
          [{ header: [1, 2] }],
          [{ list: "ordered" }, { list: "bullet" }],
          ["bold", "italic", "underline"],
          [{ align: [] }],
          ["link", "image"],
        ];
        const vm = this;

        this.descriptionEditor = new Quill(this.$refs.descriptionEditor, {
          theme: "snow",
          modules: {
            toolbar: {
              container: toolbar,
              handlers: {
                image() {
                  const input = document.createElement("input");
                  input.type = "file";
                  input.accept = "image/*";
                  input.click();
                  input.onchange = () => {
                    const file = input.files[0];
                    vm.uploadAndInsertImage(this.quill, file);
                  };
                },
              },
            },
          },
        });
        this.solutionEditor = new Quill(this.$refs.solutionEditor, {
          theme: "snow",
          modules: {
            toolbar: {
              container: toolbar,
              handlers: {
                image() {
                  const input = document.createElement("input");
                  input.type = "file";
                  input.accept = "image/*";
                  input.click();
                  input.onchange = () => {
                    const file = input.files[0];
                    vm.uploadAndInsertImage(this.quill, file);
                  };
                },
              },
            },
          },
        });

        this.descriptionEditor.on("text-change", () => {
          this.form.description = this.descriptionEditor.root.innerHTML;
        });
        this.solutionEditor.on("text-change", () => {
          this.form.solution_text = this.solutionEditor.root.innerHTML;
        });

        this.descriptionEditor.root.addEventListener("paste", (e) =>
          this.handlePaste(e, this.descriptionEditor)
        );
        this.solutionEditor.root.addEventListener("paste", (e) =>
          this.handlePaste(e, this.solutionEditor)
        );
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
/* Заголовок модального окна */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #ddd;
  margin-bottom: 10px;
}
.modal-header h3 {
  margin: 0;
  color: #56AEF6;
}
/* Кнопка закрытия */
.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #56AEF6;
}

/* Основное тело */
.modal-body {
  padding: 10px 0;
}
.section-input {
  margin-bottom: 15px;
}
.section-input label {
  display: block;
  margin-bottom: 5px;
  color: #56AEF6;
}
/* Quill-редактор */
.quill-editor {
  height: 200px;
  border: 1px solid #ccc;
  border-radius: 5px;
  background-color: #fafafa;
}

/* Файловый инпут (оставляем только для файлов, картинки убраны) */
input[type="file"] {
  display: block;
  margin-top: 5px;
}

/* Стили для ссылок на файлы с иконкой */
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
  color: #56AEF6;
}
.answer-input input[type="text"] {
  max-width: 300px;
  width: 100%;
  padding: 8px;
  border: 1px solid #56AEF6;
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
  border: 1px solid #56AEF6;
  border-radius: 3px;
}

/* Кнопки */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 15px;
}
.save-btn {
  padding: 8px 16px;
  background: #56AEF6;
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
.save-btn:disabled {
  background: #aaa;
  cursor: not-allowed;
}
.cancel-btn {
  padding: 8px 16px;
  background: #f44336;
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

/* Дополнительные стили для Quill-кода, если необходимо */
.ql-editor pre,
.ql-editor code {
  max-width: 100%;
  overflow-x: auto !important;
  white-space: pre-wrap !important;
  word-break: break-all !important;
}
</style>
