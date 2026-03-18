<template>
  <section class="auth-page">
    <AuthCard
      title="Iniciar sesión"
      subtitle="Accede a SeekGym para comparar gimnasios y seguir tus favoritos."
    >
      <form class="auth-form" @submit.prevent="onSubmit">
        <AuthInput
          v-model="formData.username"
          label="Usuario"
          placeholder="Introduce tu usuario"
        />

        <AuthInput
          v-model="formData.password"
          label="Contraseña"
          type="password"
          placeholder="Introduce tu contraseña"
        />

        <p v-if="message" class="auth-form__message auth-form__message--error">
          {{ message }}
        </p>

        <button class="auth-form__button" type="submit" :disabled="loading">
          {{ loading ? 'Cargando...' : 'Iniciar sesión' }}
        </button>

        <p class="auth-form__footer">
          ¿No tienes cuenta?
          <router-link to="/register">Regístrate</router-link>
        </p>
      </form>
    </AuthCard>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/userStore'
import AuthCard from '../components/AuthCard.vue'
import AuthInput from '../components/AuthInput.vue'

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

<style scoped>
.auth-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: linear-gradient(180deg, #fff7ed 0%, #ffffff 40%);
  padding: 24px;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.auth-form__button {
  height: 46px;
  border: none;
  border-radius: 12px;
  background: #f97316;
  color: white;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.auth-form__button:hover {
  background: #ea580c;
}

.auth-form__button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.auth-form__message {
  margin: 0;
  font-size: 14px;
}

.auth-form__message--error {
  color: #dc2626;
}

.auth-form__footer {
  margin: 0;
  font-size: 14px;
  color: #6b7280;
}

.auth-form__footer a {
  color: #f97316;
  font-weight: 600;
  text-decoration: none;
}
</style>