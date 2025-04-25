<template>
  <button 
    :class="buttonClasses" 
    @click="$emit('click')"
    @mouseenter="hover = true" 
    @mouseleave="hover = false"
  >
    <slot></slot>
  </button>
</template>

<script>
export default {
  name: "BaseButton",
  emits: ['click'],  // добавляем объявление эмитируемых событий
  props: {
    color: {
      type: String,
      default: "blue",
      validator: (value) => ["blue", "white", "gray", "green"].includes(value),
    },
  },
  data() {
    return {
      hover: false, // Состояние для hover
    };
  },
  computed: {
    buttonClasses() {
      return [
        "lesson-button", 
        this.color, 
        { hover: this.hover }, // Добавляем класс hover, если состояние true
      ];
    },
  },
};
</script>

<style scoped>
.lesson-button {
  padding: 10px;
  font-size: 16px;
  border: 2px solid #56AEF6;
  border-radius: 20px;
  cursor: pointer;
  text-align: center;
  height: 54px;
  font-family: "Navigo", sans-serif;
  font-weight: 300;
  transition: opacity 0.3s ease;
  min-width: 150px;
  cursor: pointer;
}

.lesson-button.green {
  background-color: #56AEF6;
  color: #fff;
}

.lesson-button.white {
  background-color: #fff;
  color: #000;
}

.lesson-button.gray {
  background-color: #b2b2b2;
  color: #000;
}

/* Эффект hover */
.lesson-button:hover {
  opacity: 0.8;
}

.lesson-button.green.hover {
  background-color: #b8dfff; /* Поменял цвет при hover на зелёную кнопку */
}

.lesson-button.white.hover {
  background-color: #f0f0f0; /* Можете поменять для белой кнопки */
}

.lesson-button.gray.hover {
  background-color: #e0e0e0; /* Можете поменять для серой кнопки */
}
</style>
