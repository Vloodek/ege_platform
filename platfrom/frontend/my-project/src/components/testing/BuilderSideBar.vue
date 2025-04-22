<template>
  <div class="sidebar builder">
    <!-- Время -->
    <div class="time-config" v-if="mode==='build'">
      <label>Время (мин):</label>
      <input type="number" v-model.number="localDuration" min="1" @change="emitDuration" />
    </div>
    <div class="time-config" v-else>
      <label>Время:</label>
      <div class="timer-display">{{ timerDisplay }}</div>
    </div>

    <!-- Количество вопросов -->
    <div class="count-config" v-if="mode==='build'">
      <label>Вопросов:</label>
      <input type="number" v-model.number="localCount" min="1" @change="emitCount" />
    </div>
    <div class="count-config" v-else>
      <label>Всего:</label>
      <div class="count-display">{{ localCount }}</div>
    </div>

    <!-- Сетка вопросов -->
    <div
  v-for="n in localCount"
  :key="n"
  class="q-square"
  :class="{
    active: n - 1 === currentIndex,
    correct: results[n - 1] === true,
    incorrect: results[n - 1] === false,
  }"
  @click="$emit('select', n - 1)"
>
  {{ n }}
</div>


    <!-- Навигация -->
    <div class="nav-buttons">
      <button @click="$emit('prev')" :disabled="currentIndex===0">←</button>
      <button @click="$emit('next')" :disabled="currentIndex>=localCount-1">→</button>
    </div>

    <!-- Кнопки выхода и завершения (только в сессии) -->
    <div v-if="mode==='session'" class="exit-button">
      <button @click="$emit('exit')">{{ exitLabel || 'Выйти' }}</button>
      <!-- НОВАЯ КНОПКА -->
      <button class="complete-test-btn" @click="$emit('complete')">
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
    results: { type: Object, default: () => ({}) },
    mode:          { type: String, default: 'build' },  // 'build' | 'session'
    timerDisplay:  { type: String, default: '00:00' },
    exitLabel:     { type: String, default: '' },
  },
  data() {
    return {
      localDuration: this.duration,
      localCount:    this.count,
    };
  },
  watch: {
    duration(v) { this.localDuration = v },
    count(v)    { this.localCount = v },
  },
  methods: {
    emitDuration() {
      if (this.localDuration < 1) this.localDuration = 1;
      this.$emit("update:duration", this.localDuration);
    },
    emitCount() {
      if (this.localCount < 1) this.localCount = 1;
      this.$emit("update:count", this.localCount);
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
.questions-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  grid-gap: 6px;
  margin: 16px 0;
}
.q-square {
  background: #eee;
  border: 1px solid #115544;
  border-radius: 4px;
  text-align: center;
  line-height: 32px;
  cursor: pointer;
}
.q-square.active {
  background: #115544;
  color: #fff;
}
.nav-buttons {
  display: flex;
  justify-content: space-between;
}
.nav-buttons button {
  background: #115544;
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
.exit-button {
  margin-top: 16px;
  text-align: center;
}

.exit-button button {
  background: #900;
  color: #fff;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.complete-test-btn {
  background: #115544;
  margin-top: 8px;
}

.complete-test-btn:hover {
  opacity: 0.9;
}
.q-square.correct {
  background-color: #4caf50;
  color: white;
}
.q-square.incorrect {
  background-color: #f44336;
  color: white;
}

</style>
