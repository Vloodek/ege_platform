import { createRouter, createWebHistory } from 'vue-router';
import AddHomework from './components/AddHomework.vue';
import StudentCalendar from './components/StudentCalendar.vue';
import StudentRegister from './components/StudentRegister.vue';
import DayPlan from './components/StudentDayPlan.vue';
import LessonDetails from './components/LessonDetail.vue';
import Materials from './components/LessonMaterials.vue';
import AddLesson from './components/AddLesson.vue';
import HomeworkDetails from './components/HomeworkDetails.vue';
import LessonsList from './components/LessonsList.vue';
import HomeworksList from './components/HomeworksList.vue'; 
import EditHomework from './components/EditHomework.vue';
import ShowSubmissions from './components/teacher/ShowSubmissions.vue';
const routes = [
  {
    path: '/',
    name: 'home',
    component: DayPlan,
  },
  {
    path: '/homeworks',  // Путь к компоненту с домашними заданиями
    name: 'homeworks',    
    component: HomeworksList, 
  },
  {
    path: '/edit-homework/:id',
    name: 'EditHomework',
    component: EditHomework
  },
  {
    path: '/register',
    name: 'register',
    component: StudentRegister,
  },
  {
    path: '/calendar',
    name: 'calendar',
    component: StudentCalendar,
  },
  {
    path: '/day-plan',
    name: 'day-plan',
    component: DayPlan,
  },
  {
    path: '/add-lesson',
    name: 'add-lesson',
    component: AddLesson,
  },
  {
    path: '/lesson/:id/details',
    name: 'lesson-details',
    component: LessonDetails,
  },
  
  {
    path: '/lesson/:id/materials',
    name: 'materials',
    component: Materials,
  },
  {
    path: '/lessons',
    name: 'lesson-list',
    component: LessonsList,
  },
  {
    path: '/homework/:id',
    name: 'homework-details',
    component: HomeworkDetails,
  },
  {
    path: '/homework/:id/submissions',
    name: 'homework-submissions',
    component: ShowSubmissions,
  },
  {
    path: '/lesson/:id/edit',
    name: 'add-homework',
    component: AddHomework,
  },
  {
    path: '/profile',
    name: 'user-profile',
    component: UserProfile,
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Глобальный перехватчик для всех маршрутов
router.beforeEach((to, from, next) => {
  const isLoggedIn = localStorage.getItem('access_token');
  
  console.log('Проверка авторизации:', isLoggedIn);
  
  // Если маршрут не требует авторизации (например, страница регистрации)
  if (to.name === 'register') {
    return next();  // Переходим на страницу регистрации, если пользователь не авторизован
  }

  // Если пользователь не авторизован и пытается попасть на защищенный маршрут
  if (!isLoggedIn) {
    console.log('Пользователь не авторизован, редирект на /register');
    return next('/register');  // Перенаправляем на страницу регистрации
  }

  // Если пользователь авторизован, продолжаем переход
  next();
});



import UserProfile from './components/UserProfile.vue';


export default router;
