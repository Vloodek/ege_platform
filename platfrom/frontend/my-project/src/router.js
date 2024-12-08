import AddHomework from './components/AddHomework.vue'; // Ensure this matches the file name
import { createRouter, createWebHistory } from 'vue-router';
import StudentCalendar from './components/StudentCalendar.vue';
import StudentRegister from './components/StudentRegister.vue';
import DayPlan from './components/StudentDayPlan.vue'; 
import AddTask from './components/AddHomework.vue';
import TaskDetails from './components/TaskDetail.vue';
import Materials from './components/TaskMaterials.vue';

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
    name: 'add-task',
    component: AddTask,
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
    path: '/task/:id/details',
    name: 'task-details',
    component: TaskDetails,
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
    path: '/task/:id/materials',
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
    path: '/task/:id/edit',
    name: 'edit-homework',
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
