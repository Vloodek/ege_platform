<template>
  <div class="modal-overlay" @click.self="close">
    <div class="modal-content">
      <div class="modal-header">
        <h3>Детали отклика</h3>
        <button class="close-btn" @click="close">&times;</button>
      </div>
      <div class="modal-body">
        <!-- Блок с данными отклика студента -->
        <div class="student-section">
          <h4>Отклик студента</h4>
          <p><strong>Имя:</strong> {{ submission.name }}</p>
          <p><strong>Email:</strong> {{ submission.email }}</p>
          <p>
            <strong>Статус:</strong>
            {{ submission.status === 'submitted' ? 'Отправлено' : 'Не отправлено' }}
          </p>
          <p><strong>Время отправки:</strong> {{ formatDate(submission.submission_date) }}</p>
          <p><strong>Время изменения:</strong> {{ formatDate(submission.client_submission_time) }}</p>
          <p><strong>Комментарий студента:</strong></p>
          <p>{{ submission.comment }}</p>
          <div v-if="submission.files && submission.files.length">
            <p><strong>Прикреплённые файлы:</strong></p>
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
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="save-btn" @click="submitEvaluation">Сохранить оценку</button>
        <button class="close-btn" @click="close">Закрыть</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'SubmissionDetailsModal',
  props: {
    submission: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      grade: '',
      teacherResponse: '',
    };
  },
  methods: {
    close() {
      this.$emit('close');
    },
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleString('ru-RU', {
        day: '2-digit',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    },
    getFileUrl(file) {
      if (!file) return '';
      if (typeof file === 'string') {
        return `http://localhost:8000/${file.replace(/\\/g, '/')}`;
      }
      return file.url || '';
    },
    getFileName(file) {
      if (!file) return '';
      if (typeof file === 'string') {
        return file.split('/').pop();
      }
      return file.url ? file.url.split('/').pop() : (file.file ? file.file.name : '');
    },
    async submitEvaluation() {
      // Формируем объект с оценкой и ответом преподавателя
      const payload = {
        grade: this.grade,
        teacher_response: this.teacherResponse,
      };

      try {
        // Отправляем PUT-запрос для обновления отклика (эндпоинт должен поддерживать обновление оценки)
        const response = await axios.put(
          `http://localhost:8000/update_submission/${this.submission.id}`,
          payload,
          { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` } }
        );
        if (response.status === 200) {
          alert('Оценка успешно сохранена!');
          this.close();
        } else {
          alert('Ошибка при сохранении оценки');
        }
      } catch (error) {
        console.error('Ошибка при сохранении оценки:', error);
        alert('Ошибка при сохранении оценки');
      }
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
.modal-header h3 {
  margin: 0;
  font-size: 20px;
  color: #115544;
}
.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #115544;
}
.modal-body {
  margin-bottom: 10px;
}
.modal-body p {
  margin: 10px 0;
  font-size: 16px;
}
.student-section, .evaluation-section {
  margin-bottom: 15px;
}
.student-section h4, .evaluation-section h4 {
  font-size: 18px;
  color: #115544;
  margin-bottom: 10px;
  border-bottom: 1px solid #ddd;
  padding-bottom: 5px;
}
.evaluation-fields label {
  display: block;
  margin-top: 10px;
  font-weight: bold;
  font-size: 14px;
  color: #333;
}
.evaluation-fields input,
.evaluation-fields textarea {
  width: 100%;
  padding: 8px;
  font-size: 14px;
  border: 1px solid #ddd;
  border-radius: 5px;
  margin-top: 5px;
}
.modal-footer {
  text-align: right;
  margin-top: 15px;
}
.save-btn {
  background-color: #115544;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  margin-right: 10px;
}
.save-btn:hover {
  background-color: #1e9275;
}
.close-btn {
  background-color: #ccc;
  color: #333;
  padding: 8px 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
.close-btn:hover {
  background-color: #aaa;
}
.file-preview {
  max-width: 100px;
  max-height: 100px;
  cursor: pointer;
  border: 1px solid #ddd;
  border-radius: 5px;
  margin-top: 5px;
}
</style>
