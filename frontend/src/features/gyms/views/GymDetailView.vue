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

        <img
          v-if="gymDetail.image_url"
          :src="gymDetail.image_url"
          :alt="gymDetail.name"
          class="cover-image"
        />

        <p v-if="gymDetail.description" class="description">
          {{ gymDetail.description }}
        </p>

        <div class="stats-grid">
          <div class="stat-card">
            <span class="stat-label">Ocupación actual</span>

            <strong class="stat-value">
              {{ gymDetail.current_occupancy !== null ? gymDetail.current_occupancy + '%' : '—' }}
            </strong>

            <p class="stat-status">{{ getStatusLabel(gymDetail.current_status) }}</p>

            <div v-if="gymDetail.current_occupancy !== null" class="mini-progress">
              <div
                class="mini-progress-bar"
                :class="getOccupancyClass(gymDetail.current_occupancy)"
                :style="{ width: gymDetail.current_occupancy + '%' }"
              />
            </div>

            <p v-if="gymDetail.confidence !== null" class="muted-text">
              Confianza: {{ gymDetail.confidence }}%
            </p>
          </div>

          <div class="stat-card stat-card--highlight">
            <span class="stat-label">Mejor hora hoy</span>

            <strong class="stat-value">
              {{ gymDetail.best_time_today ? gymDetail.best_time_today.label : '—' }}
            </strong>

            <template v-if="gymDetail.best_time_today">
              <p class="stat-status">
                {{ gymDetail.best_time_today.occupancy_percent }}% ocupado ·
                {{ getStatusLabel(getStatusFromOccupancy(gymDetail.best_time_today.occupancy_percent)) }}
              </p>

              <div class="mini-progress">
                <div
                  class="mini-progress-bar"
                  :class="getOccupancyClass(gymDetail.best_time_today.occupancy_percent)"
                  :style="{ width: gymDetail.best_time_today.occupancy_percent + '%' }"
                />
              </div>

              <p v-if="gymDetail.best_time_today.confidence !== null" class="muted-text">
                Confianza: {{ gymDetail.best_time_today.confidence }}%
              </p>

              <p
                v-if="gymDetail.best_time_today.score !== undefined && gymDetail.best_time_today.score !== null"
                class="muted-text"
              >
                Score: {{ formatScore(gymDetail.best_time_today.score) }}
              </p>

              <p
                v-if="gymDetail.best_time_today.reason"
                class="recommendation-reason"
              >
                {{ gymDetail.best_time_today.reason }}
              </p>
            </template>

            <p v-else class="muted-text">Sin datos</p>
          </div>
        </div>

        <div class="timeline-section">
          <div class="section-header">
            <div>
              <h2>Timeline del día</h2>
              <p class="section-subtitle">
                Vista rápida de ocupación por hora. Se marca la hora actual y la recomendación.
              </p>
            </div>

            <div class="legend">
              <span class="legend-item">
                <span class="legend-dot legend-dot--good"></span>
                Buen momento
              </span>
              <span class="legend-item">
                <span class="legend-dot legend-dot--medium"></span>
                Con espera
              </span>
              <span class="legend-item">
                <span class="legend-dot legend-dot--avoid"></span>
                Mejor evitar
              </span>
            </div>
          </div>

          <div v-if="timelineItems.length" class="timeline-chart">
            <div
              v-for="item in timelineItems"
              :key="item.hour"
              class="timeline-chart-row"
              :class="{
                'timeline-chart-row--current': item.isCurrentHour,
                'timeline-chart-row--best': item.isBestHour,
                'timeline-chart-row--past': item.isPastHour,
              }"
            >
              <div class="timeline-chart-label">
                <span class="timeline-chart-hour">{{ item.label }}</span>

                <div class="timeline-chart-badges">
                  <span
                    class="status-pill"
                    :class="getStatusClass(item.status)"
                  >
                    {{ getStatusLabel(item.status) }}
                  </span>

                  <span v-if="item.isCurrentHour" class="badge badge--current">
                    Ahora
                  </span>

                  <span v-if="item.isBestHour" class="badge badge--best">
                    Recomendada
                  </span>

                  <span v-if="item.isPastHour" class="badge badge--past">
                    Pasada
                  </span>
                </div>
              </div>

              <div class="timeline-chart-bar-area">
                <div class="timeline-chart-bar-bg">
                  <div
                    class="timeline-chart-bar-fill"
                    :class="getOccupancyClass(item.occupancy_percent)"
                    :style="{ width: item.occupancy_percent + '%' }"
                  />
                </div>
              </div>

              <div class="timeline-chart-values">
                <span class="timeline-main-value">{{ item.occupancy_percent }}%</span>
                <span>Conf. {{ item.confidence ?? '—' }}%</span>
              </div>
            </div>
          </div>

          <p v-else class="info-message">No hay timeline disponible.</p>
        </div>

        <div class="timeline-section">
          <h2>Promociones / Ofertas / Novedades</h2>

          <div v-if="gymDetail.announcements?.length" class="announcements-list">
            <article
              v-for="item in gymDetail.announcements"
              :key="item.id"
              class="announcement-card"
            >
              <strong>{{ item.kind }}</strong>
              <h3>{{ item.title }}</h3>
              <p>{{ item.content }}</p>
            </article>
          </div>

          <p v-else class="info-message">No hay publicaciones todavía.</p>
        </div>

        <template v-if="canEdit">
          <div class="manage-section">
            <h2>Editar mi gimnasio</h2>

            <p v-if="saveError" class="error">{{ saveError }}</p>

            <form class="form" @submit.prevent="onSaveGym">
              <div class="field">
                <label>Nombre</label>
                <input v-model="editForm.name" type="text" required />
              </div>

              <div class="field">
                <label>Provincia</label>
                <select v-model="editForm.province_id" required @change="onProvinceChange">
                  <option value="">Selecciona</option>
                  <option v-for="province in provinces" :key="province.id" :value="province.id">
                    {{ province.name }}
                  </option>
                </select>
              </div>

              <div class="field">
                <label>Municipio</label>
                <select v-model="editForm.municipality_id" required :disabled="!editForm.province_id">
                  <option value="">Selecciona</option>
                  <option v-for="municipality in municipalities" :key="municipality.id" :value="municipality.id">
                    {{ municipality.name }}
                  </option>
                </select>
              </div>

              <div class="field">
                <label>Código postal</label>
                <input v-model="editForm.postal_code" type="text" required />
              </div>

              <div class="field">
                <label>Dirección</label>
                <input v-model="editForm.address" type="text" required />
              </div>

              <div class="field">
                <label>Precio mensual</label>
                <input v-model="editForm.price_per_month" type="number" step="0.01" min="0" required />
              </div>

              <div class="field">
                <label>Imagen (URL)</label>
                <input v-model="editForm.image_url" type="url" />
              </div>

              <div class="field field--full">
                <label>Descripción</label>
                <textarea v-model="editForm.description" rows="4"></textarea>
              </div>

              <div class="actions">
                <button type="submit" :disabled="saveLoading">
                  {{ saveLoading ? 'Guardando...' : 'Guardar cambios' }}
                </button>
              </div>
            </form>
          </div>

          <div class="manage-section">
            <h2>Añadir publicación</h2>

            <p v-if="announcementError" class="error">{{ announcementError }}</p>

            <form class="form" @submit.prevent="onCreateAnnouncement">
              <div class="field">
                <label>Tipo</label>
                <select v-model="announcementForm.kind" required>
                  <option value="PROMOCION">Promoción</option>
                  <option value="OFERTA">Oferta</option>
                  <option value="NOVEDAD">Novedad</option>
                </select>
              </div>

              <div class="field field--full">
                <label>Título</label>
                <input v-model="announcementForm.title" type="text" required />
              </div>

              <div class="field field--full">
                <label>Contenido</label>
                <textarea v-model="announcementForm.content" rows="4" required></textarea>
              </div>

              <div class="actions">
                <button type="submit" :disabled="announcementLoading">
                  {{ announcementLoading ? 'Publicando...' : 'Publicar' }}
                </button>
              </div>
            </form>
          </div>
        </template>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, watch } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useGymsStore } from '../store/gymStore'
