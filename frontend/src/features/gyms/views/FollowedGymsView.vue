<template>
  <div class="page-container">
    <div class="page-box">
      <div class="top-bar">
        <button class="back-btn" @click="router.push('/home')">← Volver</button>
      </div>

      <h1 class="title">Gimnasios que sigues</h1>

      <p v-if="loading" class="info">Cargando...</p>
      <p v-else-if="!gyms.length" class="info">
        No sigues ningún gimnasio todavía. Entra en la ficha de un gimnasio y pulsa <strong>+ Seguir</strong>.
      </p>

      <div v-else class="gyms-list">
        <GymCard v-for="gym in gyms" :key="gym.id" :gym="gym" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getFollowedGymsService } from '../services/gymsService'
import GymCard from '../components/GymCard.vue'

const router = useRouter()
const gyms = ref([])
const loading = ref(true)

onMounted(async () => {
  const response = await getFollowedGymsService()
  if (response?.status === 200) {
    gyms.value = response.data
  }
  loading.value = false
})
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #f9fafb;
  padding: 40px 20px;
}

.page-box {
  max-width: 1100px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
}

.top-bar {
  margin-bottom: 20px;
}

.back-btn {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  font-size: 0.95rem;
  padding: 0;
}

.back-btn:hover {
  color: #111827;
}

.title {
  margin-bottom: 24px;
}

.info {
  color: #6b7280;
}

.gyms-list {
  display: grid;
  gap: 16px;
}
</style>
