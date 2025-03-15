<template>
    <div id="homeworks">
      <div class="container">
        <!-- Боковое меню -->
        <SideBar :isTestActive="false" />
  
        <!-- Основной контент с домашними заданиями -->
        <main class="main-content">
          <h2>Домашние задания</h2>
  
          <!-- Контейнер для блоков с домашними заданиями -->
          <div class="task-container">
            <div
              class="task-block"
              v-for="(homework, index) in homeworks"
              :key="index"
              @click="openHomework(homework)"
              style="cursor: pointer;"
            >
              <div class="task-description">{{ homework.description }}</div>
  
              <div class="task-bottom">
                <div class="task-time">
                  <img src="@/assets/svg/sidebar/calendar.svg" alt="calendar" class="calendar-icon" />
                  <span>{{ formatTime(homework.date) }}</span>
                </div>
                <!-- Убираем .stop в BaseButton -->
                <BaseButton color="green" @click="handleButtonClick(homework)">Проверить</BaseButton>
              </div>
            </div>
          </div>
  
          <!-- Кнопка добавления домашнего задания -->
          <div v-if="isTeacher" class="add-task-btn-container">
            <div class="add-task-btn" @click="goToAddHomeworkPage">
              <span class="plus-icon">+</span>
            </div>
          </div>
        </main>
      </div>
    </div>
  </template>
  
  <script>
  import SideBar from "./SideBar.vue";
  import BaseButton from "@/components/UI/BaseButton.vue";
  
  export default {
    components: {
      SideBar,
      BaseButton,
    },
    data() {
      return {
        homeworks: [],
        isTeacher: true,
      };
    },
    created() {
      this.fetchHomeworks();
    },
    methods: {
      async fetchHomeworks() {
    try {
        const response = await this.$axios.get("/homeworks");
        this.homeworks = response.data;
        console.log("Домашние задания загружены:", this.homeworks);
    } catch (error) {
        console.error("Ошибка при загрузке домашних заданий:", error);
    }
}
,
      openHomework(homework) {
        if (!homework.id || !homework.lesson_id) {
          console.error("ID домашки или ID урока отсутствует");
          return;
        }
        this.$router.push({
          name: "homework-details",
          params: {
            id: homework.lesson_id,
          },
        });
      },
      handleButtonClick(homework) {
        // Отсюда уже не нужно вызывать stopPropagation(), так как оно должно быть обработано только на уровне родительского компонента
        this.openHomework(homework); // Вызываем openHomework
      },
      formatTime(dateString) {
        const date = new Date(dateString);
        const day = String(date.getDate()).padStart(2, "0");
        const month = String(date.getMonth() + 1).padStart(2, "0");
        const year = date.getFullYear();
        const hours = String(date.getHours()).padStart(2, "0");
        const minutes = String(date.getMinutes()).padStart(2, "0");
        return `${day}.${month}.${year} ${hours}:${minutes}`;
      },
      goToAddHomeworkPage() {
        this.$router.push({ name: "add-homework" });
      },
    },
  };
  </script>
  
  
  
  <style scoped>
  #homeworks {
    display: flex;
    min-height: 100vh;
    background-color: #f5f5f5;
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
    border-radius: 20px;
    margin-left: 20px;
  }
  h2 {
    text-align: center;
    font-weight: 450;
  }
  .task-container {
    margin-bottom: 30px;
  }
  .task-block {
    padding: 25px;
    margin-bottom: 15px;
    border: 2px solid #115544;
    border-radius: 20px;
    background-color: #fff;
  }
  .task-description {
    font-size: 18px;
    font-weight: 350;
    margin-bottom: 25px;
  }
  .task-bottom {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 40px;
  }
  .task-time {
    display: flex;
    align-items: center;
    font-size: 16px;
    font-weight: 350;
    color: #000;
  }
  .task-time span {
    line-height: 1;
    display: flex;
    align-items: center;
  }
  .calendar-icon {
    width: 20px;
    height: 20px;
    margin-right: 8px;
    margin-bottom: 7px;
    filter: brightness(0);
  }
  .add-task-btn-container {
    display: flex;
    justify-content: flex-end;
  }
  .add-task-btn {
    width: 50px;
    height: 50px;
    background-color: #115544;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
  }
  .plus-icon {
    font-size: 28px;
    color: white;
  }
  </style>
  