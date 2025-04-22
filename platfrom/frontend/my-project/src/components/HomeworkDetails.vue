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
            <strong>Дедлайн:</strong><br />
            {{ formatDate(homework.date) }}
          </div>

          <div v-if="homework.text" class="homework-description ql-editor" v-html="homework.text"></div>

          <div v-if="homeworkImages.length" class="images-container">
            <div class="images">
              <img v-for="(image, index) in homeworkImages" :key="index" :src="getFileUrl(image)" alt="Homework Image"
                @click="openImage(getFileUrl(image))" />
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

          <div v-if="isTeacher" class="teacher-buttons">
            <BaseButton color="green" @click="goToEditHomework">
              Изменить ДЗ
            </BaseButton>
            <BaseButton color="white" @click="goToResponses">
              Отклики студентов
            </BaseButton>
          </div>

          <div v-if="!isTeacher && submission" class="student-section">
  <div class="section-divider">
    <h2>Ваш ответ:</h2>
    <p>{{ submission.comment }}</p>

    <div class="uploaded-files">
      <div
        v-for="(file, index) in submission.files"
        :key="index"
        class="uploaded-file"
      >
        📄
        <a :href="getFileUrl(file)" target="_blank">
          {{ getFileName(file) }}
        </a>
      </div>
    </div>
  </div>

  <div
    v-if="teacherResponse"
    class="section-divider"
  >
    <h3>Оценка преподавателя: {{ teacherResponse.teacher_grade || "Не выставлена" }}</h3>
    <p><strong>Комментарий:</strong> {{ teacherResponse.teacher_comment || "Нет комментария" }}</p>

    <div v-if="teacherResponse.files.length" class="teacher-files">
      <p><strong>Файлы преподавателя:</strong></p>
      <ul>
        <li
          v-for="(file, index) in teacherResponse.files"
          :key="index"
        >
          📄 <a :href="getFileUrl(file.file_path)" target="_blank">{{ file.file_name }}</a>
        </li>
      </ul>
    </div>
  </div>

  <div class="section-divider">
    <BaseButton
      :color="teacherResponse?.teacher_grade ? 'gray' : 'green'"
      :disabled="!!teacherResponse?.teacher_grade"
      @click="openModal"
    >
      Редактировать ответ
    </BaseButton>
  </div>
</div>



          <div v-if="!isTeacher && !submission" class="no-submission">
            <BaseButton color="green" @click="openModal">
              Добавить ответ
            </BaseButton>
          </div>

          <StudentSubmissionModal v-if="isModalOpen" :isOpen="isModalOpen" :submission="submission" @close="closeModal"
            @responseSubmitted="fetchSubmission" />
        </div>
        <div v-else>
          <p>Загрузка задания...</p>
        </div>
      </main>
    </div>
  </div>
</template>

<script>

import SideBar from "./SideBar.vue";
import BaseButton from "@/components/UI/BaseButton.vue";
import StudentSubmissionModal from "@/components/student/StudentSubmissionModal.vue";

export default {
  components: { SideBar, BaseButton, StudentSubmissionModal },
  data() {
    return {
      homework: null,
      submission: null,
      teacherResponse: null,
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
        ? this.homework.files.filter(
          (file) => !/\.(jpg|jpeg|png|gif)$/i.test(file)
        )
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
  updated() {
    this.$nextTick(() => {
      this.applyEditorStyles();
    });
  },
  methods: {
    async fetchHomeworkDetails() {
      try {
        const response = await this.$axios.get(
          `/homeworks/${this.$route.params.id}`
        );
        if (response.status === 200) {
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
        const homeworkId = this.homework.id;
        const response = await this.$axios.get(
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
        const response = await this.$axios.get(`/teacher_response/${submissionId}`);
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
      if (!file) return "";
      const parts = file.split(/[\\/]/);
      return parts[parts.length - 1];
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
      this.$router.push({
        name: "EditHomework",
        params: { id: this.homework.id },
      });
    },
    goToResponses() {
      this.$router.push({
        name: "homework-submissions",
        params: { id: this.$route.params.id },
      });
    },
    applyEditorStyles() {
  const editorImages = document.querySelectorAll(".ql-editor img");

  editorImages.forEach((img) => {
    if (img.dataset.listenerAttached === "true") return;

    img.style.maxWidth = "300px";
    img.style.width = "auto";
    img.style.height = "auto";
    img.style.objectFit = "contain";
    img.style.display = "block";
    img.style.margin = "10px auto";
    img.style.cursor = "pointer";

    const src = img.getAttribute("src");
    if (src) {
      img.addEventListener("click", () => {
        window.open(src, "_blank");
      });
      img.dataset.listenerAttached = "true";
    }
  });
}

,
  },
};
</script>

<style scoped>
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
  display: inline-block;
  background-color: #ffffff;
  border: 1px solid #606060;
  padding: 10px 14px;
  border-radius: 6px;
  color: #000000;
  font-size: 16px;
  font-weight: 500;
  line-height: 1.5;
  margin: 20px 0;
  white-space: nowrap;
}

.homework-description {
  margin: 20px 0;
  font-size: 16px;
  line-height: 1.6;
  color: #333;
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

.teacher-buttons {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.no-submission {
  margin-top: 20px;
  text-align: center;
}

.student-block,
.teacher-block {
  border: 1px solid #b8e0c2;
  background-color: #f1fdf5;
  border-radius: 8px;
  padding: 20px;
  margin-top: 20px;
  color: #115544;
}

.teacher-block {
  margin-top: 30px;
  background-color: #e6f8ec;
}

.block-title {
  font-size: 18px;
  font-weight: normal;
  color: #115544;
  margin-bottom: 10px;
}

.sub-label {
  font-weight: normal;
  color: #115544;
  margin-bottom: 4px;
  display: block;
}

.ql-editor img {
  max-width: 300px !important;
  width: auto !important;
  height: auto !important;
  object-fit: contain !important;
  display: block !important;
  margin: 10px auto !important;
}

.section-divider {
  padding: 20px 0;
  border-top: 1px solid #ddd;
}

.section-divider:first-of-type {
  border-top: none;
}

.section-divider h2,
.section-divider h3 {
  font-size: 18px;
  font-weight: normal;
  color: #222;
  margin-bottom: 10px;
}

.uploaded-files,
.teacher-files {
  margin-top: 10px;
}
.student-section {
  margin-top: 20px;
}

.section-divider {
  padding: 20px 0;
  border-top: 2px solid #b8e0c2; /* Линия сверху */
}

.section-divider:first-of-type {
  border-top: none;
}

.section-divider h2 {
  font-size: 18px;
  font-weight: 500;
  color: #115544;
  margin-bottom: 10px;
}

.uploaded-files,
.teacher-files {
  margin-top: 10px;
}

.uploaded-file {
  margin-bottom: 5px;
}

.uploaded-file a {
  color: #115544;
  font-size: 14px;
  text-decoration: none;
}

.uploaded-file a:hover {
  text-decoration: underline;
}

.images img {
  display: none;
}
</style>
