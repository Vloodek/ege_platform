<template>
  <div id="day-plan">
    <div class="container">
      <SideBar :isTestActive="false" />

      <main class="main-content">
        <h2>Занятия</h2>

        <div class="filter-container">
  <label for="lesson-filter">Фильтр:</label>
  <select id="lesson-filter" v-model="selectedStatus">
    <option value="">Все</option>
    <option value="upcoming">Предстоящие</option>
    <option value="past">Прошедшие</option>
  </select>

  <!-- Фильтр по группам (только для преподавателя) -->
  <label v-if="isTeacher" for="group-filter">Группа:</label>
  <select
    v-if="isTeacher"
    id="group-filter"
    v-model="selectedGroupId"
  >
    <option value="">Все группы</option>
    <option
      v-for="group in groups"
      :key="group.id"
      :value="group.id"
    >
      {{ group.name }}
    </option>
  </select>
</div>


        <div class="task-container">
          <div class="task-block" v-for="lesson in filteredLessons" :key="lesson.id">
            <!-- Кнопка удаления (только для учителя) -->
            <button
              v-if="isTeacher"
              class="delete-btn"
              @click="deleteLesson(lesson.id)"
              title="Удалить урок"
            >×</button>

            <!-- Заголовок урока -->
            <div class="task-header-container">
              <div :class="['task-header', lessonHeaderClass(lesson)]">
                {{ lesson.name }}
              </div>
            </div>

            <div class="task-bottom">
              <div class="task-info">
                <!-- Плашка с названием группы (только для преподавателя) -->
                <div
                  v-if="isTeacher && lesson.group_ids.length"
                  class="lesson-group-badge"
                >
                  Группа «{{ groupName(lesson) }}»
                </div>

                <!-- Дата урока -->
                <div class="task-time">
                  <img
                    src="@/assets/svg/sidebar/calendar.svg"
                    alt="calendar"
                    class="calendar-icon"
                  />
                  <span class="calendar-text">{{ formatTime(lesson.date) }}</span>
                </div>
              </div>

              <BaseButton :color="buttonColor" @click="openLesson(lesson.id)">
                {{ buttonText }}
              </BaseButton>
            </div>
          </div>
        </div>

        <!-- Кнопка добавления урока (для учителя) -->
        <div v-if="isTeacher" class="add-task-btn-container">
          <div class="add-task-btn" @click="goToAddLessonPage">
            <span class="plus-icon">+</span>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import SideBar from '@/components/SideBar.vue';
import BaseButton from '@/components/UI/BaseButton.vue';

