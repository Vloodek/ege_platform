<template>
  <aside :class="['sidebar', { 'sidebar-test': isTestActive }]">
    <ul>
      <li><router-link to="/calendar">Занятия</router-link></li> <!-- Добавим роутер на занятия -->
      <li><router-link to="/calendar">Расписание</router-link></li> <!-- Теперь Расписание ведет на /calendar -->
      <li><a href="#">Домашние задания</a></li>
      <li><a href="#">Тренажер</a></li>
      <li v-if="isTestActive"><a href="#">Тест</a></li>  <!-- Добавим элемент для теста -->
    </ul>
  </aside>
</template>

<script>
export default {
  name: "SideBar",
  props: {
    isTestActive: {
      type: Boolean,
      default: false,  // По умолчанию тест не активен
    },
  },
};
</script>

<style scoped>
/* Боковое меню */
.sidebar {
  width: 240px;
  background-color: #ffffff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.sidebar ul {
  list-style: none;
  padding: 0;
}

.sidebar li {
  margin-bottom: 16px;
}

.sidebar a,
.sidebar li a {
  text-decoration: none;
  color: #333;
  font-size: 16px;
  font-weight: 500;
}

.sidebar a:hover,
.sidebar li a:hover {
  color: #4CAF50;
}

/* Стиль для бокового меню во время теста */
.sidebar-test {
  background-color: #f0f0f0;  /* Меняем фон, когда активен тест */
}
</style>
