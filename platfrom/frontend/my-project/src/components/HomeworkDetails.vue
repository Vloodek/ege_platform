<template>
  <div id="homework-details">
    <div class="container">
      <SideBar :isTestActive="false" />

      <main class="main-content">
        <div v-if="homework">
          <div class="header-section">
            <div class="back-arrow" @click="$router.go(-1)"></div>
            <h1 class="homework-title centered">
              {{ homework.description || "Детали домашнего задания" }}
            </h1>
          </div>

          <div class="homework-deadline">
            <strong>Дедлайн: </strong>{{ formatDate(homework.date) }}
          </div>

          <div v-if="homework.text" class="homework-description">
            <p>{{ homework.text }}</p>
          </div>

          <div v-if="homeworkImages.length" class="images-container">
            <div class="images">
              <img
                v-for="(image, index) in homeworkImages"
                :key="index"
                :src="getFileUrl(image)"
                alt="Homework Image"
                @click="openImage(getFileUrl(image))"
              />
            </div>
          </div>

          <div v-if="otherFiles.length" class="files-section">
            <ul>
              <li v-for="(file, index) in otherFiles" :key="index">
                <a :href="getFileUrl(file)" target="_blank">
                  <img src="@/assets/svg/files.svg" alt="file icon" class="file-icon" />
                  {{ getFileName(file) }}
                </a>
              </li>
            </ul>
          </div>

          <!-- Если преподаватель -->
          <div v-if="isTeacher" class="teacher-buttons">
            <BaseButton color="green" @click="goToEditHomework">Изменить ДЗ</BaseButton>
            <BaseButton color="white" @click="goToResponses">Отклики студентов</BaseButton>
          </div>

          <!-- Если студент -->
          <div v-if="!isTeacher && submission" class="submission-section">
            <h2>Ваш ответ:</h2>
            <p>{{ submission.comment }}</p>

            <div class="uploaded-files">
              <div v-for="(file, index) in submission.files" :key="index" class="uploaded-file">
                📄 <a :href="getFileUrl(file)" target="_blank">{{ getFileName(file) }}</a>
              </div>
            </div>

            <!-- Отклик преподавателя -->
            <div v-if="teacherResponse" class="teacher-response">
              <h3>Оценка преподавателя: {{ teacherResponse.teacher_grade || "Не выставлена" }}</h3>
              <p><strong>Комментарий:</strong> {{ teacherResponse.teacher_comment || "Нет комментария" }}</p>

              <div v-if="teacherResponse.files.length" class="teacher-files">
                <p><strong>Файлы преподавателя:</strong></p>
                <ul>
                  <li v-for="(file, index) in teacherResponse.files" :key="index">
                    📄 <a :href="getFileUrl(file.file_path)" target="_blank">{{ file.file_name }}</a>
                  </li>
                </ul>
              </div>
            </div>

            <BaseButton
              :color="teacherResponse?.teacher_grade ? 'gray' : 'green'"
              :disabled="!!teacherResponse?.teacher_grade"
              @click="openModal"
            >
              Редактировать ответ
            </BaseButton>
          </div>

          <div v-if="!isTeacher && !submission" class="no-submission">
            <BaseButton color="green" @click="openModal">Добавить ответ</BaseButton>
          </div>

          <StudentSubmissionModal
            v-if="isModalOpen"
            :isOpen="isModalOpen"
            :submission="submission"
            @close="closeModal"
            @responseSubmitted="fetchSubmission"
          />
        </div>

        <div v-else>
          <p>Загрузка задания...</p>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import SideBar from "../components/SideBar.vue";
import BaseButton from "@/components/UI/BaseButton.vue";
import StudentSubmissionModal from "@/components/student/StudentSubmissionModal.vue";
import axios from "axios";

