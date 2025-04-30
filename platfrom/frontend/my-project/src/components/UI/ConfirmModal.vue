<template>
  <div
    v-if="show"
    class="modal-overlay"
  >
    <div class="modal-window">
      <h3>{{ title }}</h3>
      <p>{{ message }}</p>
      <div class="modal-actions">
        <button
          class="btn cancel"
          @click="$emit('cancel')"
        >
          {{ cancelText }}
        </button>
        <button
          class="btn confirm"
          @click="$emit('confirm')"
        >
          {{ confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>
  
  <script>
  export default {
    name: "ConfirmModal",
    props: {
      show: Boolean,
      title: {
        type: String,
        default: "Вы уверены?",
      },
      message: {
        type: String,
        default: "Это действие нельзя отменить.",
      },
      cancelText: {
        type: String,
        default: "Отмена",
      },
      confirmText: {
        type: String,
        default: "Подтвердить",
      },
    },
  };
  </script>
  
  <style scoped>
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }
  .modal-window {
    background: white;
    padding: 24px;
    border-radius: 10px;
    width: 400px;
    max-width: 90%;
    box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    text-align: center;
  }
  .modal-window h3 {
    margin-top: 0;
  }
  .modal-actions {
    margin-top: 20px;
    display: flex;
    justify-content: space-between;
  }
  .modal-actions .btn {
    padding: 10px 20px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: bold;
  }
  .modal-actions .cancel {
    background: #bdc3c7;
    color: white;
  }
  .modal-actions .confirm {
    background: #e74c3c;
    color: white;
  }
  .modal-actions .cancel:hover {
    background: #95a5a6;
  }
  .modal-actions .confirm:hover {
    background: #c0392b;
  }
  </style>
  