<template>
  <div class="home-container">
    <div class="home-box">
      <h2 class="title">¿Cuándo entrenar sin esperar máquinas?</h2>
      <p class="subtitle">
        Consulta el estado actual de tu gym y descubre cuál es la mejor hora de hoy para entrenar.
      </p>

      <GymFilters
        :city="filters.city"
        :postal-code="filters.postal_code"
        @apply="onApplyFilters"
      />

      <p v-if="loading" class="info-message">Cargando gimnasios...</p>
      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="!loading && !error && gyms.length === 0" class="info-message">
        No hay gimnasios para esos filtros.
      </p>

      <div v-if="!loading && gyms.length > 0" class="gyms-list">
        <GymCard
          v-for="gym in gyms"
          :key="gym.id"
          :gym="gym"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useGymsStore } from '../store/gymStore'
import GymFilters from '../components/GymFilters.vue'
import GymCard from '../components/GymCard.vue'

const gymsStore = useGymsStore()
const { gyms, loading, error, currentFilters } = storeToRefs(gymsStore)

const filters = reactive({
  city: 'Sevilla',
  postal_code: '',
})

async function onApplyFilters(newFilters) {
  filters.city = newFilters.city
  filters.postal_code = newFilters.postal_code

  await gymsStore.fetchHomeGyms({
    city: newFilters.city,
    postal_code: newFilters.postal_code,
  })
}

onMounted(async () => {
  filters.city = currentFilters.value.city || 'Sevilla'
  filters.postal_code = currentFilters.value.postal_code || ''

  await gymsStore.fetchHomeGyms({
    city: filters.city,
    postal_code: filters.postal_code,
  })
})
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  background: #f9fafb;
  padding: 40px 20px;
}

.home-box {
  width: 100%;
  max-width: 1100px;
  background: white;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
}

.title {
  margin-bottom: 10px;
}

.subtitle {
  color: #6b7280;
  margin-bottom: 24px;
}

.info-message {
  color: #4b5563;
  margin-top: 10px;
}

.error {
  color: red;
  margin-top: 10px;
}

.gyms-list {
  display: grid;
  gap: 16px;
  margin-top: 20px;
}
</style>