<template>
  <div class="sidebar builder">
    <!-- Время -->
    <div
      v-if="mode === 'build'"
      class="time-config"
    >
      <label>Время (мин):</label>
      <input
        v-model.number="localDuration"
        type="number"
        min="1"
        @input="onLocalDurationInput"
      >
    </div>
    <div
      v-else
      class="time-config"
    >
      <label>Время:</label>
      <div class="timer-display">
        {{ timerDisplay }}
      </div>
    </div>

    <!-- Количество вопросов -->
    <div
      v-if="mode === 'build'"
      class="count-config"
    >
      <label>Вопросов:</label>
      <input
        v-model.number="localCount"
        type="number"
        min="1"
        @input="onLocalCountInput"
      >
    </div>
    <div
      v-else
      class="count-config"
    >
      <label>Всего:</label>
      <div class="count-display">
        {{ localCount }}
      </div>
    </div>

    <!-- Навигация сверху (только в сессии) -->
    <div
      v-if="mode === 'session'"
      class="nav-buttons"
    >
      <button
        :disabled="currentIndex === 0"
        @click="$emit('prev')"
      >
        ←
      </button>
      <button
        :disabled="currentIndex >= localCount - 1"
        @click="$emit('next')"
      >
        →
      </button>
    </div>

    <!-- Сетка вопросов -->
    <div class="questions-grid">
      <div
        v-for="n in localCount"
        :key="n"
        class="q-square"
        :class="{
          active: n - 1 === currentIndex,
          answered: mode === 'session' && !testFinished && answers[n - 1] != null,
          correct: mode === 'session' && testFinished && results[n - 1] === true,
          incorrect: mode === 'session' && testFinished && results[n - 1] === false
        }"
        @click="$emit('select', n - 1)"
      >
        {{ n }}
      </div>
    </div>

    <!-- Навигация снизу (только в режиме build) -->
    <div
      v-if="mode === 'build'"
      class="nav-buttons"
    >
      <button
        :disabled="currentIndex === 0"
        @click="$emit('prev')"
      >
        ←
      </button>
      <button
        :disabled="currentIndex >= localCount - 1"
        @click="$emit('next')"
      >
        →
      </button>
    </div>

    <!-- Кнопки выхода и завершения -->
    <div
      v-if="mode === 'session'"
      class="footer-buttons"
    >
      <button
        class="btn-exit"
        @click="$emit('exit')"
      >
        {{ exitLabel || 'Выйти' }}
      </button>
      <button
        class="btn-complete"
        @click="$emit('complete')"
      >
        Завершить тест
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: "BuilderSidebar",
  props: {
    duration:     { type: Number, default: 30 },
    count:        { type: Number, default: 5 },
    currentIndex: { type: Number, default: 0 },
    results:      { type: Object,  default: () => ({}) },
    answers:      { type: Object,  default: () => ({}) },
    testFinished: { type: Boolean, default: false },
    mode:         { type: String,  default: 'build' }, // 'build' | 'session'
    timerDisplay: { type: String,  default: '00:00' },
    exitLabel:    { type: String,  default: '' },
  },
  data() {
    return {
      localDuration: this.duration,
      localCount:    this.count,
    };
  },
  watch: {
    duration(v) { this.localDuration = v; },
    count(v)    { this.localCount    = v; },
  },
  methods: {
    onLocalDurationInput() {
    // минимум 1
    if (this.localDuration < 1) this.localDuration = 1;
    // сразу поднимаем в родителя
    this.$emit("update:duration", this.localDuration);
  },

  onLocalCountInput() {
    if (this.localCount < 1) this.localCount = 1;
    this.$emit("update:count", this.localCount);

    // если текущий индекс за границей — корректируем
    if (this.currentIndex >= this.localCount) {
      this.$emit("select", this.localCount - 1);
    }
  },
  },
};
</script>

<style scoped>
.sidebar.builder {
  width: 260px;
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.time-config,
.count-config {
  margin-bottom: 12px;
}
.time-config label,
.count-config label {
  display: block;
  font-size: 14px;
  margin-bottom: 4px;
}
.time-config input,
.count-config input {
  width: 100%;
  padding: 6px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.timer-display,
.count-display {
  padding: 6px;
  border: 1px solid #ccc;
  border-radius: 4px;
  text-align: center;
  font-weight: bold;
}

/* Навигация */
.nav-buttons {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}
.nav-buttons button {
  background: #56AEF6;
  color: #fff;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
}
.nav-buttons button:disabled {
  opacity: 0.5;
  cursor: default;
}

/* Сетка вопросов */
.questions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(40px, 1fr));
  grid-gap: 6px;
  margin-bottom: 16px;
}
.q-square {
  background: #eee;
  border: 1px solid #56AEF6;
  border-radius: 4px;
  text-align: center;
  line-height: 32px;
  cursor: pointer;
}
.q-square.active {
  background: #56AEF6;
  color: #fff;
  border: 2px solid #000; /* черная обводка */
}

.q-square.answered {
  background: #a5d6a7; /* светло-зеленый */
  color: #1b5e20;
}
.q-square.correct {
  background-color: #4caf50;
  color: white;
}
.q-square.incorrect {
  background-color: #f44336;
  color: white;
}

/* Кнопки внизу */
.footer-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 16px;
}
.btn-exit,
.btn-complete {
  width: 48%;
  padding: 10px;
  border: none;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
}
.btn-exit {
  background-color: #e74c3c;
  color: #fff;
}
.btn-exit:hover {
  background-color: #c0392b;
}
.btn-complete {
  background-color: #3498db;
  color: #fff;
}
.btn-complete:hover {
  background-color: #2980b9;
}
</style>
