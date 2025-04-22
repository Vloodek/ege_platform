// src/composables/useTestSession.js
import { ref, computed, watch, onBeforeUnmount } from 'vue'
import axios from 'axios'

export function useTestSession(config) {
  // --- входные параметры конфигурации ---
  //   config.startUrl:      `/testing/start` или `/homework_tests/${id}/start`
  //   config.sessionUrl:    `/testing/session` или `/homework_tests/session`
  //   config.answerUrl:     `/testing/submit_answer` или `/homework_tests/session/{sid}/answer`
  //   config.completeUrl:   `/testing/complete` или `/homework_tests/session/{sid}/complete`
  //   config.resultsUrl:    `/testing/results`   или `/homework_tests/session/{sid}/results`
  //   config.sseTimerUrl:   `/sse/timer?session_id={sid}`
  //   config.storageKey:    'testSessionId' или 'homeworkSessionId'

  const sessionId = ref(localStorage.getItem(config.storageKey) || null)
  const taskIds   = ref([])
  const tasksMap  = ref({})
  const answers   = ref({})
  const score     = ref(0)
  const testFinished = ref(false)
  const currentTaskIndex = ref(0)
  const remainingTime    = ref(0)
  let   timerSource      = null

  const task      = computed(() => tasksMap.value[currentTaskId.value] || null)
  const loading   = ref(true)
  const userAnswer= ref('')
  const showSolution = ref(false)
  const solutions = ref({})

  const currentTaskId = computed(() => taskIds.value[currentTaskIndex.value])

  // при смене currentTaskId грузим задачу из tasksMap
  watch(currentTaskId, async () => {
    loading.value = true
    userAnswer.value = answers.value[currentTaskId.value] || ''
    loading.value = false
  }, { immediate: true })

  // --- инициализация сессии ---
  async function init(testId = null) {
    // если нет в localStorage — стартуем новую
    if (!sessionId.value) {
      const form = new FormData()
      if (testId !== null) form.append('test_id', testId.toString())
      form.append('user_id', JSON.parse(localStorage.getItem('user')).userId.toString())

      const res = await axios.post(config.startUrl, form)
      sessionId.value = res.data.session_id || res.data.attempt_id
      localStorage.setItem(config.storageKey, sessionId.value)
    }

    // получаем данные сессии
    const resSession = await axios.get(`${config.sessionUrl}/${sessionId.value}`)
    // ожидаем: resSession.data.tasks для домашки или task_ids/answers для тестов
    if (resSession.data.tasks) {
      // --- домашка ---
      taskIds.value = resSession.data.tasks.map(t => t.id)
      const base = window.location.origin
      resSession.data.tasks.forEach(t => {
        t.files = (t.files||[]).map(p => `${base}/${p.replace(/\\/g,'/')}`)
        tasksMap.value[t.id] = t
      })
      remainingTime.value = resSession.data.remaining_time
      // duration можно тоже сохранить, если нужно
    } else {
      // --- тесты ---
      taskIds.value = resSession.data.task_ids
      answers.value = resSession.data.answers
      remainingTime.value = resSession.data.expires_at
      // и т. д.
    }

    // запустим таймер SSE
    startTimer()
  }

  function startTimer() {
    const url = config.sseTimerUrl.replace('{sid}', sessionId.value)
    timerSource = new EventSource(`${axios.defaults.baseURL}${url}`, { withCredentials: true })
    timerSource.onmessage = e => {
      if (e.data === 'Test finished') {
        remainingTime.value = 0
        finishTest()
      } else {
        const secs = parseInt(e.data, 10)
        if (!isNaN(secs)) remainingTime.value = secs
      }
    }
  }

  async function submitAnswer() {
    if (testFinished.value) return
    answers.value[currentTaskId.value] = userAnswer.value

    // для домашки — JSON, для тестов — FormData
    const payload = 
      config.answerUrl.includes('submit_answer')
        ? new URLSearchParams({
            session_id: sessionId.value,
            task_id: currentTaskId.value,
            answer: userAnswer.value
          })
        : { task_id: currentTaskId.value, answer: userAnswer.value }

    await axios.post(
      config.answerUrl.replace('{sid}', sessionId.value),
      payload,
      config.answerUrl.includes('submit_answer')
        ? { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
        : {}
    )

    userAnswer.value = ''
    if (currentTaskIndex.value < taskIds.value.length - 1) currentTaskIndex.value++
  }

  async function finishTest() {
    timerSource.close()
    testFinished.value = true
    await axios.post(config.completeUrl.replace('{sid}', sessionId.value))
    const res = await axios.get(config.resultsUrl.replace('{sid}', sessionId.value))
    score.value = res.data.score
    if (res.data.solutions) solutions.value = res.data.solutions
  }

  onBeforeUnmount(() => {
    if (timerSource) timerSource.close()
  })

  return {
    sessionId, taskIds, tasksMap,
    answers, score, testFinished,
    currentTaskIndex, remainingTime,
    task, loading, userAnswer,
    showSolution, solutions,

    formattedTime: computed(() => {
      const m = String(Math.floor(remainingTime.value/60)).padStart(2,'0')
      const s = String(remainingTime.value%60).padStart(2,'0')
      return `${m}:${s}`
    }),

    init, submitAnswer, finishTest,
    goToTask: idx => currentTaskIndex.value = idx,
    prevTask:  () => { if (currentTaskIndex.value>0) currentTaskIndex.value-- },
    nextTask:  () => { if (currentTaskIndex.value<taskIds.value.length-1) currentTaskIndex.value++ },
  }
}
