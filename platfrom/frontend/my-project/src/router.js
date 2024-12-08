import AddHomework from './components/AddHomework.vue';
import { createRouter, createWebHistory } from 'vue-router';
import StudentCalendar from './components/StudentCalendar.vue';
import StudentRegister from './components/StudentRegister.vue';
import DayPlan from './components/StudentDayPlan.vue'; 
import LessonDetails from './components/LessonDetail.vue'; // Обновите импорт
import Materials from './components/LessonMaterials.vue';
import AddLesson from './components/AddLesson.vue';
import HomeworkDetails from './components/HomeworkDetails.vue';
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
    path: '/add-lesson',
    name: 'add-lesson',
    component: AddLesson,
    beforeEnter: (to, from, next) => {
      const isLoggedIn = localStorage.getItem('access_token');
      if (!isLoggedIn) {
        next('/register');
      } else {
        next();
      }
    }
  }
  ,
  {
    path: '/lesson/:id/details', // Обновите маршрут на уроки
    name: 'lesson-details', // Обновите название маршрута
    component: LessonDetails, // Убедитесь, что это правильный компонент
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
    path: '/lesson/:id/materials',
    name: 'materials',
    component: Materials,
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
    path: '/homework/:id', // Параметр id домашнего задания
    name: 'homework-details',
    component: HomeworkDetails,
  },
  {
    path: '/lesson/:id/edit',
    name: 'add-homework',
    component: AddHomework,  // Обновите, если компонент называется AddHomework
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
  history: createWebHistory(),
  routes,
});

export default router;
