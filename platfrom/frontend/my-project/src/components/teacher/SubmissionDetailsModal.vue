<template>
  <div class="modal-overlay" @click.self="close">
    <div class="modal-content">
      <div class="modal-header">
        <h3 class="modal-title">{{ submission.user_name }}</h3>
        <button class="btn-close" @click="close">&times;</button>
      </div>

      <div class="modal-body">
        <!-- Секция студента -->
        <section class="section student-section">
          <div class="form-row">
            <div class="form-group">
              <label>Статус</label>
              <div class="value">
                <span
                  :class="{
                    'status-badge': true,
                    submitted: submission.status === 'submitted',
                    waiting: submission.status !== 'submitted'
                  }"
                >
                  {{ submission.status === 'submitted' ? 'Отправлено' : 'Не отправлено' }}
                </span>
              </div>
            </div>
            <div class="form-group" v-if="submission.submission_date">
              <label>Время отправки</label>
              <div class="value">{{ formatDate(submission.submission_date) }}</div>
            </div>
            <div class="form-group" v-if="submission.client_submission_time">
              <label>Время изменения</label>
              <div class="value">{{ formatDate(submission.client_submission_time) }}</div>
            </div>
          </div>

          <div class="form-group full-width">
            <label>Комментарий студента</label>
            <p class="value">{{ submission.comment || '—' }}</p>
          </div>

          <div v-if="submission.files?.length" class="form-group full-width">
            <label>Прикреплённые файлы</label>
            <ul class="file-list">
              <li v-for="(file, i) in submission.files" :key="i">
                📄
                <a :href="getFileUrl(file)" target="_blank">{{ getFileName(file) }}</a>
              </li>
            </ul>
          </div>
        </section>

        <hr class="divider" />

        <!-- Секция преподавателя -->
        <section class="section eval-section">
          <h4>Оценка преподавателя</h4>
          <div class="form-row">
            <div class="form-group">
              <label for="grade">Оценка</label>
              <input
                id="grade"
                type="number"
                v-model="grade"
                min="0"
                max="100"
                placeholder="0–100"
              />
            </div>
            <div class="form-group full-width">
              <label for="teacherResponse">Комментарий</label>
              <textarea
                id="teacherResponse"
                v-model="teacherResponse"
                rows="3"
                placeholder="Ваш комментарий"
              ></textarea>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group full-width">
              <label>Новые файлы</label>
              <input ref="fileInput" type="file" multiple @change="handleFileUpload" />
              <ul class="file-list small">
                <li v-for="(f, i) in uploadedFiles" :key="i">
                  {{ f.name }}
                  <button class="btn-delete" @click="removeUploadedFile(i)">×</button>
                </li>
              </ul>
            </div>
          </div>

          <div v-if="teacherResponseFiles.length" class="form-row">
            <div class="form-group full-width">
              <label>Загруженные файлы</label>
              <ul class="file-list small">
                <li v-for="(f, i) in teacherResponseFiles" :key="i">
                  📄
                  <a :href="getFileUrl(f.file_path)" target="_blank">{{ f.file_name }}</a>
                  <button class="btn-delete" @click="deleteFile(f)">×</button>
                </li>
              </ul>
            </div>
          </div>
        </section>
      </div>

      <div class="modal-footer">
        <button class="btn btn-save" :disabled="isLoading" @click="submitEvaluation">
          {{ isLoading ? 'Сохранение...' : 'Сохранить' }}
        </button>
        <button class="btn btn-cancel" @click="close">Закрыть</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "SubmissionDetailsModal",
  props: { submission: { type: Object, required: true } },
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
  mounted() {
    this.loadTeacherResponse();
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
    formatDate(date) {
      if (!date) return "—";
      return new Date(date).toLocaleString("ru-RU", {
        day: "2-digit", month: "long", year: "numeric",
        hour: "2-digit", minute: "2-digit",
      });
    },
    getFileUrl(path) {
      const clean = (typeof path === "string" ? path : path.file_path)
        .replace(/\\/g, "/").replace(/^\//, "");
      return `${this.$axios.defaults.baseURL.replace(/\/$/, "")}/${clean}`;
    },
    getFileName(file) {
  if (typeof file === "string") {
    // Разделим строку пути по слешам и вернем последний элемент
    return file.split(/(\\|\/)/).pop();
  }
  return file.file_name || 'Без имени';
}
,
    handleFileUpload(e) {
      this.uploadedFiles.push(...e.target.files);
    },
    removeUploadedFile(i) {
      this.uploadedFiles.splice(i, 1);
    },
    async loadTeacherResponse() {
      try {
        const { data } = await this.$axios.get(`/teacher_response/${this.submission.id}`);
        this.teacherResponse = data.teacher_comment;
        this.grade = data.teacher_grade != null ? String(data.teacher_grade) : "";
        this.teacherResponseFiles = data.files || [];
      } catch (e) {
        console.error(e);
      }
    },
    deleteFile(f) {
      this.filesToDelete.push(f.file_path);
      this.teacherResponseFiles = this.teacherResponseFiles.filter(x => x.file_path !== f.file_path);
    },
    async submitEvaluation() {
      this.isLoading = true;
      const fd = new FormData();
      fd.append("teacher_comment", this.teacherResponse);
      if (this.grade !== "") fd.append("teacher_grade", this.grade);
      fd.append("files_to_delete", JSON.stringify(this.filesToDelete));
      this.uploadedFiles.forEach(f => fd.append("files", f));

      try {
        await this.$axios.put(`/update_teacher_response/${this.submission.id}`, fd, {
          headers: { "Content-Type": "multipart/form-data" }
        });
        this.$emit("success", "Оценка сохранена");
        this.close();
      } catch (e) {
        console.error(e);
        alert("Ошибка при сохранении");
      } finally {
        this.isLoading = false;
      }
    },
  },
};
</script>