import { useUserStore } from '../../auth/store/userStore'

const route = useRoute()
const gymsStore = useGymsStore()
const userStore = useUserStore()

const {
  gymDetail,
  myGym,
  detailLoading,
  detailError,
  provinces,
  municipalities,
  saveLoading,
  saveError,
  announcementLoading,
  announcementError,
} = storeToRefs(gymsStore)

const editForm = reactive({
  name: '',
  province_id: '',
  municipality_id: '',
  postal_code: '',
  address: '',
  description: '',
  price_per_month: '',
  image_url: '',
})

const announcementForm = reactive({
  kind: 'PROMOCION',
  title: '',
  content: '',
})

const currentHour = computed(() => new Date().getHours())

const bestHour = computed(() => {
  return gymDetail.value?.best_time_today?.hour ?? null
})

const timelineItems = computed(() => {
  const timeline = gymDetail.value?.today_timeline ?? []

  return timeline
    .filter((item) => item.occupancy_percent !== null)
    .map((item) => ({
      ...item,
      isCurrentHour: item.hour === currentHour.value,
      isBestHour: bestHour.value !== null && item.hour === bestHour.value,
      isPastHour: item.hour < currentHour.value,
    }))
})

const canEdit = computed(() => {
  return (
    userStore.user &&
    userStore.user.rol === 'GIMNASIO' &&
    userStore.user.estado_gym === 'APROBADO' &&
    myGym.value &&
    gymDetail.value &&
    myGym.value.slug === gymDetail.value.slug
  )
})

