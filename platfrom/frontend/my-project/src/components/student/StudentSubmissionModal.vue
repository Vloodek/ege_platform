<template>
    <div class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <h2>{{ submission ? "Редактировать ответ" : "Добавить ответ" }}</h2>
  
        <!-- Существующие файлы -->
        <div v-if="existingSubmissionFiles.length">
          <p>Прикрепленные файлы:</p>
          <ul>
            <li v-for="(file, index) in existingSubmissionFiles" :key="index">
              <a :href="getFileUrl(file)" target="_blank">{{ getFileName(file) }}</a>
              <button type="button" class="remove-btn" @click="removeSubmissionFile(index)">❌</button>
            </li>
          </ul>
        </div>
  
        <!-- Новые файлы -->
        <div v-if="uploadedFiles.length">
          <p>Новые файлы:</p>
          <ul>
            <li v-for="(file, index) in uploadedFiles" :key="index">
              📄 {{ file.name }}
              <button type="button" class="remove-btn" @click="removeUploadedFile(index)">❌</button>
            </li>
          </ul>
        </div>
  
        <h3>Комментарий или ответ:</h3>
        <textarea v-model="responseText" placeholder="Введите ваш ответ..."></textarea>
  
        <h3>Прикрепить файлы:</h3>
        <div class="file-drop-zone" @dragover.prevent @drop="handleDrop">
          <p>Перетащите файлы сюда или <span @click="selectFile">выберите файл</span></p>
          <input type="file" multiple ref="fileInput" @change="handleFileUpload" hidden />
        </div>
  
        <!-- Кнопки -->
        <div class="modal-actions">
          <BaseButton color="green" @click="submitResponse" :disabled="isSubmitting">
            {{ isSubmitting ? "Отправка..." : "Отправить" }}
          </BaseButton>
          <BaseButton color="red" @click="closeModal">Отмена</BaseButton>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import BaseButton from "@/components/UI/BaseButton.vue";
  import axios from "axios";
  
  export default {
    components: { BaseButton },
    props: {
      submission: Object,
      isOpen: Boolean,
    },
    data() {
      return {
        responseText: this.submission?.comment || "",
        uploadedFiles: [],
        existingSubmissionFiles: this.submission?.files || [],
        filesToDelete: [],
        isSubmitting: false, // Флаг для предотвращения двойной отправки
      };
    },
    watch: {
      submission(newVal) {
        if (newVal) {
          this.responseText = newVal.comment || "";
          this.existingSubmissionFiles = [...newVal.files];
          this.uploadedFiles = []; // Очищаем загруженные файлы при изменении submission
        }
      },
    },
    methods: {
      closeModal() {
        this.$emit("close");
      },
      selectFile() {
        this.$refs.fileInput.click();
      },
      handleFileUpload(event) {
        this.uploadedFiles.push(...event.target.files);
      },
      handleDrop(event) {
        event.preventDefault();
        if (event.dataTransfer.files.length) {
          this.uploadedFiles.push(...event.dataTransfer.files);
        }
      },
      async submitResponse() {
        if (this.isSubmitting) return;
        this.isSubmitting = true;
  
        if (!this.responseText && !this.uploadedFiles.length && !this.existingSubmissionFiles.length) {
          alert("Добавьте ответ или прикрепите файлы!");
          this.isSubmitting = false;
          return;
        }
  
        const formData = new FormData();
        formData.append("homework_id", this.$route.params.id);
  
        const userData = JSON.parse(localStorage.getItem("user"));
        if (!userData || !userData.userId) {
          alert("Ошибка: Не найден userId в localStorage");
          this.isSubmitting = false;
          return;
        }
  
        formData.append("user_id", userData.userId);
        formData.append("comment", this.responseText);
        formData.append("student_submission_time", new Date().toISOString());
  
        formData.append("existing_files", JSON.stringify(this.existingSubmissionFiles));
        formData.append("files_to_delete", JSON.stringify(this.filesToDelete));
  
        this.uploadedFiles.forEach(file => {
          formData.append("files", file);
        });
  
        try {
          let response;
          if (this.submission) {
            response = await axios.put(`http://localhost:8000/update_submission/${this.submission.id}`, formData, {
              headers: { "Content-Type": "multipart/form-data" },
            });
          } else {
            response = await axios.post("http://localhost:8000/submit_homework", formData, {
              headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` },
            });
          }
  
          if (response.status === 200 || response.status === 201) {
            alert("Ответ успешно отправлен!");
            this.$emit("responseSubmitted");
            this.closeModal();
          } else {
            alert("Ошибка при отправке ответа");
          }
        } catch (error) {
          console.error("Ошибка при отправке ответа:", error);
          alert("Ошибка при отправке ответа");
        } finally {
          this.isSubmitting = false;
        }
      },
      removeSubmissionFile(index) {
        const file = this.existingSubmissionFiles[index];
        this.filesToDelete.push(file);
        this.existingSubmissionFiles.splice(index, 1);
      },
      removeUploadedFile(index) {
        this.uploadedFiles.splice(index, 1);
      },
      getFileUrl(file) {
        return file ? `http://localhost:8000/${file.replace(/\\/g, "/")}` : "";
      },
      getFileName(file) {
        return file ? file.split("/").pop() : "";
      },
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
    justify-content: center;
    align-items: center;
  }
  .modal-content {
    background: white;
    padding: 20px;
    border-radius: 10px;
    width: 500px;
  }
  .modal-actions {
    display: flex;
    justify-content: space-between;
    margin-top: 20px;
  }
  .file-drop-zone {
    border: 2px dashed #1e9275;
    padding: 20px;
    text-align: center;
    cursor: pointer;
    border-radius: 5px;
  }
  .file-drop-zone:hover {
    background: rgba(30, 146, 117, 0.1);
  }
  h2, h3 {
    color: #1e9275; /* Зеленый цвет */
    font-weight: normal; /* Нежирный */
  }
  textarea {
    width: 100%;
    min-height: 100px;
    margin-top: 10px;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 5px;
  }
  </style>
  