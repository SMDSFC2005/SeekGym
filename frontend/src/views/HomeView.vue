<template>
  <div class="home">
    <h1>SeekGym</h1>
    <p>Proyecto arrancado correctamente.</p>

    <p v-if="userStore.isAuthenticated">
      Usuario autenticado: {{ userStore.user?.username }}
    </p>

    <button v-if="userStore.isAuthenticated" @click="onLogout">
      Cerrar sesión
    </button>

    <router-link v-else to="/login">Ir al login</router-link>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '@/features/auth/store/userStore'

const router = useRouter()
const userStore = useUserStore()

function onLogout() {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.home {
  min-height: 100vh;
  display: grid;
  place-content: center;
  gap: 12px;
  text-align: center;
}

button {
  height: 42px;
  border: none;
  border-radius: 10px;
  background: #f97316;
  color: white;
  padding: 0 18px;
  cursor: pointer;
}
</style>