function getStatusLabel(status) {
  if (status === 'GOOD') return 'Buen momento'
  if (status === 'MEDIUM') return 'Con espera'
  if (status === 'AVOID') return 'Mejor evitar'
  return 'Sin datos'
}

function getStatusFromOccupancy(occupancyPercent) {
  if (occupancyPercent === null || occupancyPercent === undefined) return null
  if (occupancyPercent < 40) return 'GOOD'
  if (occupancyPercent < 70) return 'MEDIUM'
  return 'AVOID'
}

function getStatusClass(status) {
  if (status === 'GOOD') return 'status-pill--good'
  if (status === 'MEDIUM') return 'status-pill--medium'
  if (status === 'AVOID') return 'status-pill--avoid'
  return ''
}

function getOccupancyClass(occupancyPercent) {
  if (occupancyPercent === null || occupancyPercent === undefined) return 'bar-fill--empty'
  if (occupancyPercent < 40) return 'bar-fill--good'
  if (occupancyPercent < 70) return 'bar-fill--medium'
  return 'bar-fill--avoid'
}

function formatScore(score) {
  return Number(score).toFixed(3)
}

function fillEditForm() {
  if (!gymDetail.value) return

  editForm.name = gymDetail.value.name || ''
  editForm.province_id = gymDetail.value.province_id || ''
  editForm.municipality_id = gymDetail.value.municipality_id || ''
  editForm.postal_code = gymDetail.value.postal_code || ''
  editForm.address = gymDetail.value.address || ''
  editForm.description = gymDetail.value.description || ''
  editForm.price_per_month = gymDetail.value.price_per_month || ''
  editForm.image_url = gymDetail.value.image_url || ''
}

async function onProvinceChange() {
  editForm.municipality_id = ''
  gymsStore.resetMunicipalities()

  if (editForm.province_id) {
    await gymsStore.fetchMunicipalities(editForm.province_id)
  }
}

async function onSaveGym() {
  const result = await gymsStore.updateGym(route.params.slug, {
    name: editForm.name,
    province_id: editForm.province_id,
    municipality_id: editForm.municipality_id,
    postal_code: editForm.postal_code,
    address: editForm.address,
    description: editForm.description,
    price_per_month: editForm.price_per_month,
    image_url: editForm.image_url,
  })

  if (result.isOk) {
    fillEditForm()
  }
}

async function onCreateAnnouncement() {
  const result = await gymsStore.createAnnouncement(route.params.slug, {
    kind: announcementForm.kind,
    title: announcementForm.title,
    content: announcementForm.content,
  })

  if (result.isOk) {
    announcementForm.kind = 'PROMOCION'
    announcementForm.title = ''
    announcementForm.content = ''
  }
}

watch(gymDetail, async (value) => {
  if (!value) return

  fillEditForm()

  if (canEdit.value && value.province_id) {
    await gymsStore.fetchMunicipalities(value.province_id)
  }
})

onMounted(async () => {
  await gymsStore.fetchGymDetail(route.params.slug)
  await gymsStore.fetchProvinces()

  if (userStore.user?.rol === 'GIMNASIO' && userStore.user?.estado_gym === 'APROBADO') {
    await gymsStore.fetchMyGym()
  }

  if (gymDetail.value?.province_id) {
    await gymsStore.fetchMunicipalities(gymDetail.value.province_id)
  }

  fillEditForm()
})
</script>

<style scoped>
.detail-container {
  min-height: 100vh;
  background: #f3f4f6;
  padding: 40px 20px;
}

.detail-box {
  max-width: 1100px;
  margin: 0 auto;
  background: #ffffff;
  border-radius: 18px;
  padding: 32px;
  box-shadow: 0 12px 35px rgba(15, 23, 42, 0.08);
}