<style scoped>
.modal-overlay {
  position: fixed; top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
}
.modal-content {
  background: #fff; border-radius: 8px;
  width: 90%; max-width: 600px; max-height: 90vh;
  display: flex; flex-direction: column;
  overflow: hidden;
}
.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 20px; border-bottom: 1px solid #eee;
}
.modal-title { margin: 0; font-size: 1.25rem; }
.btn-close {
  font-size: 1.5rem; background: none; border: none; cursor: pointer;
  line-height: 1; color: #333;
}
.modal-body {
  padding: 20px; overflow-y: auto; flex: 1;
}
.section {
  margin-bottom: 20px;
}
.divider {
  border: none; border-top: 1px solid #eee; margin: 0 20px;
}
.form-row {
  display: flex; flex-wrap: wrap; gap: 16px;
}
.form-group {
  flex: 1 1 200px; display: flex; flex-direction: column;
}
.form-group.full-width {
  flex: 1 1 100%;
}
.form-group label {
  font-weight: 600; margin-bottom: 4px; color: #444;
}
.form-group input,
.form-group textarea,
.form-group select {
  padding: 8px 10px; border: 1px solid #ccc; border-radius: 4px;
  font-size: 0.95rem; color: #333; resize: vertical;
}
.value {
  padding: 6px 8px; background: #f9f9f9; border-radius: 4px;
}
.status-badge {
  padding: 2px 8px; border-radius: 12px; font-size: 0.85rem;
}
.status-badge.submitted { background: #e0f7e9; color: #2d7a46; }
.status-badge.waiting { background: #fdecea; color: #a52a2a; }
.file-list {
  list-style: none; padding: 0; margin: 4px 0 0;
}
.file-list.small li {
  display: flex; align-items: center;
  font-size: 0.85rem; margin-top: 4px;
}
.file-list li a {
  color: #56aef6; text-decoration: none;
}
.btn-delete {
  margin-left: 8px; background: none; border: none; cursor: pointer;
  color: #c00; font-size: 1rem; line-height: 1;
}
.modal-footer {
  display: flex; justify-content: flex-end; gap: 12px;
  padding: 12px 20px; border-top: 1px solid #eee;
}
.btn {
  padding: 8px 16px; border-radius: 4px;
  font-size: 0.95rem; cursor: pointer; border: none;
}
.btn-save {
  background: #28a745; color: #fff;
}
.btn-cancel {
  background: #ccc; color: #333;
}
</style>