export default {
  name: 'DayPlan',
  components: { SideBar, BaseButton },

  data() {
    return {
      lessons: [],
      role: null,
      isTeacher: false,
      userGroup: null,
      selectedStatus: '',
      selectedGroupId: '', // <--- Добавлено
      groups: [],
      groupMap: {},
    };
  },

  computed: {
    buttonText() {
      return this.isTeacher ? 'Перейти' : 'Посмотреть';
    },
    buttonColor() {
      return 'green';
    },
    filteredLessons() {
  const now = Date.now();
  let list = this.lessons;

  // Студент видит только свои группы
  if (!this.isTeacher && this.userGroup != null) {
    list = list.filter(l => l.group_ids?.includes(this.userGroup));
  }

  // Фильтр по статусу (времени)
  if (this.selectedStatus === 'upcoming') {
    list = list.filter(l => new Date(l.date).getTime() >= now);
  } else if (this.selectedStatus === 'past') {
    list = list.filter(l => new Date(l.date).getTime() < now);
  }

  // Фильтр по группе (только для учителя)
  if (this.isTeacher && this.selectedGroupId) {
    list = list.filter(l => l.group_ids?.includes(Number(this.selectedGroupId)));
  }

  return list;
}

  },

  async created() {
    this.loadUserRole();
    await this.fetchGroups();
    await this.fetchLessons();
  },

  methods: {
    loadUserRole() {
      try {
        const u = JSON.parse(localStorage.getItem('user') || '{}');
        this.role = u.role;
        this.isTeacher = u.role === 'teacher';
        this.userGroup = u.group_id ?? null;
      } catch {
        this.role = null;
        this.isTeacher = false;
        this.userGroup = null;
      }
    },

    async fetchGroups() {
      // GET /groups → [{ id, name }, ...]
      try {
        const { data } = await this.$axios.get('/groups');
        this.groups = data;
        this.groupMap = {};
        data.forEach(g => { this.groupMap[g.id] = g.name });
      } catch (err) {
        console.error('Ошибка загрузки групп:', err);
      }
    },

    async fetchLessons() {
      try {
        const u = JSON.parse(localStorage.getItem('user') || '{}');
        let groupId = null;
        if (!this.isTeacher && u.group_name) {
          const res = await this.$axios.get('/group-id', {
            params: { group_name: u.group_name }
          });
          groupId = res.data.group_id;
        }
        const params = this.isTeacher ? {} : { group_id: groupId };
        const { data } = await this.$axios.get('/lessons', { params });
        this.lessons = data;
      } catch (err) {
        console.error('Ошибка загрузки уроков:', err);
      }
    },

    groupName(lesson) {
      const gid = lesson.group_ids?.[0];
      return this.groupMap[gid] || '—';
    },

    formatTime(dt) {
      const d = new Date(dt);
      const dd = String(d.getDate()).padStart(2, '0');
      const mm = String(d.getMonth()+1).padStart(2, '0');
      const yy = d.getFullYear();
      const hh = String(d.getHours()).padStart(2, '0');
      const min = String(d.getMinutes()).padStart(2, '0');
      return `${dd}.${mm}.${yy} ${hh}:${min}`;
    },

    lessonHeaderClass(lesson) {
      return new Date(lesson.date).getTime() >= Date.now()
        ? 'header-upcoming'
        : 'header-past';
    },

    openLesson(id) {
      if (!this.isTeacher) {
        const lesson = this.lessons.find(l => l.id === id);
        if (!lesson || !lesson.group_ids?.includes(this.userGroup)) {
          return alert('У вас нет доступа к этому уроку');
        }
      }
      this.$router.push({ name: 'lesson-details', params: { id } });
    },

    goToAddLessonPage() {
      this.$router.push({ name: 'add-lesson' });
    },

    async deleteLesson(id) {
      if (!confirm('Удалить этот урок?')) return;
      try {
        await this.$axios.delete(`/lessons/${id}`);
        this.lessons = this.lessons.filter(l => l.id !== id);
      } catch {
        alert('Ошибка при удалении урока');
      }
    }
  }
};
</script>

<style scoped>
/* Общие стили */
#day-plan {
  display: flex;
  min-height: 100vh;
  background: #f5f5f5;
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
  background: #fff;
  padding: 20px;
  border-radius: 20px;
  margin-left: 20px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}
h2 {
  text-align: center;
  font-weight: 450;
}

/* Фильтр */
.filter-container {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
  align-items: center;
}
.filter-container select {
  padding: 5px 12px;
  border: 2px solid #56AEF6;
  border-radius: 8px;
  outline: none;
  min-width: 140px;
}


/* Задачи */
.task-container {
  margin-bottom: 30px;
}
.task-block {
  position: relative;
  padding: 15px;
  margin-bottom: 15px;
  border: 2px solid #56AEF6;
  border-radius: 20px;
  background: #fff;
}

/* Кнопка удаления */
.delete-btn {
  position: absolute;
  top: 8px; right: 8px;
  width: 24px; height: 24px;
  border: none; background: transparent;
  font-size: 18px; color: #a00; cursor: pointer;
}
.delete-btn:hover { color: #f00; }

/* Заголовок */
.task-header-container { margin-bottom: 10px; }
.task-header {
  display: inline-block;
  padding: 8px 12px;
  font-size: 18px;
  font-weight: 350;
  border-radius: 8px;
  margin-left: 12px;
}
.header-upcoming { background: #D2FFF4; }
.header-past     { background: #FFD2D2; }

/* Нижняя часть */
.task-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  padding: 10px 15px;
}
.task-info { display: flex; flex-direction: column; }
.task-time {
  display: flex; align-items: center;
  font-size: 16px; margin-top: 4px;
}
.calendar-icon {
  width: 20px; height: 20px;
  margin-right: 8px; filter: brightness(0);
}
.calendar-text { padding-top: 2px; }

/* Плашка группы */
.lesson-group-badge {
  display: inline-block;
  background: #f0f0f0;
  color: #333;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 14px;
  margin-bottom: 6px;
  font-weight: 500;
}

/* Кнопка добавить урок */
.add-task-btn-container {
  display: flex; justify-content: flex-end;
}
.add-task-btn {
  width: 50px; height: 50px;
  background: #56AEF6; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; margin-top: 20px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}
.add-task-btn:hover { background: #b8dfff; }
.plus-icon { font-size: 28px; color: #fff; }
</style>