.title {
  margin: 0 0 8px;
  font-size: 2rem;
  color: #111827;
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

.cover-image {
  width: 100%;
  max-height: 360px;
  object-fit: cover;
  border-radius: 16px;
  margin-bottom: 20px;
}

.description {
  color: #4b5563;
  margin-bottom: 24px;
  line-height: 1.6;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.stat-card {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 18px;
}

.stat-card--highlight {
  border: 1px solid #dbeafe;
  background: linear-gradient(180deg, #f8fbff 0%, #f3f8ff 100%);
}

.stat-label {
  display: block;
  margin-bottom: 8px;
  color: #6b7280;
  font-size: 0.9rem;
  font-weight: 600;
}

.stat-value {
  display: block;
  font-size: 1.8rem;
  color: #111827;
  margin-bottom: 8px;
}

.stat-status {
  color: #374151;
  font-weight: 500;
}

.mini-progress {
  width: 100%;
  height: 10px;
  background: #e5e7eb;
  border-radius: 999px;
  overflow: hidden;
  margin: 12px 0 10px;
}

.mini-progress-bar {
  height: 100%;
  border-radius: 999px;
}

.muted-text {
  color: #6b7280;
  font-size: 0.92rem;
  margin-top: 6px;
}

.recommendation-reason {
  margin-top: 10px;
  color: #374151;
  line-height: 1.5;
}

.timeline-section,
.manage-section {
  margin-top: 36px;
}

.timeline-section h2,
.manage-section h2 {
  margin: 0 0 10px;
  color: #111827;
}

.section-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  align-items: flex-start;
  margin-bottom: 18px;
}

.section-subtitle {
  margin-top: 6px;
  color: #6b7280;
}

.legend {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #4b5563;
  font-size: 0.9rem;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
}

.legend-dot--good {
  background: #22c55e;
}

.legend-dot--medium {
  background: #f59e0b;
}

.legend-dot--avoid {
  background: #ef4444;
}

.timeline-chart {
  display: grid;
  gap: 12px;
}

.timeline-chart-row {
  display: grid;
  grid-template-columns: 170px 1fr 120px;
  gap: 14px;
  align-items: center;
  padding: 14px 16px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
}

.timeline-chart-row--current {
  border-color: #93c5fd;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.08);
}

.timeline-chart-row--best {
  border-color: #86efac;
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.08);
}

.timeline-chart-row--past {
  opacity: 0.72;
}

.timeline-chart-label {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.timeline-chart-hour {
  font-weight: 700;
  color: #111827;
  font-size: 1rem;
}

.timeline-chart-badges {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
}

.timeline-chart-bar-area {
  width: 100%;
}

.timeline-chart-bar-bg {
  width: 100%;
  height: 18px;
  background: #e5e7eb;
  border-radius: 999px;
  overflow: hidden;
}

.timeline-chart-bar-fill {
  height: 100%;
  border-radius: 999px;
}

.timeline-chart-values {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: flex-end;
  color: #4b5563;
  font-size: 0.92rem;
  font-weight: 500;
}

.timeline-main-value {
  font-size: 1rem;
  color: #111827;
  font-weight: 700;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 600;
  background: #e5e7eb;
  color: #374151;
}

.status-pill--good {
  background: #dcfce7;
  color: #166534;
}

.status-pill--medium {
  background: #fef3c7;
  color: #92400e;
}

.status-pill--avoid {
  background: #fee2e2;
  color: #991b1b;
}

.badge {
  display: inline-flex;
  align-items: center;
  padding: 5px 10px;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 700;
}

.badge--current {
  background: #dbeafe;
  color: #1d4ed8;
}

.badge--best {
  background: #dcfce7;
  color: #15803d;
}

.badge--past {
  background: #f3f4f6;
  color: #6b7280;
}

.bar-fill--good {
  background: linear-gradient(90deg, #4ade80, #22c55e);
}

.bar-fill--medium {
  background: linear-gradient(90deg, #fbbf24, #f59e0b);
}

.bar-fill--avoid {
  background: linear-gradient(90deg, #f87171, #ef4444);
}

.bar-fill--empty {
  background: #d1d5db;
}

.announcements-list {
  display: grid;
  gap: 12px;
}

.announcement-card {
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  padding: 16px;
  background: #ffffff;
}

.form {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field--full {
  grid-column: 1 / -1;
}

input,
select,
textarea,
button {
  padding: 12px;
  border-radius: 12px;
  border: 1px solid #d1d5db;
  font: inherit;
}

textarea {
  resize: vertical;
}

.actions {
  grid-column: 1 / -1;
}

button {
  background: #111827;
  color: white;
  cursor: pointer;
  border: none;
  font-weight: 600;
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.info-message {
  color: #4b5563;
}

.error {
  color: #dc2626;
  font-weight: 500;
}

@media (max-width: 768px) {
  .detail-box {
    padding: 22px;
  }

  .stats-grid,
  .form {
    grid-template-columns: 1fr;
  }

  .timeline-chart-row {
    grid-template-columns: 1fr;
    align-items: stretch;
  }

  .timeline-chart-values {
    align-items: flex-start;
  }
}
</style>