export default {
  components: { SideBar, BaseButton, StudentSubmissionModal },
  data() {
    return {
      homework: null,
      submission: null,
      teacherResponse: null, // Данные отклика преподавателя
      isTeacher: false,
      isModalOpen: false,
    };
  },
  computed: {
    homeworkImages() {
      return Array.isArray(this.homework?.images) ? this.homework.images : [];
    },
    otherFiles() {
      return Array.isArray(this.homework?.files)
        ? this.homework.files.filter(file => !/\.(jpg|jpeg|png|gif)$/i.test(file))
        : [];
    },
  },
  async created() {
    await this.fetchHomeworkDetails();
    const userData = JSON.parse(localStorage.getItem("user"));

    if (userData?.role === "teacher") {
      this.isTeacher = true;
    } else {
      this.isTeacher = false;
      await this.fetchSubmission();
    }
  },
  methods: {
    async fetchHomeworkDetails() {
      try {
        const response = await axios.get(`/homeworks/${this.$route.params.id}`);
        if (response.status === 200) {
          // Если API возвращает массив, берем первый элемент
          this.homework = response.data[0];
        }
      } catch (error) {
        console.error("Ошибка загрузки домашнего задания", error);
      }
    },
    async fetchSubmission() {
      try {
        const userData = JSON.parse(localStorage.getItem("user"));
        if (!userData?.userId || !this.homework) return;
        // Используем id домашнего задания, полученный в fetchHomeworkDetails
        const homeworkId = this.homework.id;
        const response = await axios.get(
          `/homeworks/${homeworkId}/submission?user_id=${userData.userId}`
        );
        if (response.data) {
          this.submission = response.data;
          await this.fetchTeacherResponse(response.data.id);
        }
      } catch (error) {
        console.error("Ошибка загрузки отправленного ответа", error);
      }
    },
    async fetchTeacherResponse(submissionId) {
      try {
        const response = await axios.get(`/teacher_response/${submissionId}`);
        this.teacherResponse = response.data;
      } catch (error) {
        console.error("Ошибка загрузки отклика преподавателя", error);
      }
    },
    openModal() {
      this.isModalOpen = true;
    },
    closeModal() {
      this.isModalOpen = false;
    },
    getFileUrl(file) {
      return file ? `http://localhost:8000/${file.replace(/\\/g, "/")}` : "";
    },
    getFileName(file) {
      return file ? file.split("/").pop() : "";
    },
    openImage(imageUrl) {
      window.open(imageUrl, "_blank");
    },
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString("ru-RU", {
        day: "2-digit",
        month: "long",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    },
    goToEditHomework() {
      this.$router.push({ name: "EditHomework", params: { id: this.homework.id } });
    },
    goToResponses() {
      this.$router.push({ name: "homework-submissions", params: { id: this.$route.params.id } });
    },
  },
};
</script>





<style scoped>
/* Основные стили */
#homework-details {
  padding: 20px;
}
.images-container {
  margin-top: 20px;
  text-align: center;
}
.images img {
  max-width: 150px;
  margin: 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.3s ease;
}
.images img:hover {
  transform: scale(1.5);
}
.container {
  display: flex;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}
.main-content {
  flex: 1;
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  margin-left: 20px;
  position: relative;
}
.header-section {
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
  width: 20px;
  height: 20px;
  background-color: #115544;
  clip-path: polygon(100% 0, 0 50%, 100% 100%);
  cursor: pointer;
}
.homework-title {
  flex: 1;
  font-size: 24px;
  color: #115544;
  font-weight: 500;
  text-align: center;
  margin: 0;
}
.homework-deadline {
  margin: 10px 0;
}
.homework-description {
  margin: 20px 0;
}
.uploaded-files {
  margin: 10px 0;
}
.uploaded-file {
  background: #eee;
  padding: 5px;
  border-radius: 5px;
  margin: 5px 0;
}
.files-section ul {
  list-style: none;
  padding: 0;
  margin: 20px 0 0;
}
.files-section ul li {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}
.files-section ul li a {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: inherit;
  font-size: 16px;
}
.file-icon {
  width: 42px;
  height: 42px;
  margin-right: 10px;
  flex-shrink: 0;
}
.homework-files a:hover {
  text-decoration: underline;
}
/* Кнопки */
.remove-btn {
  background: transparent;
  color: red;
  border: none;
  cursor: pointer;
  font-size: 16px;
  margin-left: 5px;
}
.submit-btn, .add-btn {
  padding: 10px 20px;
  background-color: #115544;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  position: absolute;
  right: 20px;
  bottom: 20px;
}
.submit-btn:hover, .add-btn:hover {
  background-color: #1e9275;
}
@media (max-width: 768px) {
  .container {
    flex-direction: column;
  }
  .main-content {
    margin-left: 0;
    width: 100%;
  }
}
.page-title, h3, h4 {
  font-weight: 500;
}
.file-drop-zone {
  border: 2px dashed #115544;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  margin: 10px 0;
  border-radius: 10px;
}
.file-drop-zone p {
  margin: 0;
}
.file-drop-zone span {
  color: #115544;
  text-decoration: underline;
  cursor: pointer;
}
</style>
