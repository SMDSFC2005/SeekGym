<template>
  <div class="home-container">
    <div class="home-box">
      <h2 class="title">¿Cuándo entrenar sin esperar máquinas?</h2>
      <p class="subtitle">
        Consulta el estado actual de tu gym y descubre cuál es la mejor hora de hoy para entrenar.
      </p>

      <div class="filters">
        <div class="filter-group">
          <label class="label">Ciudad</label>
          <input v-model="filters.city" type="text" class="input" />
        </div>

        <div class="filter-group">
          <label class="label">Código postal</label>
          <select v-model="filters.postal_code" class="input">
            <option value="">Todos</option>
            <option value="41020">41020</option>
            <option value="41019">41019</option>
          </select>
        </div>

        <button class="filter-button" @click="onApplyFilters" :disabled="loading">
          Aplicar
        </button>
      </div>

      <p v-if="loading" class="info-message">Cargando gimnasios...</p>
      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="!loading && !error && gyms.length === 0" class="info-message">
        No hay gimnasios para esos filtros.
      </p>

      <div v-if="!loading && gyms.length > 0" class="gyms-list">
        <div v-for="gym in gyms" :key="gym.id" class="gym-card">
          <div class="gym-header">
            <div>
              <h3>{{ gym.name }}</h3>
              <p class="gym-location">{{ gym.city }} · {{ gym.postal_code }}</p>
            </div>

            <span class="status" :class="getStatusClass(gym.current_status)">
              {{ getStatusLabel(gym.current_status) }}
            </span>
          </div>

          <div class="gym-meta">
            <span>⭐ {{ gym.rating }}</span>
            <span>{{ gym.price_per_month }} €/mes</span>
          </div>

          <p class="gym-address">{{ gym.address }}</p>

          <div class="gym-stats">
            <div class="stat-box">
              <span class="stat-label">Ocupación actual</span>
              <strong>
                {{ gym.current_occupancy !== null ? gym.current_occupancy + '%' : '—' }}
              </strong>
            </div>

            <div class="stat-box">
              <span class="stat-label">Mejor hora hoy</span>
              <strong>
                {{ gym.best_time_today ? gym.best_time_today.label : '—' }}
              </strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useGymsStore } from '../store/gymStore'

const gymsStore = useGymsStore()
const { gyms, loading, error, currentFilters } = storeToRefs(gymsStore)

const filters = reactive({
  city: 'Sevilla',
  postal_code: '',
})

function getStatusLabel(status) {
  if (status === 'GOOD') return 'Buen momento'
  if (status === 'MEDIUM') return 'Con espera'
  if (status === 'AVOID') return 'Mejor evitar'
  return 'Sin datos'
}

function getStatusClass(status) {
  if (status === 'GOOD') return 'status-good'
  if (status === 'MEDIUM') return 'status-medium'
  if (status === 'AVOID') return 'status-avoid'
  return ''
}

async function onApplyFilters() {
  await gymsStore.fetchHomeGyms({
    city: filters.city,
    postal_code: filters.postal_code,
  })
}

onMounted(async () => {
  filters.city = currentFilters.value.city
  filters.postal_code = currentFilters.value.postal_code

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

.filters {
  display: grid;
  grid-template-columns: 1fr 220px 120px;
  gap: 16px;
  align-items: end;
  margin-bottom: 24px;
}

.filter-group {
  display: flex;
  flex-direction: column;
}

.label {
  font-weight: 600;
  margin-bottom: 6px;
}

.input {
  height: 42px;
  padding: 0 12px;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  background: white;
}

.filter-button {
  height: 42px;
  border: none;
  border-radius: 10px;
  background: #111827;
  color: white;
  cursor: pointer;
}

.filter-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

.gym-card {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  background: #fff;
}

.gym-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.gym-header h3 {
  margin: 0;
}

.gym-location {
  margin-top: 4px;
  color: #6b7280;
}

.status {
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 600;
}

.status-good {
  background: #dcfce7;
  color: #166534;
}

.status-medium {
  background: #fef3c7;
  color: #92400e;
}

.status-avoid {
  background: #fee2e2;
  color: #991b1b;
}

.gym-meta {
  display: flex;
  gap: 16px;
  margin-top: 12px;
  color: #374151;
}

.gym-address {
  margin-top: 10px;
  color: #4b5563;
}

.gym-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-top: 18px;
}

.stat-box {
  background: #f9fafb;
  border-radius: 10px;
  padding: 14px;
}

.stat-label {
  display: block;
  color: #6b7280;
  margin-bottom: 6px;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .filters {
    grid-template-columns: 1fr;
  }

  .gym-stats {
    grid-template-columns: 1fr;
  }

  .gym-header {
    flex-direction: column;
  }
}
</style>