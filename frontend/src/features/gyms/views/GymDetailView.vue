<template>
  <div class="detail-container">
    <div class="detail-box">
      <p v-if="detailLoading" class="info-message">Cargando gimnasio...</p>
      <p v-else-if="detailError" class="error">{{ detailError }}</p>

      <template v-else-if="gymDetail">
        <h1 class="title">{{ gymDetail.name }}</h1>

        <p class="subtitle">
          {{ gymDetail.municipality }} · {{ gymDetail.province }} · {{ gymDetail.postal_code }} · {{ gymDetail.address }}
        </p>

        <div class="meta">
          <span>⭐ {{ gymDetail.rating }}</span>
          <span>{{ gymDetail.price_per_month }} €/mes</span>
          <span>{{ gymDetail.reviews_count }} reseñas</span>
        </div>

        <p v-if="gymDetail.description" class="description">
          {{ gymDetail.description }}
        </p>

        <div class="stats-grid">
          <div class="stat-card">
            <span class="stat-label">Ocupación actual</span>
            <strong>
              {{ gymDetail.current_occupancy !== null ? gymDetail.current_occupancy + '%' : '—' }}
            </strong>
            <p>
              {{ getStatusLabel(gymDetail.current_status) }}
            </p>
          </div>

          <div class="stat-card">
            <span class="stat-label">Mejor hora hoy</span>
            <strong>
              {{ gymDetail.best_time_today ? gymDetail.best_time_today.label : '—' }}
            </strong>
            <p v-if="gymDetail.best_time_today">
              {{ gymDetail.best_time_today.occupancy_percent }}% ocupado
            </p>
            <p v-else>Sin datos</p>
          </div>
        </div>

        <div class="timeline-section">
          <h2>Timeline del día</h2>

          <div class="timeline-list">
            <div
              v-for="item in gymDetail.today_timeline"
              :key="item.hour"
              class="timeline-row"
            >
              <span>{{ item.label }}</span>
              <span>
                {{ item.occupancy_percent !== null ? item.occupancy_percent + '%' : '—' }}
              </span>
              <span>{{ getStatusLabel(item.status) }}</span>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useGymsStore } from '../store/gymStore'

const route = useRoute()
const gymsStore = useGymsStore()

const { gymDetail, detailLoading, detailError } = storeToRefs(gymsStore)

function getStatusLabel(status) {
  if (status === 'GOOD') return 'Buen momento'
  if (status === 'MEDIUM') return 'Con espera'
  if (status === 'AVOID') return 'Mejor evitar'
  return 'Sin datos'
}

onMounted(async () => {
  await gymsStore.fetchGymDetail(route.params.slug)
})
</script>

<style scoped>
.detail-container {
  min-height: 100vh;
  background: #f9fafb;
  padding: 40px 20px;
}

.detail-box {
  max-width: 1100px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
}

.title {
  margin-bottom: 8px;
}

.subtitle {
  color: #6b7280;
  margin-bottom: 12px;
}

.meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  color: #374151;
  margin-bottom: 20px;
}

.description {
  color: #4b5563;
  margin-bottom: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.stat-card {
  background: #f9fafb;
  border-radius: 12px;
  padding: 16px;
}

.stat-label {
  display: block;
  margin-bottom: 6px;
  color: #6b7280;
  font-size: 0.9rem;
}

.timeline-section h2 {
  margin-bottom: 16px;
}

.timeline-list {
  display: grid;
  gap: 10px;
}

.timeline-row {
  display: grid;
  grid-template-columns: 100px 120px 1fr;
  gap: 16px;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
}

.info-message {
  color: #4b5563;
}

.error {
  color: red;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .timeline-row {
    grid-template-columns: 1fr;
  }
}
</style>