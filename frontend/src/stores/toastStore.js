import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useToastStore = defineStore('toast', () => {
  const message = ref('')
  const type = ref('success')
  const visible = ref(false)
  let timer = null

  // muestra el toast y lo esconde solo a los 3 segundos
  function show(msg, toastType = 'success') {
    message.value = msg
    type.value = toastType
    visible.value = true
    // reseteamos el timer por si ya había uno corriendo
    clearTimeout(timer)
    timer = setTimeout(() => { visible.value = false }, 3000)
  }

  // para cerrarlo manualmente si hace falta
  function hide() {
    visible.value = false
  }

  return { message, type, visible, show, hide }
})
