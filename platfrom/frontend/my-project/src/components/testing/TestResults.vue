<template>
  <div class="results-wrapper">
    <h2>Результаты теста</h2>

    <!-- Преподаватель -->
    <div v-if="isTeacher">
      <!-- 1) Кнопка удаления -->
      <div class="actions">
        <BaseButton color="danger" @click="deleteTest">
          Удалить тест
        </BaseButton>
      </div>

      <table v-if="students.length" class="results-table">
        <thead>
          <tr>
            <th>Имя</th>
            <th>Группа</th>
            <th>Сдал</th>
            <th>Правильных</th>
            <th>Всего</th>
            <th>Процент</th>
            <!-- 2) Новая колонка: дата сдачи -->
            <th>Дата сдачи</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in students" :key="s.user_id">
            <td>{{ s.name }}</td>
            <td>{{ s.class_name }}</td>
            <td>{{ s.passed ? '✅' : '❌' }}</td>
            <td>{{ s.correct }}</td>
            <td>{{ s.total }}</td>
            <td>{{ s.passed ? Math.round((s.correct / s.total) * 100) : '-' }}%</td>
            <!-- 3) Ячейка с completed_at -->
            <td>
              {{ s.completed_at
                 ? new Date(s.completed_at).toLocaleString()
                 : '-' }}
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else>
        Нет данных
      </div>
    </div>

    <!-- Ученик -->
    <div v-else>
      <div v-if="myScore !== null">
        Вы набрали <strong>{{ myScore }}</strong> баллов из {{ maxScore }}.
      </div>
      <div v-else>
        Загрузка...
      </div>
    </div>

    <div class="actions">
      <BaseButton color="white" @click="$emit('close')">
        Закрыть
      </BaseButton>
    </div>
  </div>
</template>

<script>
import BaseButton from "@/components/UI/BaseButton.vue";

export default {
  name: "HomeworkTestResults",
  components: { BaseButton },
  props: {
    testId: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      isTeacher: false,
      students: [],
      myScore: null,
      maxScore: null,
    };
  },
  async mounted() {
    const user = JSON.parse(localStorage.getItem("user"));
    this.isTeacher = user.role === "teacher";

    if (this.isTeacher) {
      try {
        // передаём withCredentials, чтобы резолвились HttpOnly-куки
        const res = await this.$axios.get(
          `/homework_tests/${this.testId}/results_by_group`,
          { withCredentials: true }
        );
        this.students = res.data;
      } catch (error) {
        console.error("Ошибка при загрузке результатов для преподавателя:", error);
      }
    } else {
      try {
        const res = await this.$axios.get(
          `/homework_tests/${this.testId}/student_result`,
          {
            withCredentials: true,
            params: { user_id: user.userId }
          }
        );
        this.myScore = res.data.score;
        this.maxScore = res.data.max_score;
      } catch (error) {
        console.error("Ошибка при загрузке результатов для студента:", error);
      }
    }
  },
  methods: {
    async deleteTest() {
      if (!confirm("Вы уверены, что хотите удалить этот тест и все его результаты?")) {
        return;
      }
      try {
        await this.$axios.delete(
          `/homework_tests/${this.testId}`,
          { withCredentials: true }
        );
        // сообщаем родителю или перенаправляем
        this.$emit("deleted", this.testId);
      } catch (err) {
        console.error("Не удалось удалить тест:", err);
        alert("Ошибка при удалении теста");
      }
    }
  }
};
</script>

<style scoped>
.results-wrapper {
  padding: 20px;
  background: white;
  border-radius: 12px;
}
.results-table {
  width: 100%;
  border-collapse: collapse;
}
.results-table th,
.results-table td {
  padding: 8px;
  border: 1px solid #ccc;
  text-align: center;
}
.actions {
  margin-top: 20px;
  text-align: right;
}
</style>
