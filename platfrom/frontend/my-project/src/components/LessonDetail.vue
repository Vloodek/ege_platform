<template>
  <div id="lesson-detail">
    <div class="container">
      <SideBar :isTestActive="false" />

      <main class="main-content" v-if="lesson">
        <!-- Header -->
        <div class="header-section">
          <div class="back-arrow" @click="goBack" />
          <h1 class="lesson-title">{{ lesson.name }}</h1>
        </div>

        <!-- Video -->
        <div v-if="lesson.videoLink" class="video-container">
          <div v-if="videoEmbedHtml" v-html="videoEmbedHtml" />
          <iframe
            v-else-if="videoEmbedUrl"
            :src="videoEmbedUrl"
            width="100%"
            height="400"
            frameborder="0"
            allow="autoplay; encrypted-media; fullscreen; picture-in-picture; screen-wake-lock;"
            allowfullscreen
          />
        </div>

        <!-- Description + Actions -->
        <div class="content-section">
          <div class="left-column">
            <div class="calendar">
              <img
                class="calendar-icon"
                src="@/assets/svg/TaskDetail/calendar.svg"
                alt="Calendar Icon"
              />
              <span class="lesson-date">{{ formatDateTime(lesson.date) }}</span>
            </div>
            <p class="lesson-description">{{ lesson.description }}</p>
            <div class="checkbox-container">
              <input type="checkbox" id="watched" v-model="lesson.watched" />
              <label for="watched">Просмотрено</label>
            </div>
          </div>

          <div class="right-column">
            <!-- Materials button -->
            <BaseButton color="white" @click="viewMaterials">
              Материалы занятия
            </BaseButton>

            <!-- Homework button -->
            <BaseButton
              v-if="isTeacher || homeworkExists"
              color="green"
              @click="goToHomework"
            >
              ДЗ
            </BaseButton>

            <!-- Take Test button (всегда, если есть тест) -->
            <BaseButton
              v-if="testExists"
              color="green"
              @click="goToTest"
            >
              Пройти тест
            </BaseButton>
            <!-- Create Test button (только если нет теста и ты учитель) -->
            <BaseButton
              v-else-if="isTeacher"
              color="green"
              @click="goToCreateTest"
            >
              Создать тест
            </BaseButton>
          </div>
        </div>
      </main>

      <div v-else class="loading">Загрузка...</div>
    </div>
  </div>
</template>

<script>
import SideBar from "./SideBar.vue";
import BaseButton from "@/components/UI/BaseButton.vue";

export default {
  name: "LessonDetail",
  components: { SideBar, BaseButton },
  data() {
    return {
      lesson: null,
      videoEmbedUrl: null,
      videoEmbedHtml: null,
      isTeacher: false,
      homeworkExists: false,
      testExists: false,
      testId: null,
    };
  },
  async created() {
    const user = JSON.parse(localStorage.getItem("user")) || {};
    this.isTeacher = user.role === "teacher";

    await this.fetchLesson();
    await this.checkHomework();
    await this.checkTest();
  },
  methods: {
    goBack() {
      this.$router.go(-1);
    },
    async fetchLesson() {
      try {
        const lessonId = this.$route.params.id;
        const { data } = await this.$axios.get(`/lessons/${lessonId}`);
        this.lesson = data;
        this.processVideoLink(data.videoLink);
      } catch (err) {
        console.error("Ошибка загрузки занятия:", err);
      }
    },
    async checkHomework() {
      try {
        const lessonId = this.$route.params.id;
        await this.$axios.get(`/homeworks/by_lesson/${lessonId}/id`);
        this.homeworkExists = true;
      } catch {
        this.homeworkExists = false;
      }
    },
    async checkTest() {
  try {
    const lessonId = this.$route.params.id;
    // Проверяем наличие теста для урока
    const { data } = await this.$axios.get(`/homework_tests/by_lesson/${lessonId}`);
    this.testExists = true;
    this.testId = data.id;
  } catch (err) {
    console.warn("Нет тестов домашки:", err);
    this.testExists = false;
  }
},
    goToHomework() {
      const lessonId = this.$route.params.id;
      if (this.homeworkExists) {
        this.$router.push(`/homework/${lessonId}`);
      } else {
        this.$router.push(`/lesson/${lessonId}/edit`);
      }
    },
    goToCreateTest() {
      this.$router.push({
        name: "CreateHomeworkTest",
        params: { id: this.lesson.id },
      });
    },
    goToTest() {
  this.$router.push({
    name: "HomeworkTestSession", // 👈 название маршрута
    params: { id: this.testId },
  });
}
,
    viewMaterials() {
      this.$router.push(`/lesson/${this.lesson.id}/materials`);
    },
    processVideoLink(link) {
      if (!link) return;
      if (link.includes("<iframe")) {
        this.videoEmbedHtml = link;
      } else if (/youtube\.com|youtu\.be/.test(link)) {
        const m = link.match(/(?:v=|\/)([A-Za-z0-9_-]{11})/);
        this.videoEmbedUrl = m
          ? `https://www.youtube.com/embed/${m[1]}`
          : null;
      } else if (/vkvideo\.ru/.test(link)) {
        const m = link.match(/video-?(\d+)_(\d+)/);
        this.videoEmbedUrl = m
          ? `https://vk.com/video_ext.php?oid=-${m[1]}&id=${m[2]}&hd=2`
          : null;
      }
    },
    formatDateTime(dt) {
      return new Date(dt).toLocaleString("ru-RU", {
        day: "2-digit",
        month: "2-digit",
        year: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
      });
    },
  },
};
</script>

<style scoped>
#lesson-detail {
  display: flex;
  min-height: 100vh;
  background: #f5f5f5;
}
.container {
  display: flex;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}
.loading {
  flex: 1;
  text-align: center;
  color: #666;
  font-size: 18px;
}
.main-content {
  flex: 1;
  background: #fff;
  padding: 20px;
  border-radius: 20px;
  margin-left: 20px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
.header-section {
  position: relative;
  text-align: center;
  margin-bottom: 20px;
}
.back-arrow {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 20px; height: 20px;
  background: #115544;
  clip-path: polygon(100% 0,0 50%,100% 100%);
  cursor: pointer;
}
.lesson-title {
  font-size: 24px;
  color: #115544;
  margin: 0;
  font-weight: 500;
}
.video-container {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}
.content-section {
  display: flex;
  justify-content: space-between;
}
.left-column {
  flex: 1;
}
.calendar {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}
.calendar-icon {
  width: 24px; height: 24px;
  margin-right: 10px;
}
.lesson-date {
  font-size: 16px; color: #000;
}
.lesson-description {
  margin: 10px 0;
  font-size: 16px; color: #333;
}
.checkbox-container {
  display: flex;
  align-items: center;
  margin-top: 10px;
}
.checkbox-container input {
  appearance: none;
  width: 20px; height: 20px;
  border: 2px solid #115544;
  border-radius: 4px;
  margin-right: 10px;
  position: relative;
}
.checkbox-container input:checked {
  background: #115544;
}
.checkbox-container input:checked::after {
  content: "✔";
  position: absolute; top: 2px; left: 4px;
  color: #fff; font-size: 14px;
}
.checkbox-container label {
  font-size: 16px; color: #333;
}
.right-column {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
}
</style>
