<template>
  <div>
    <h1>Login</h1>

    <form @submit.prevent="onSubmit">
      <div>
        <label>Username</label>
        <input v-model="formData.username" type="text" />
      </div>

      <div>
        <label>Password</label>
        <input v-model="formData.password" type="password" />
      </div>

      <button type="submit" :disabled="loading">
        {{ loading ? 'Cargando...' : 'Iniciar sesión' }}
      </button>
    </form>

    <p v-if="message">{{ message }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/userStore'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const message = ref('')

const formData = ref({
  username: '',
  password: '',
})

async function onSubmit() {
  loading.value = true
  message.value = ''

  const result = await userStore.login(
    formData.value.username,
    formData.value.password
  )

  loading.value = false

  if (result.isOk) {
    router.push('/')
  } else {
    message.value = result.message
  }
}
</script>