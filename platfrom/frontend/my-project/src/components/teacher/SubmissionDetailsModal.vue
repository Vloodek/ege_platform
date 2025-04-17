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
          <p>
            <span class="green-text">Статус:</span>
            {{ submission.status === 'submitted' ? 'Отправлено' : 'Не отправлено' }}
          </p>
          <p v-if="submission.submission_date">
            <span class="green-text">Время отправки:</span>
            {{ formatDate(submission.submission_date) }}
          </p>
          <p v-if="submission.client_submission_time">
            <span class="green-text">Время изменения:</span>
            {{ formatDate(submission.client_submission_time) }}
          </p>
          <p><span class="green-text">Комментарий студента:</span></p>
          <p>{{ submission.comment || 'Нет комментария' }}</p>

          <div v-if="submission.files && submission.files.length">
            <p><span class="green-text">Прикреплённые файлы:</span></p>
            <ul>
              <li v-for="(file, index) in submission.files" :key="index">
                📄
                <a :href="getFileUrl(file)" target="_blank">
                  {{ getFileName(file) }}
                </a>
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
            <input
              id="grade"
              v-model="grade"
              type="number"
              min="0"
              max="100"
              placeholder="Введите оценку"
            />

            <label for="teacherResponse">Комментарий преподавателя:</label>
            <textarea
              id="teacherResponse"
              v-model="teacherResponse"
              placeholder="Введите комментарий"
            ></textarea>

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
                  📄
                  <a :href="getFileUrl(file.file_path)" target="_blank">
                    {{ file.file_name }}
                  </a>
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
      const path = typeof file === "string" ? file : file.file_path;
      const clean = path.replace(/\\/g, "/").replace(/^\//, "");
      const base = this.$axios.defaults.baseURL.replace(/\/$/, "");
      return `${base}/${clean}`;
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
        const { data } = await this.$axios.get(
          `/teacher_response/${this.submission.id}`
        );
        this.teacherResponse = data.teacher_comment;
        this.grade =
          data.teacher_grade != null ? String(data.teacher_grade) : "";
        this.teacherResponseFiles = data.files || [];
      } catch (error) {
        console.error("Ошибка загрузки отклика преподавателя:", error);
      }
    },
    deleteFile(file) {
      this.filesToDelete.push(file.file_path);
      this.teacherResponseFiles = this.teacherResponseFiles.filter(
        (f) => f.file_path !== file.file_path
      );
    },
    async submitEvaluation() {
      this.isLoading = true;
      const formData = new FormData();
      formData.append("teacher_comment", this.teacherResponse);
      if (this.grade !== "") {
        formData.append("teacher_grade", this.grade);
      }
      formData.append("files_to_delete", JSON.stringify(this.filesToDelete));
      this.uploadedFiles.forEach((f) => formData.append("files", f));

      try {
        const response = await this.$axios.put(
          `/update_teacher_response/${this.submission.id}`,
          formData,
          { headers: { "Content-Type": "multipart/form-data" } }
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
.modal-body {
  margin-bottom: 15px;
}
.modal-footer {
  display: flex;
  justify-content: space-between;
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
