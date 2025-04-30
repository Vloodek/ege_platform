<template>
  <div id="lesson-detail">
    <div class="container">
      <SideBar :is-test-active="false" />

      <main v-if="lesson" class="main-content">
        <!-- Header -->
        <div class="header-section">
          <button class="back-arrow" @click="goBack"></button>
          <h1 class="lesson-title">{{ lesson.name }}</h1>
        </div>

        <!-- Video -->
        <div v-if="lesson.videoLink" class="video-container">
          <div v-if="videoEmbedHtml" v-html="videoEmbedHtml"></div>
          <iframe
            v-else-if="videoEmbedUrl"
            :src="videoEmbedUrl"
            width="100%"
            height="400"
            frameborder="0"
            allow="autoplay; encrypted-media; fullscreen; picture-in-picture; screen-wake-lock;"
            allowfullscreen
          ></iframe>
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
              <input
                id="watched"
                v-model="lesson.watched"
                type="checkbox"
              />
              <label for="watched">Просмотрено</label>
            </div>

            <div v-if="isTeacher && lesson.group_ids.length" class="lesson-group-badge">
              Группа «{{ groupName }}»
            </div>
          </div>

          <div class="right-column">
            <BaseButton color="white" @click="viewMaterials">
              Материалы занятия
            </BaseButton>

            <BaseButton
              v-if="isTeacher || homeworkExists"
              color="green"
              @click="goToHomework"
            >
              ДЗ
            </BaseButton>

            <BaseButton
              v-if="testExists"
              color="green"
              @click="onTestButtonClick"
            >
              {{ testButtonText }}
            </BaseButton>
            <BaseButton
              v-else-if="!testExists && isTeacher"
              color="green"
              @click="goToCreateTest"
            >
              Создать тест
            </BaseButton>
          </div>
        </div>
      </main>

      <div v-else class="loading">Загрузка...</div>

      <!-- Modal -->
      <div v-if="showResultsModal" class="modal-overlay" @click.self="closeResults">
        <div class="modal-window">
          <button class="modal-close" @click="closeResults">×</button>
          <HomeworkTestResults :test-id="testId" @close="closeResults" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SideBar from "@/components/SideBar.vue";
import BaseButton from "@/components/UI/BaseButton.vue";
import HomeworkTestResults from "@/components/testing/TestResults.vue";

