<template>
  <section class="auth-page">
    <AuthCard
      title="Crear cuenta"
      subtitle="Regístrate en SeekGym para guardar reseñas y seguir gimnasios."
    >
      <form class="auth-form" @submit.prevent="onSubmit">
        <AuthInput
          v-model="formData.username"
          label="Usuario"
          placeholder="Elige un usuario"
        />

        <AuthInput
          v-model="formData.email"
          label="Email"
          type="email"
          placeholder="Introduce tu email"
        />

        <AuthInput
          v-model="formData.password"
          label="Contraseña"
          type="password"
          placeholder="Mínimo 8 caracteres"
        />

        <p v-if="message" :class="messageClass">
          {{ message }}
        </p>

        <button class="auth-form__button" type="submit" :disabled="loading">
          {{ loading ? 'Creando cuenta...' : 'Registrarse' }}
        </button>

        <p class="auth-form__footer">
          ¿Ya tienes cuenta?
          <router-link to="/login">Inicia sesión</router-link>
        </p>
      </form>
    </AuthCard>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/userStore'
import AuthCard from '../components/AuthCard.vue'
import AuthInput from '../components/AuthInput.vue'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const message = ref('')
const isError = ref(false)

const formData = ref({
  username: '',
  email: '',
  password: '',
})

const messageClass = computed(() =>
  isError.value
    ? 'auth-form__message auth-form__message--error'
    : 'auth-form__message auth-form__message--success'
)

async function onSubmit() {
  loading.value = true
  message.value = ''
  isError.value = false

  const result = await userStore.register(
    formData.value.username,
    formData.value.password,
    formData.value.email
  )

  loading.value = false

  if (result.isOk) {
    message.value = 'Usuario registrado correctamente'
    setTimeout(() => router.push('/login'), 1000)
  } else {
    isError.value = true
    message.value = 'No se pudo registrar el usuario'
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

.auth-form__message--success {
  color: #16a34a;
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