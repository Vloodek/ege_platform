<template>
  <div :class="['sidebar', userTypeClass]" :style="{ height: sidebarHeight }">
    <ul class="menu">
      <!-- Пункты меню -->
      <li v-for="item in menuItems" :key="item.label" class="menu-item">
        <router-link :to="item.link" class="menu-link">
          <img :src="item.icon" alt="icon" class="menu-icon" />
          <span class="menu-label">{{ item.label }}</span>
        </router-link>
      </li>
    </ul>
  </div>
</template>

<script>
import lessonsIcon from "@/assets/svg/sidebar/lessons.svg";
import scheduleIcon from "@/assets/svg/sidebar/calendar.svg";
import homeworkIcon from "@/assets/svg/sidebar/dz.svg";
import trainerIcon from "@/assets/svg/sidebar/train.svg";
import groupsIcon from "@/assets/svg/sidebar/groups.svg";

export default {
  props: {
    userType: {
      type: String,
      required: true, // student, teacher, или test
    },
    isTestActive: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    userTypeClass() {
      return {
        teacher: this.userType === "teacher",
        student: this.userType === "student",
        test: this.isTestActive,
      };
    },
    sidebarHeight() {
      if (this.isTestActive) return "100vh";
      return this.userType === "teacher" ? "350px" : "270px";
    },
    menuItems() {
      const commonItems = [
        { label: "Занятия", icon: lessonsIcon, link: "/lessons" },
        { label: "Расписание", icon: scheduleIcon, link: "/calendar" }, // Ссылка на календарь
        { label: "Домашние задания", icon: homeworkIcon, link: "/homeworks" },
        { label: "Тренажёр", icon: trainerIcon, link: "/trainer" },
      ];
      if (this.userType === "teacher") {
        return [...commonItems, { label: "Группы", icon: groupsIcon, link: "/groups" }];
      }
      return commonItems;
    },
  },
};
</script>

<style scoped>
/* Общий стиль бокового меню */
.sidebar {
  display: flex;
  flex-direction: column;
  align-items: flex-start; /* Выровняем содержимое по левому краю */
  width: 257px; /* Установим ширину */
  background-color: #ffffff; /* Фон белый */
  color: #000000; /* Текст чёрный */
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2); /* Тень */
}

/* Меню */
.menu {
  list-style: none;
  padding: 0;
  margin: 0;
  width: 100%;
}

/* Пункт меню */
.menu-item {
  display: flex;
  align-items: center; /* Выравнивание по вертикали (центр) */
  padding: 10px 15px;
  border-radius: 10px;
  margin-bottom: 10px;
  transition: background-color 0.2s;
  cursor: pointer;
  color: #000000; /* Текст чёрный */
}

.menu-item:hover {
  background-color: #e0e0e0; /* Подсветка серым */
}

/* Иконки меню */
.menu-icon {
  width: 40px;
  height: 40px;
  margin-right: 15px; /* Отступ между иконкой и текстом */
  display: inline-block; /* Обеспечивает правильное выравнивание */
}

/* Подписи меню */
.menu-link {
  display: flex; /* Используем flexbox для выравнивания содержимого */
  align-items: center; /* Вертикальное выравнивание по центру */
  width: 100%; /* Обеспечивает растяжение на всю ширину блока */
}

.menu-label {
  font-size: 18px;
  text-align: left; /* Выравниваем текст по левому краю */
  font-weight: 350; /* Для light версии шрифта */
  display: inline-block; /* Чтобы текст и иконка располагались на одной линии */
  flex-grow: 1; /* Позволяет тексту вырасти, заполняя пространство */
  line-height: normal; /* Убираем лишний интерлиньяж */
}

/* Убираем подсветку для ссылок */
.menu-link {
  text-decoration: none; /* Убираем подчеркивание */
  color: inherit; /* Устанавливаем цвет текста, как у родительского элемента */
}
</style>