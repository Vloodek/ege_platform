<template>
  <div class="modal-overlay" @click.self="close">
    <div class="modal-content">
      <div class="modal-header">
        <h3>{{ submission.user_name }}</h3>
        <button class="close-btn" @click="close">&times;</button>
      </div>
      <div class="modal-body">
        <!-- Блок с данными отклика студента -->
        <div class="student-section">
          <p><span class="green-text">Статус:</span> {{ submission.status === 'submitted' ? 'Отправлено' : 'Не отправлено' }}</p>
          <p v-if="submission.submission_date">
            <span class="green-text">Время отправки:</span> {{ formatDate(submission.submission_date) }}
          </p>
          <p v-if="submission.client_submission_time">
            <span class="green-text">Время изменения:</span> {{ formatDate(submission.client_submission_time) }}
          </p>
          <p><span class="green-text">Комментарий студента:</span></p>
          <p>{{ submission.comment || 'Нет комментария' }}</p>

          <div v-if="submission.files && submission.files.length">
            <p><span class="green-text">Прикреплённые файлы:</span></p>
            <ul>
              <li v-for="(file, index) in submission.files" :key="index">
                📄 <a :href="getFileUrl(file)" target="_blank">{{ getFileName(file) }}</a>
              </li>
            </ul>
          </div>
        </div>

        <hr />

        <!-- Блок для оценки преподавателя -->
        <div class="evaluation-section">
          <h4>Оценка преподавателя</h4>
          <div class="evaluation-fields">
            <label for="grade">Оценка:</label>
            <!-- Поле больше не блокируется даже если оценка уже установлена -->
            <input id="grade" v-model="grade" type="number" min="0" max="100" placeholder="Введите оценку" />

            <label for="teacherResponse">Комментарий преподавателя:</label>
            <textarea id="teacherResponse" v-model="teacherResponse" placeholder="Введите комментарий"></textarea>

            <label for="fileInput">Прикрепить файлы:</label>
            <input type="file" multiple @change="handleFileUpload" ref="fileInput" />

            <div v-if="uploadedFiles.length">
              <p><span class="green-text">Файлы, ожидающие загрузки:</span></p>
              <ul>
                <li v-for="(file, index) in uploadedFiles" :key="index">
                  📄 {{ file.name }}
                  <button class="delete-btn" @click="removeUploadedFile(index)">❌</button>
                </li>
              </ul>
            </div>

            <div v-if="teacherResponseFiles.length">
              <p><span class="green-text">Файлы преподавателя:</span></p>
              <ul>
                <li v-for="(file, index) in teacherResponseFiles" :key="index">
                  📄 <a :href="getFileUrl(file.file_path)" target="_blank">{{ file.file_name }}</a>
                  <button class="delete-btn" @click="deleteFile(file)">❌</button>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="save-btn" @click="submitEvaluation" :disabled="isLoading">
          {{ isLoading ? 'Сохранение...' : 'Сохранить оценку' }}
        </button>
        <button class="close-btn" @click="close">Закрыть</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "SubmissionDetailsModal",
  props: {
    submission: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      grade: "",
      teacherResponse: "",
      uploadedFiles: [],
      teacherResponseFiles: [],
      filesToDelete: [],
      isLoading: false,
    };
  },
  methods: {
    close() {
      this.$emit("close");
      this.resetData();
    },
    resetData() {
      this.grade = "";
      this.teacherResponse = "";
      this.uploadedFiles = [];
      this.filesToDelete = [];
    },
    formatDate(dateString) {
      if (!dateString) return "—";
      return new Date(dateString).toLocaleString("ru-RU", {
        day: "2-digit",
        month: "long",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    },
    getFileUrl(file) {
      if (!file) return "#";
      const filePath = typeof file === "string" ? file : file.file_path;
      return `http://localhost:8000/${filePath.replace(/\\/g, "/")}`;
    },
    getFileName(file) {
      if (!file) return "Файл";
      return typeof file === "string" ? file.split("\\").pop() : file.file_name;
    },
    handleFileUpload(event) {
      this.uploadedFiles.push(...event.target.files);
    },
    removeUploadedFile(index) {
      this.uploadedFiles.splice(index, 1);
    },
    async loadTeacherResponse() {
      try {
        const response = await axios.get(
          `http://localhost:8000/teacher_response/${this.submission.id}`,
          {
            headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` },
          }
        );
        this.teacherResponse = response.data.teacher_comment;
        // Если значение teacher_grade не равно null, преобразуем его в строку для корректного отображения
        this.grade = response.data.teacher_grade !== null ? response.data.teacher_grade.toString() : "";
        this.teacherResponseFiles = response.data.files || [];
      } catch (error) {
        console.error("Ошибка загрузки отклика преподавателя:", error);
      }
    },
    async deleteFile(file) {
      this.filesToDelete.push(file.file_path);
      this.teacherResponseFiles = this.teacherResponseFiles.filter(
        (f) => f.file_path !== file.file_path
      );
    },
    async submitEvaluation() {
      this.isLoading = true;
      const formData = new FormData();
      formData.append("teacher_comment", this.teacherResponse);
      
      // Добавляем оценку, только если поле не пустое
      if (this.grade !== "") {
        formData.append("teacher_grade", this.grade);
      }
      
      formData.append("files_to_delete", JSON.stringify(this.filesToDelete));
      this.uploadedFiles.forEach((file) => formData.append("files", file));

      try {
        const response = await axios.put(
          `http://localhost:8000/update_teacher_response/${this.submission.id}`,
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
              Authorization: `Bearer ${localStorage.getItem("access_token")}`,
            },
          }
        );

        if (response.status === 200) {
          this.$emit("success", "Оценка успешно сохранена!");
          this.close();
        }
      } catch (error) {
        console.error("Ошибка при сохранении оценки:", error);
        alert("Ошибка при сохранении оценки");
      } finally {
        this.isLoading = false;
      }
    },
  },
  mounted() {
    this.loadTeacherResponse();
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
  z-index: 1000;
}
.modal-content {
  background: #fff;
  border-radius: 10px;
  width: 90%;
  max-width: 500px;
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
.modal-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 15px;
}
.save-btn {
  background-color: #28a745;
  color: white;
  padding: 8px 16px;
  border: none;
  cursor: pointer;
  border-radius: 5px;
}
.close-btn {
  background-color: #dc3545;
  color: white;
  padding: 8px 16px;
  border: none;
  cursor: pointer;
  border-radius: 5px;
}
.green-text {
  color: #115544;
}
.delete-btn {
  background: none;
  border: none;
  color: red;
  cursor: pointer;
  font-size: 14px;
}
</style>
