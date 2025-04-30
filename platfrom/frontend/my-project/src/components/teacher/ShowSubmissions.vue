<template>
  <div id="homework-responses">
    <div class="container">
      <!-- Боковое меню -->
      <SideBar :is-test-active="false" />

      <!-- Основной контент -->
      <main class="main-content">
        <div v-if="homework">
          <!-- Заголовок и стрелка назад -->
          <div class="header-section">
            <div class="back-arrow" @click="$router.go(-1)" />
            <h1 class="homework-title centered">
              Отклики на домашнее задание: {{ homework.description }}
            </h1>
          </div>

          <!-- Фильтр по группе -->
          <div class="filters">
            <div class="filter-label">
              <label for="group">Выберите группу:</label>
            </div>
            <div class="filter-select">
              <select v-model="selectedGroup" @change="onGroupChange">
                <option v-for="group in groups" :key="group.id" :value="group.id">
                  {{ group.name }}
                </option>
              </select>
            </div>
          </div>

          <!-- Таблица с объединёнными данными -->
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
                  v-for="row in rows"
                  :key="row.id"
                  class="table-row"
                  @click="viewDetails(row)"
                >
                  <td>{{ row.name }}</td>
                  <td>{{ row.email }}</td>
                  <td :class="getStatusClass(row.status)">
                    {{ getStatusText(row.status) }}
                  </td>
                  <td>{{ formatDate(row.submission_date) }}</td>
                  <td>{{ formatDate(row.client_submission_time) }}</td>
                </tr>
                <tr v-if="rows.length === 0">
                  <td colspan="5" class="no-data">
                    Нет участников или откликов для выбранной группы
                  </td>
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
import { ref, onMounted, getCurrentInstance } from 'vue';
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
    const lessonId = Number(route.params.id);

    const homework = ref(null);
    const groups = ref([]);
    const selectedGroup = ref(null);
    const rows = ref([]);                  // объединённый список студентов + отклики
    const modalVisible = ref(false);
    const selectedSubmission = ref(null);

    // 1) загрузить детали домашнего задания
    const fetchHomeworkDetails = async () => {
      try {
        const { data } = await $axios.get(`/homeworks/${lessonId}`);
        homework.value = data[0];
      } catch (e) {
        console.error('Ошибка загрузки домашнего задания:', e);
      }
    };

    // 2) загрузить все группы
    const fetchGroups = async () => {
      try {
        const { data } = await $axios.get('/groups/');
        groups.value = data;
        if (groups.value.length) {
          selectedGroup.value = groups.value[0].id;
          await loadRows();
        }
      } catch (e) {
        console.error('Ошибка загрузки групп:', e);
      }
    };

    // 3) собрать строки: всех пользователей + их отклики
    const loadRows = async () => {
  if (!selectedGroup.value || !homework.value) return;

  try {
    const [usersRes, subsRes] = await Promise.all([
      $axios.get(`/groups/${selectedGroup.value}/users`),
      $axios.get(`/api/homework/${homework.value.id}/submissions`, {
        params: { group: selectedGroup.value }
      })
    ]);
    console.log("usersRes:", usersRes.data);
    console.log("subsRes:", subsRes.data);

    // Если в usersRes.data нет поля role — просто не фильтруем
    const students = usersRes.data.map(u => ({
      id: u.id,
      name: u.name,
      email: u.email
    }));
    console.log("students:", students);

    const subs = subsRes.data;

    rows.value = students.map(u => {
      const match = subs.find(x => x.user_id === u.id);
      return {
        id: u.id,
        name: u.name,
        email: u.email,
        status: match?.status ?? 'waiting',
        submission_date: match?.student_submission_time ?? null,
        client_submission_time: match?.modified_submission_time ?? null
      };
    });
    console.log("rows:", rows.value);
  } catch (e) {
    console.error("Ошибка при загрузке данных:", e);
    rows.value = [];
  }
};


    const onGroupChange = () => {
      loadRows();
    };

    const viewDetails = async row => {
      try {
        const { data } = await $axios.get(`/homeworks/${homework.value.id}/submission`, {
          params: { user_id: row.id }
        });
        selectedSubmission.value = data;
        modalVisible.value = true;
      } catch (e) {
        console.error('Ошибка получения деталей отклика:', e);
      }
    };

    const getStatusText = status => {
      switch (status) {
        case 'submitted': return 'Получен ответ';
        case 'graded': return 'Оценено';
        case 'response_received': return 'На доработке';
        case 'waiting': return 'Нет ответа';
        default: return status;
      }
    };
    const getStatusClass = status => {
      switch (status) {
        case 'submitted': return 'status-received';
        case 'graded': return 'status-graded';
        case 'response_received': return 'status-rework';
        case 'waiting': return 'status-waiting';
        default: return '';
      }
    };
    const formatDate = dateString => {
      if (!dateString) return '-';
      return new Date(dateString).toLocaleString('ru-RU', {
        day: '2-digit', month: 'long', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
      });
    };

    onMounted(async () => {
      await fetchHomeworkDetails();
      await fetchGroups();
    });

    return {
      homework,
      groups,
      selectedGroup,
      rows,
      modalVisible,
      selectedSubmission,
      onGroupChange,
      viewDetails,
      getStatusText,
      getStatusClass,
      formatDate
    };
  }
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
