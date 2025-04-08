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
  
          <!-- Описание задания с использованием Quill -->
          <section class="section-input">
            <label for="description">Описание задания:</label>
            <div ref="descriptionEditor" class="quill-editor"></div>
          </section>
  
          <!-- Прикрепить файлы -->
          <section class="section-input">
            <label>Прикрепить файлы:</label>
            <input type="file" multiple @change="handleTaskFileUpload" ref="taskFileInput" />
            <ul v-if="form.taskFiles.length">
              <li v-for="(file, index) in form.taskFiles" :key="index">
                {{ file.name }} <button @click="removeTaskFile(index)">Удалить</button>
              </li>
            </ul>
          </section>
  
          <!-- Прикрепить картинки -->
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
  
          <!-- Файлы решения -->
          <section class="section-input">
            <label>Прикрепить файлы решения:</label>
            <input type="file" multiple @change="handleSolutionFileUpload" ref="solutionFileInput" />
            <ul v-if="form.solution_files.length">
              <li v-for="(file, index) in form.solution_files" :key="index">
                {{ file.name }} <button @click="removeSolutionFile(index)">Удалить</button>
              </li>
            </ul>
          </section>
  
          <!-- Картинки решения -->
          <section class="section-input">
            <label>Прикрепить картинки решения:</label>
            <input type="file" multiple accept="image/*" @change="handleSolutionImageUpload" ref="solutionImageInput" />
            <ul v-if="form.solution_images.length">
              <li v-for="(file, index) in form.solution_images" :key="index">
                {{ file.name }} <button @click="removeSolutionImage(index)">Удалить</button>
              </li>
            </ul>
          </section>
  
          <!-- Ответ -->
          <section class="section-input">
            <label>Ответ:</label>
  
            <!-- Однострочный ответ -->
            <input v-if="isTextInput" type="text" v-model="form.answerText" />
  
            <!-- Таблица 2x1 -->
            <div v-if="isTableTwo">
              <input v-model="form.answerTable[0]" type="text" style="width: 60px;" />
              <input v-model="form.answerTable[1]" type="text" style="width: 60px;" />
            </div>
  
            <!-- Таблица 10x1 -->
            <div v-if="isTableTen">
              <div v-for="(val, index) in form.answerTable" :key="index">
                <input v-model="form.answerTable[index]" type="text" style="width: 60px; margin: 2px 0;" />
              </div>
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
      visible: {
        type: Boolean,
        default: true,
      },
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
          answerTable: [],
        },
        isLoading: false,
        descriptionEditor: null,
        solutionEditor: null,
      };
    },
    computed: {
      isTextInput() {
        return this.form.taskNumber >= 1 && this.form.taskNumber <= 16;
      },
      isTableTwo() {
        return [17, 26, 27].includes(this.form.taskNumber);
      },
      isTableTen() {
        return this.form.taskNumber === 25;
      },
    },
    watch: {
      "form.taskNumber"() {
        if (this.isTableTwo) {
          this.form.answerTable = ["", ""];
          this.form.answerText = "";
        } else if (this.isTableTen) {
          this.form.answerTable = Array(10).fill("");
          this.form.answerText = "";
        } else {
          this.form.answerText = "";
          this.form.answerTable = [];
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
    
    // Вставляем изображение в описание задания
    const range = this.descriptionEditor.getSelection();
    if (range) {
      this.descriptionEditor.insertEmbed(range.index, 'image', imageUrl);
    }

    // Добавляем файл в форму
    this.form.taskImages.push(file);
  }
},

handleSolutionImageUpload(event) {
  const files = event.target.files;
  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    const imageUrl = URL.createObjectURL(file);
    
    // Вставляем изображение в решение
    const range = this.solutionEditor.getSelection();
    if (range) {
      this.solutionEditor.insertEmbed(range.index, 'image', imageUrl);
    }

    // Добавляем файл в форму
    this.form.solution_images.push(file);
  }
}
,
      removeTaskImage(index) {
        this.form.taskImages.splice(index, 1);
      },
      handleSolutionFileUpload(event) {
        this.form.solution_files.push(...event.target.files);
      },
      removeSolutionFile(index) {
        this.form.solution_files.splice(index, 1);
      },
      removeSolutionImage(index) {
        this.form.solution_images.splice(index, 1);
      },
      async submitTask() {
        this.isLoading = true;
        const formData = new FormData();
        formData.append("task_number", this.form.taskNumber);
        formData.append("description", this.form.description);
        formData.append("solution_text", this.form.solution_text);
  
        // Тип ответа
        let answer_format = "text";
        if ([17, 26, 27].includes(this.form.taskNumber)) {
          answer_format = "table2";
        } else if (this.form.taskNumber === 25) {
          answer_format = "table10";
        }
        formData.append("answer_format", answer_format);
  
        // Ответ — один из двух форматов
        if (this.isTextInput) {
          formData.append("answer", this.form.answerText);
        } else {
          formData.append("answer", JSON.stringify(this.form.answerTable));
        }
        formData.append(
          "correct_answer",
          this.isTextInput ? this.form.answerText : JSON.stringify(this.form.answerTable)
        );
  
        // Файлы
        this.form.taskFiles.forEach(file => formData.append("taskFiles", file));
        this.form.taskImages.forEach(file => formData.append("taskImages", file));
        this.form.solution_files.forEach(file => formData.append("solution_files", file));
        this.form.solution_images.forEach(file => formData.append("solution_images", file));
  
        try {
          const response = await axios.post("http://localhost:8000/exam_tasks", formData, {
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
          answerTable: [],
        };
      },
      initEditors() {
  this.$nextTick(() => {
    const descriptionEditorElement = this.$refs.descriptionEditor;
    const solutionEditorElement = this.$refs.solutionEditor;

    if (descriptionEditorElement && solutionEditorElement) {
      const toolbarOptions = [
        [{ 'header': '1' }, { 'header': '2' }, { 'font': [] }],
        [{ 'list': 'ordered' }, { 'list': 'bullet' }],
        ['bold', 'italic', 'underline'],
        [{ 'align': [] }],
        ['link', 'image'],
      ];

      // Функция-обработчик для изображений
      const imageHandler = function() {
        const input = document.createElement('input');
        input.setAttribute('type', 'file');
        input.setAttribute('accept', 'image/*');
        input.click();

        input.onchange = async () => {
          const file = input.files[0];
          if (file) {
            // Создаем FormData и отправляем файл на сервер
            const formData = new FormData();
            formData.append("image", file); // убедитесь, что сервер принимает имя "image" или измените его под ваш эндпоинт

            try {
              const response = await axios.post("http://localhost:8000/upload_image", formData, {
                headers: {
                  "Content-Type": "multipart/form-data",
                  Authorization: `Bearer ${localStorage.getItem("access_token")}`,
                },
              });
              // Предполагается, что сервер возвращает JSON с полем image_url
              const imageUrl = response.data.image_url;

              const range = this.quill.getSelection();
              this.quill.insertEmbed(range.index, 'image', imageUrl);
            } catch (error) {
              console.error("Ошибка загрузки изображения:", error);
              alert("Ошибка загрузки изображения");
            }
          }
        };
      };

      // Инициализация редакторов с кастомным обработчиком
      this.descriptionEditor = new Quill(descriptionEditorElement, {
        theme: 'snow',
        modules: {
          toolbar: {
            container: toolbarOptions,
            handlers: {
              image: imageHandler,
            },
          },
        },
      });

      this.solutionEditor = new Quill(solutionEditorElement, {
        theme: 'snow',
        modules: {
          toolbar: {
            container: toolbarOptions,
            handlers: {
              image: imageHandler,
            },
          },
        },
      });

      // Обновление состояния формы при изменении содержимого редакторов
      this.descriptionEditor.on('text-change', () => {
        this.form.description = this.descriptionEditor.root.innerHTML;
      });

      this.solutionEditor.on('text-change', () => {
        this.form.solution_text = this.solutionEditor.root.innerHTML;
      });
    } else {
      console.error("Ошибка: не удалось найти элементы для инициализации Quill.");
    }
  });
}
,
    },
    mounted() {
      this.initEditors();
    },
  };
  </script>
  
  <style scoped>
  /* Основной контейнер */
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
  