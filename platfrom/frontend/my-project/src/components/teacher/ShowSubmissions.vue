<template>
  <div id="homework-responses">
    <div class="container">
      <!-- Боковое меню -->
      <SideBar :isTestActive="false" />

      <!-- Основной контент -->
      <main class="main-content">
        <div v-if="homework">
          <!-- Заголовок и стрелка назад -->
          <div class="header-section">
            <div class="back-arrow" @click="$router.go(-1)"></div>
            <h1 class="homework-title centered">
              Отклики на домашнее задание: {{ homework.description }}
            </h1>
          </div>

          <!-- Фильтр по группе, выровненный по правому краю -->
          <div class="filters">
            <div class="filter-label">
              <label for="group">Выберите группу:</label>
            </div>
            <div class="filter-select">
              <select v-model="selectedGroup" @change="fetchSubmissions">
                <option v-for="group in groups" :key="group.id" :value="group.id">
                  {{ group.name }}
                </option>
              </select>
            </div>
          </div>

          <!-- Таблица с откликами -->
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>Имя</th>
                  <th>Email</th>
                  <th>Статус</th>
                  <th>Время отправки</th>
                  <th>Время изменения</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="submission in submissions"
                  :key="submission.id"
                  @click="viewDetails(submission)"
                  class="table-row"
                >
                  <td>{{ submission.name }}</td>
                  <td>{{ submission.email }}</td>
                  <td :class="getStatusClass(submission.status)">
                    {{ getStatusText(submission.status) }}
                  </td>
                  <td>{{ formatDate(submission.submission_date) }}</td>
                  <td>{{ formatDate(submission.client_submission_time) }}</td>
                </tr>
                <tr v-if="submissions.length === 0">
                  <td colspan="5" class="no-data">Нет откликов для выбранной группы</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div v-else>
          <p>Загрузка домашнего задания...</p>
        </div>
      </main>
    </div>

    <!-- Модальное окно для деталей отклика -->
    <SubmissionDetailsModal
      v-if="modalVisible"
      :submission="selectedSubmission"
      @close="modalVisible = false"
    />
  </div>
</template>

<script>
import { ref, onMounted, watch, getCurrentInstance } from 'vue';
import { useRoute } from 'vue-router';
import SideBar from '@/components/SideBar.vue';
import SubmissionDetailsModal from '@/components/teacher/SubmissionDetailsModal.vue';

export default {
  name: 'ShowSubmissions',
  components: { SideBar, SubmissionDetailsModal },
  setup() {
    const { proxy } = getCurrentInstance();
    const $axios = proxy.$axios;

    const route = useRoute();
    const lessonId = route.params.id;

    const homework = ref(null);
    const selectedGroup = ref(null);
    const groups = ref([]);
    const submissions = ref([]);
    const modalVisible = ref(false);
    const selectedSubmission = ref(null);

    const fetchHomeworkDetails = async () => {
      try {
        const { data } = await $axios.get(`/homeworks/${lessonId}`);
        homework.value = data[0];
      } catch (error) {
        console.error('Ошибка загрузки домашнего задания:', error);
      }
    };

    const fetchGroups = async () => {
      try {
        const { data } = await $axios.get('/groups/');
        groups.value = data;
        if (groups.value.length > 0) {
          selectedGroup.value = groups.value[0].id;
          if (homework.value) {
            fetchSubmissions();
          }
        }
      } catch (error) {
        console.error('Ошибка загрузки групп:', error);
      }
    };

    const fetchSubmissions = async () => {
      if (!selectedGroup.value || !homework.value) return;
      try {
        const { data } = await $axios.get(
          `/api/homework/${homework.value.id}/submissions`,
          { params: { group: selectedGroup.value } }
        );
        submissions.value = data;
      } catch (error) {
        console.error('Ошибка загрузки откликов:', error);
      }
    };

    const viewDetails = async (submissionData) => {
      try {
        const userId = submissionData.user_id || submissionData.id;
        const { data } = await $axios.get(
          `/homeworks/${homework.value.id}/submission`,
          { params: { user_id: userId } }
        );
        selectedSubmission.value = data;
        modalVisible.value = true;
      } catch (error) {
        console.error('Ошибка получения деталей отклика:', error);
      }
    };

    const getStatusText = (status) => {
      switch (status) {
        case 'submitted':
          return 'Получен ответ';
        case 'graded':
          return 'Оценено';
        case 'response_received':
          return 'На доработке';
        case 'waiting':
          return 'Нет ответа';
        default:
          return 'Неизвестный статус';
      }
    };

    const getStatusClass = (status) => {
      switch (status) {
        case 'submitted':
          return 'status-received';
        case 'graded':
          return 'status-graded';
        case 'response_received':
          return 'status-rework';
        case 'waiting':
          return 'status-waiting';
        default:
          return '';
      }
    };

    const formatDate = (dateString) => {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleString('ru-RU', {
        day: '2-digit',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    };

    watch(homework, (newHw) => {
      if (newHw && selectedGroup.value) {
        fetchSubmissions();
      }
    });

    onMounted(() => {
      fetchHomeworkDetails();
      fetchGroups();
    });

    return {
      homework,
      selectedGroup,
      groups,
      submissions,
      modalVisible,
      selectedSubmission,
      fetchSubmissions,
      viewDetails,
      getStatusText,
      getStatusClass,
      formatDate,
    };
  },
};
</script>

<style scoped>
.container {
  display: flex;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f3f3f3;
}

.main-content {
  flex: 1;
  background-color: #fff;
  padding: 20px;
  border-radius: 20px;
  margin-left: 20px;
}

.header-section {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  position: relative;
}

.back-arrow {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  background-color: #56AEF6;
  clip-path: polygon(100% 0, 0 50%, 100% 100%);
  cursor: pointer;
}

.homework-title {
  flex: 1;
  font-size: 24px;
  color: #56AEF6;
  font-weight: 500;
  text-align: center;
  margin: 0;
}

.filters {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-bottom: 20px;
}

.filters .filter-label {
  margin-right: 10px;
  font-size: 16px;
}

select {
  padding: 10px;
  font-size: 16px;
  border-radius: 5px;
  border: 1px solid #ddd;
}

.table-container {
  margin-top: 20px;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid #ddd;
}

th,
td {
  padding: 12px 15px;
  text-align: left;
}

th {
  background-color: #f4f4f4;
  font-weight: bold;
}

td {
  border-bottom: 1px solid #ddd;
}

tbody tr:hover {
  background-color: #f1f1f1;
  cursor: pointer;
}

.status-received {
  color: rgb(255, 149, 0);
  font-weight: bold;
}

.status-graded {
  color: green;
  font-weight: bold;
}

.status-rework {
  color: gray;
  font-weight: bold;
}

.status-waiting {
  color: red;
  font-weight: bold;
}

.no-data {
  text-align: center;
  padding: 20px;
  font-style: italic;
}
</style>