export default {
  name: "LessonDetail",
  components: {
    SideBar,
    BaseButton,
    HomeworkTestResults
  },
  data() {
    return {
      lesson: null,
      videoEmbedUrl: null,
      videoEmbedHtml: null,
      isTeacher: false,
      homeworkExists: false,
      testExists: false,
      testPassed: false,
      testId: null,
      showResultsModal: false,
      groups: [],
      groupMap: {}
    };
  },
  computed: {
    testButtonText() {
      if (this.isTeacher) {
        return "Результаты теста";
      }
      return this.testPassed ? "Результаты теста" : "Пройти тест";
    },
    groupName() {
      const gid = this.lesson.group_ids[0];
      return this.groupMap[gid] || "—";
    }
  },
  async created() {
    const user = JSON.parse(localStorage.getItem("user") || "{}");
    this.isTeacher = user.role === "teacher";

    if (this.isTeacher) {
      await this.fetchGroups();
    }

    await this.fetchLesson();
    await this.checkHomework();
    await this.checkTest();
  },
  methods: {
    goBack() {
      this.$router.go(-1);
    },

    async fetchGroups() {
      try {
        const { data } = await this.$axios.get("/groups");
        this.groups = data;
        data.forEach(g => {
          this.groupMap[g.id] = g.name;
        });
      } catch (err) {
        console.error("Ошибка загрузки групп:", err);
      }
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
        const { data } = await this.$axios.get(
          `/homework_tests/by_lesson/${lessonId}`
        );
        this.testExists = true;
        this.testId = data.id;
        if (!this.isTeacher) {
          await this.checkTestStatus();
        }
      } catch {
        this.testExists = false;
      }
    },

    async checkTestStatus() {
      const user = JSON.parse(localStorage.getItem("user") || "{}");
      try {
        await this.$axios.get(
          `/homework_tests/${this.testId}/student_result`,
          { params: { user_id: user.userId } }
        );
        this.testPassed = true;
      } catch (err) {
        this.testPassed = false;
      }
    },

    viewMaterials() {
      this.$router.push(`/lesson/${this.lesson.id}/materials`);
    },

    goToHomework() {
      const lessonId = this.$route.params.id;
      const path = this.homeworkExists
        ? `/homework/${lessonId}`
        : `/lesson/${lessonId}/edit`;
      this.$router.push(path);
    },

    goToCreateTest() {
      this.$router.push({
        name: "CreateHomeworkTest",
        params: { id: this.lesson.id }
      });
    },

    onTestButtonClick() {
      if (!this.isTeacher && !this.testPassed) {
        this.goToTest();
      } else {
        this.showResultsModal = true;
      }
    },

    goToTest() {
      this.$router.push({
        name: "HomeworkTestSession",
        params: { id: this.testId }
      });
    },

    closeResults() {
      this.showResultsModal = false;
    },

    processVideoLink(link) {
      if (!link) return;
      // если сохранён готовый iframe HTML
      if (link.trim().startsWith("<iframe")) {
        this.videoEmbedHtml = link;
        this.videoEmbedUrl = null;
        return;
      }
      // YouTube
      const yt = link.match(/(?:v=|\/)([A-Za-z0-9_-]{11})/);
      if (yt) {
        this.videoEmbedUrl = `https://www.youtube.com/embed/${yt[1]}`;
        this.videoEmbedHtml = null;
        return;
      }
      // VK
      const vk = link.match(/video-(\d+)_(\d+)/);
      if (vk) {
        const [ , owner, vid ] = vk;
        this.videoEmbedUrl = `https://vk.com/video_ext.php?oid=${owner}&id=${vid}&hd=2`;
        this.videoEmbedHtml = null;
        return;
      }
      // иначе — прямой URL
      this.videoEmbedUrl = link;
      this.videoEmbedHtml = null;
    },

    formatDateTime(dt) {
      return new Date(dt).toLocaleString("ru-RU", {
        day: "2-digit",
        month: "2-digit",
        year: "2-digit",
        hour: "2-digit",
        minute: "2-digit"
      });
    }
  }
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
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
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
  width: 20px;
  height: 20px;
  background: #56AEF6;
  clip-path: polygon(100% 0, 0 50%, 100% 100%);
  cursor: pointer;
}
.lesson-title {
  font-size: 24px;
  color: #56AEF6;
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
  width: 24px;
  height: 24px;
  margin-right: 10px;
}
.lesson-date {
  font-size: 16px;
  color: #000;
}
.lesson-description {
  margin: 10px 0;
  font-size: 16px;
  color: #333;
}
.checkbox-container {
  display: flex;
  align-items: center;
  margin-top: 10px;
}
.checkbox-container input {
  appearance: none;
  width: 20px;
  height: 20px;
  border: 2px solid #56AEF6;
  border-radius: 4px;
  margin-right: 10px;
  position: relative;
}
.checkbox-container input:checked {
  background: #56AEF6;
}
.checkbox-container input:checked::after {
  content: "✔";
  position: absolute;
  top: 2px;
  left: 4px;
  color: #fff;
  font-size: 14px;
}
.checkbox-container label {
  font-size: 16px;
  color: #333;
}

/* Бейдж группы */
.lesson-group-badge {
  display: inline-block;
  background: #f0f0f0;
  color: #333;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 14px;
  margin-top: 10px;
  font-weight: 500;
}

.right-column {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
}

/* Стили модалки */
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
.modal-window {
  background: #fff;
  border-radius: 12px;
  max-width: 800px;
  width: 90%;
  max-height: 90%;
  overflow-y: auto;
  position: relative;
  padding: 20px;
}
.modal-close {
  position: absolute;
  top: 10px;
  right: 10px;
  background: transparent;
  border: none;
  font-size: 24px;
  cursor: pointer;
}
</style>
