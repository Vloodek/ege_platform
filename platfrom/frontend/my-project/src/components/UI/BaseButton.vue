<template>
    <button :class="buttonClasses" @click="$emit('click')">
      <slot></slot>
    </button>
  </template>
  
  <script>
  export default {
    props: {
      color: {
        type: String,
        default: "green", // По умолчанию белая кнопка
        validator: (value) => ["green", "white","gray"].includes(value),
      },
    },
    computed: {
      buttonClasses() {
        return ["lesson-button", this.color];
      },
    },
  };
  </script>
  
  <style scoped>
  .lesson-button {
    padding: 10px;
    font-size: 16px;
    border: 2px solid #115544;
    border-radius: 20px;
    cursor: pointer;
    text-align: center;
    height: 54px;
    font-family: "Navigo", sans-serif;
    font-weight: 300;
    transition: opacity 0.3s ease;
    min-width: 150px;
  }
  
  .lesson-button.green {
    background-color: #115544;
    color: #fff;
  }
  
  .lesson-button.white {
    background-color: #fff;
    color: #000;
  }
  
  .lesson-button:hover {
    opacity: 0.8;
  }
  .lesson-button.gray {
    background-color: #b2b2b2;
    color: #000;
  }
  </style>
  