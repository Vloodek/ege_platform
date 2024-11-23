import { createRouter, createWebHistory } from 'vue-router';
import StudentCalendar from './components/StudentCalendar.vue';
import StudentRegister from './components/StudentRegister.vue';
import DayPlan from './components/StudentDayPlan.vue'; 
import AddTask from './components/AddTask.vue'; // Импортируем компонент добавления задания

const routes = [
  {
    path: '/',
    name: 'home',
    component: DayPlan,
    beforeEnter: (to, from, next) => {
      const isLoggedIn = localStorage.getItem('access_token');
      if (!isLoggedIn) {
        next('/register');
      } else {
        next();
      }
    }
  },
  {
    path: '/register',
    name: 'register',
    component: StudentRegister,
    beforeEnter: (to, from, next) => {
      const isLoggedIn = localStorage.getItem('access_token');
      if (isLoggedIn) {
        next('/');
      } else {
        next();
      }
    }
  },
  {
    path: '/calendar',
    name: 'calendar',
    component: StudentCalendar,
    beforeEnter: (to, from, next) => {
      const isLoggedIn = localStorage.getItem('access_token');
      if (!isLoggedIn) {
        next('/register');
      } else {
        next();
      }
    }
  },
  {
    path: '/day-plan',
    name: 'day-plan',
    component: DayPlan,
    beforeEnter: (to, from, next) => {
      const isLoggedIn = localStorage.getItem('access_token');
      if (!isLoggedIn) {
        next('/register');
      } else {
        next();
      }
    }
  },
  {
    path: '/add-task',
    name: 'add-task', // Новый маршрут для страницы добавления задания
    component: AddTask, // Компонент добавления задания
    beforeEnter: (to, from, next) => {
      const isLoggedIn = localStorage.getItem('access_token');
      if (!isLoggedIn) {
        next('/register');
      } else {
        next();
      }
    }
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
