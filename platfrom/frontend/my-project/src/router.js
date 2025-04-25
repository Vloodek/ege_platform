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
import StudentGroups from './components/teacher/StudentGroups.vue';
import TaskTrainer from './components/TaskTrainer.vue';
import UserProfile from './components/UserProfile.vue';
import ExamTaskList from './components/ExamTaskList.vue';
import TrainTaskDetail from './components/TrainTaskDetail.vue';
import TestSession from './components/testing/TestSession.vue';
import CreateHomeworkTest from './components/testing/CreateHomeworkTest.vue'
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
    path: '/test-session/:id',
    name: 'test-session',
    component: TestSession,
    props: true
  },
  {
    path: '/train-tasks/:id',
    name: 'TrainTaskDetail',
    component: TrainTaskDetail,
    props:true
  },
  {
    path: '/task-detail/:id',
    name: 'task-detail',
    component: ExamTaskList,
    // Передаём параметры как props: id — числовой идентификатор, name — название из query-параметров.
    props: route => ({
      id: Number(route.params.id),
      name: route.query.name || ''
    })
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
    path: "/trainer",
    name: "trainer",
    component: TaskTrainer,
  },
  {
    path: "/groups",
    name: "groups",
    component: StudentGroups,
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
    path: '/homeworks/:id/create-test',
    name: 'CreateHomeworkTest',
    props: true,
    component: CreateHomeworkTest,
  },
  {
    path: "/homework_test/:id",
    name: "HomeworkTestSession",
    component: () => import("@/components/testing/HomeworkTestSession.vue"),
    meta: { requiresAuth: true },
  }
,  
  {
    path: '/lesson/:id/edit',
    name: 'add-homework',
    component: AddHomework,
  },
  {
    path: '/test/:id/results',
    name: 'HomeworkTestResults',
    component: () => import('@/components/testing/TestResults.vue'),
    meta: { requiresAuth: true },
  }
,  
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






export default router;
