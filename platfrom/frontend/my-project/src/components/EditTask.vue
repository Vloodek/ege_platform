<template>
    <div id="edit-task">
      <div class="container">
        <!-- Кнопка "Вернуться" -->
        <button class="back-button" @click="confirmBack">Вернуться</button>
  
        <!-- Заголовок редактирования -->
        <h1 class="edit-title">Редактирование задания</h1>
  
        <!-- Форма редактирования задания -->
        <form @submit.prevent="saveTask">
          <!-- Номер задания -->
          <div class="form-group">
            <label for="taskNumber" class="form-label">Выберите номер задания</label>
            <select v-model="task.number" id="taskNumber" class="form-control">
              <option v-for="n in 27" :key="n" :value="n">{{ n }}</option>
            </select>
          </div>
  
          <!-- Текст задания -->
          <div class="form-group">
            <label for="taskText" class="form-label">Текст задания</label>
            <textarea v-model="task.text" id="taskText" class="form-control" placeholder="Введите текст задания"></textarea>
          </div>
  
          <!-- Картинка задания -->
          <div class="form-group">
            <label class="form-label">Добавьте картинку</label>
            <input type="file" @change="handleFileUpload('image')" class="form-control" />
          </div>
  
          <!-- Прикрепленные файлы -->
          <div class="form-group">
            <label class="form-label">Прикрепленные файлы</label>
            <input type="file" @change="handleFileUpload('files')" class="form-control" multiple />
          </div>
  
          <!-- Дедлайн -->
          <div class="form-group">
            <label for="deadline" class="form-label">Выберите дедлайн</label>
            <input type="date" v-model="task.deadline" id="deadline" class="form-control" />
            <button type="button" @click="addDeadline" class="add-deadline">Добавить</button>
          </div>
  
          <!-- Кнопка для сохранения задания -->
          <button type="submit" class="save-button">Сохранить</button>
        </form>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        task: {
          number: null, // Номер задания
          text: '', // Текст задания
          image: null, // Картинка задания
          files: [], // Прикрепленные файлы
          deadline: '', // Дедлайн
        },
        hasUnsavedChanges: false, // Для отслеживания изменений
      };
    },
    methods: {
      // Обработка загрузки файлов
      handleFileUpload(type) {
        if (type === 'image') {
          const file = this.$refs.image.files[0];
          this.task.image = file;
        } else if (type === 'files') {
          const files = this.$refs.files.files;
          this.task.files = Array.from(files);
        }
        this.hasUnsavedChanges = true;
      },
  
      // Добавление дедлайна
      addDeadline() {
        if (this.task.deadline) {
          this.hasUnsavedChanges = true;
        }
      },
  
      // Подтверждение возвращения на предыдущую страницу
      confirmBack() {
        if (this.hasUnsavedChanges) {
          if (window.confirm('Убедитесь, что все данные не будут сохранены. Вы уверены?')) {
            this.$router.push('/tasks');
          }
        } else {
          this.$router.push('/tasks');
        }
      },
  
      // Сохранение задания
      saveTask() {
        // Логика сохранения задания
        console.log('Задание сохранено:', this.task);
        this.hasUnsavedChanges = false;
      },
    },
  };
  </script>
  
  <style scoped>
  #edit-task {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    background-color: #f5f5f5;
    padding: 20px;
  }
  
  .container {
    max-width: 800px;
    margin: 0 auto;
    background-color: #fff;
    padding: 20px;
    border-radius: 8px;
  }
  
  .back-button {
    background-color: #f44336;
    color: white;
    padding: 10px 20px;
    border-radius: 5px;
    cursor: pointer;
    margin-bottom: 20px;
  }
  
  .back-button:hover {
    background-color: #d32f2f;
  }
  
  .edit-title {
    font-size: 28px;
    color: #333;
    text-align: left;
    margin-bottom: 20px;
  }
  
  .form-group {
    margin-bottom: 20px;
  }
  
  .form-label {
    font-size: 18px;
    color: #555;
    display: block;
    margin-bottom: 8px;
  }
  
  .form-control {
    width: 100%;
    padding: 10px;
    border-radius: 5px;
    border: 1px solid #ccc;
  }
  
  textarea.form-control {
    height: 150px;
  }
  
  .add-deadline {
    margin-top: 10px;
    background-color: #4CAF50;
    color: white;
    padding: 10px 20px;
    border-radius: 5px;
    cursor: pointer;
  }
  
  .add-deadline:hover {
    background-color: #45a049;
  }
  
  .save-button {
    background-color: #4CAF50;
    color: white;
    padding: 10px 20px;
    border-radius: 5px;
    cursor: pointer;
    width: 100%;
    margin-top: 20px;
  }
  
  .save-button:hover {
    background-color: #45a049;
  }
  </style>
  