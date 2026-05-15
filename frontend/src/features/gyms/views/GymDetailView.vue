<template>
  <div class="detail-container">
    <div class="detail-box">
      <div class="top-bar">
        <button class="back-btn" @click="router.push('/home')">← Volver</button>
      </div>

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

          <button
            v-if="canFollow"
            class="follow-btn"
            :class="{ 'follow-btn--following': isFollowing }"
            :disabled="followLoading"
            @click="toggleFollow"
          >
            {{ isFollowing ? '✓ Siguiendo' : '+ Seguir' }}
          </button>
        </div>

        <div class="cover-wrapper">
          <img
            v-if="gymDetail.image_url"
            :src="gymDetail.image_url"
            :alt="gymDetail.name"
            class="cover-image"
          />
          <div v-else-if="canEdit" class="cover-placeholder">Sin imagen</div>
          <div v-if="canEdit" class="cover-change-btn" @click="coverInput.click()">
            {{ imageUploading ? 'Subiendo...' : 'Cambiar imagen' }}
          </div>
          <input
            ref="coverInput"
            type="file"
            accept="image/*"
            class="file-input-hidden"
            @change="onCoverChange"
          />
        </div>

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
                v-if="gymDetail.best_time_today.reason"
                class="recommendation-reason"
              >
                {{ gymDetail.best_time_today.reason }}
              </p>
            </template>

            <p v-else class="muted-text">Sin datos</p>
          </div>

          <div class="stat-card stat-card--tomorrow">
            <span class="stat-label">Mejor hora mañana</span>

            <strong class="stat-value">
              {{ gymDetail.best_time_tomorrow ? gymDetail.best_time_tomorrow.label : '—' }}
            </strong>

            <template v-if="gymDetail.best_time_tomorrow">
              <p class="stat-status">
                {{ gymDetail.best_time_tomorrow.occupancy_percent }}% ocupado ·
                {{ getStatusLabel(getStatusFromOccupancy(gymDetail.best_time_tomorrow.occupancy_percent)) }}
              </p>

              <div class="mini-progress">
                <div
                  class="mini-progress-bar"
                  :class="getOccupancyClass(gymDetail.best_time_tomorrow.occupancy_percent)"
                  :style="{ width: gymDetail.best_time_tomorrow.occupancy_percent + '%' }"
                />
              </div>

              <p v-if="gymDetail.best_time_tomorrow.confidence !== null" class="muted-text">
                Confianza: {{ gymDetail.best_time_tomorrow.confidence }}%
              </p>

              <p
                v-if="gymDetail.best_time_tomorrow.reason"
                class="recommendation-reason"
              >
                {{ gymDetail.best_time_tomorrow.reason }}
              </p>
            </template>

            <p v-else class="muted-text">Sin datos</p>
          </div>
        </div>

        <!-- Horario visible para todos -->
        <div v-if="gymDetail.schedule?.length" class="timeline-section">
          <h2>Horario</h2>

          <div class="schedule-view">
            <div
              v-for="row in scheduleRows"
              :key="row.day_type"
              class="schedule-view-row"
              :class="{
                'schedule-view-row--today': row.isToday,
                'schedule-view-row--closed': row.is_closed,
                'schedule-view-row--holiday': row.day_type === 'HOL',
              }"
            >
              <span class="schedule-view-day">{{ row.label }}</span>
              <span v-if="row.is_closed" class="schedule-view-hours schedule-view-hours--closed">Cerrado</span>
              <span v-else class="schedule-view-hours">{{ pad(row.opening_hour) }}:00 – {{ pad(row.closing_hour) }}:00</span>
              <span v-if="row.isToday" class="badge badge--current">Hoy</span>
            </div>
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
            <h2>Mi gimnasio</h2>

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

              <div class="field field--full">
                <label>Descripción</label>
                <textarea v-model="editForm.description" rows="4"></textarea>
              </div>

              <div class="field field--full">
                <label class="section-label">Horario</label>
                <p class="section-hint">Los cambios afectan a las recomendaciones de horario.</p>

                <div class="schedule-table">
                  <div class="schedule-header">
                    <span>Día</span>
                    <span>Cerrado</span>
                    <span>Abre</span>
                    <span>Cierra</span>
                  </div>

                  <div
                    v-for="row in editForm.schedule"
                    :key="row.day_type"
                    class="schedule-row"
                    :class="{ 'schedule-row--closed': row.is_closed }"
                  >
                    <span class="schedule-day">{{ row.label }}</span>

                    <label class="schedule-checkbox">
                      <input type="checkbox" v-model="row.is_closed" />
                    </label>

                    <select v-model="row.opening_hour" :disabled="row.is_closed">
                      <option v-for="h in hours" :key="h" :value="h">{{ pad(h) }}:00</option>
                    </select>

                    <select v-model="row.closing_hour" :disabled="row.is_closed">
                      <option v-for="h in closingHours" :key="h" :value="h">{{ pad(h) }}:00</option>
                    </select>
                  </div>
                </div>
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

        <div v-if="canDelete" class="danger-zone">
          <h2>Zona de peligro</h2>
          <p>Una vez eliminado el gimnasio no se puede recuperar.</p>
          <button class="btn-delete" :disabled="deleteLoading" @click="onDeleteGym">
            {{ deleteLoading ? 'Eliminando...' : 'Eliminar gimnasio' }}
          </button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'

// arrays de horas para los selectores del horario
const hours = Array.from({ length: 24 }, (_, i) => i)
const closingHours = Array.from({ length: 24 }, (_, i) => i + 1)

// formatea una hora como "07", "22", etc.
function pad(h) {
  return String(h).padStart(2, '0')
}

const SCHEDULE_LABELS = {
  MON: 'Lunes', TUE: 'Martes', WED: 'Miércoles', THU: 'Jueves',
  FRI: 'Viernes', SAT: 'Sábado', SUN: 'Domingo', HOL: 'Festivos',
}

const DAY_ORDER = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN', 'HOL']

// horario por defecto que usamos si el gym no tiene uno configurado
const DEFAULT_SCHEDULE = [
  { day_type: 'MON', opening_hour: 7,  closing_hour: 22, is_closed: false },
  { day_type: 'TUE', opening_hour: 7,  closing_hour: 22, is_closed: false },
  { day_type: 'WED', opening_hour: 7,  closing_hour: 22, is_closed: false },
  { day_type: 'THU', opening_hour: 7,  closing_hour: 22, is_closed: false },
  { day_type: 'FRI', opening_hour: 7,  closing_hour: 22, is_closed: false },
  { day_type: 'SAT', opening_hour: 9,  closing_hour: 20, is_closed: false },
  { day_type: 'SUN', opening_hour: 10, closing_hour: 16, is_closed: false },
  { day_type: 'HOL', opening_hour: 10, closing_hour: 14, is_closed: false },
]
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useGymsStore } from '../store/gymStore'
import { useUserStore } from '../../auth/store/userStore'
import { useToastStore } from '@/stores/toastStore'
import { toggleFollowGymService, deleteGymService, uploadGymImageService } from '../services/gymsService'

const route = useRoute()
const router = useRouter()
const gymsStore = useGymsStore()
const userStore = useUserStore()
const toastStore = useToastStore()

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

// formulario de edición del gym, se rellena cuando carga gymDetail
const editForm = reactive({
  name: '',
  province_id: '',
  municipality_id: '',
  postal_code: '',
  address: '',
  description: '',
  price_per_month: '',
  image_url: '',
  schedule: DEFAULT_SCHEDULE.map((r) => ({ ...r, label: SCHEDULE_LABELS[r.day_type] })),
})

// formulario para crear un anuncio nuevo
const announcementForm = reactive({
  kind: 'PROMOCION',
  title: '',
  content: '',
})

// hora actual del navegador para marcar la franja en el timeline
const currentHour = computed(() => new Date().getHours())

// hora recomendada para marcarla en el timeline
const bestHour = computed(() => {
  return gymDetail.value?.best_time_today?.hour ?? null
})

// filtramos las horas sin dato y añadimos flags de estado para el timeline
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

// pillamos el día de la semana actual para resaltar la fila correspondiente en el horario
const todayDayType = computed(() => {
  const map = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
  return map[new Date().getDay() === 0 ? 6 : new Date().getDay() - 1]
})

// prepara las filas del horario con la etiqueta del día y si es hoy
const scheduleRows = computed(() => {
  const schedule = gymDetail.value?.schedule ?? []
  return schedule.map((row) => ({
    ...row,
    label: SCHEDULE_LABELS[row.day_type],
    isToday: row.day_type === todayDayType.value,
  }))
})

// el usuario puede editar si es el dueño del gym o superuser
const canEdit = computed(() => {
  if (!userStore.user || !gymDetail.value) return false
  if (userStore.user.is_superuser && myGym.value?.slug === gymDetail.value.slug) return true
  return (
    userStore.user.rol === 'GIMNASIO' &&
    userStore.user.estado_gym === 'APROBADO' &&
    myGym.value?.slug === gymDetail.value.slug
  )
})

const followLoading = ref(false)
const isFollowing = computed(() => gymDetail.value?.is_following ?? false)
// los dueños del gym no pueden seguirlo, eso es para los demás usuarios
const canFollow = computed(() => {
  if (!userStore.user || !gymDetail.value) return false
  return !canEdit.value
})

const deleteLoading = ref(false)

const coverInput = ref(null)
const imageUploading = ref(false)

// sube la imagen de portada del gym cuando el dueño selecciona un archivo
async function onCoverChange(e) {
  const file = e.target.files[0]
  if (!file) return
  imageUploading.value = true
  const res = await uploadGymImageService(route.params.slug, file)
  imageUploading.value = false
  coverInput.value.value = ''
  if (res?.status === 200) {
    gymDetail.value.image_url = res.data.image_url
    toastStore.show('Imagen actualizada correctamente')
  } else {
    toastStore.show('Error al subir la imagen', 'error')
  }
}

// el superuser puede borrar cualquier gym, el dueño solo el suyo
const canDelete = computed(() => {
  if (!userStore.user || !gymDetail.value) return false
  if (userStore.user.is_superuser) return true
  return canEdit.value
})

// borra el gym con confirmación previa, y nos manda a home si todo va bien
async function onDeleteGym() {
  if (!confirm(`¿Seguro que quieres eliminar "${gymDetail.value.name}"? Esta acción no se puede deshacer.`)) return
  deleteLoading.value = true
  const response = await deleteGymService(route.params.slug)
  if (response?.status === 204) {
    router.push('/home')
  }
  deleteLoading.value = false
}

// toggle seguir/dejar de seguir, evitamos doble clic con followLoading
async function toggleFollow() {
  if (followLoading.value) return
  followLoading.value = true
  try {
    const response = await toggleFollowGymService(route.params.slug)
    if (response?.status === 200 || response?.status === 201) {
      gymDetail.value.is_following = !gymDetail.value.is_following
    }
  } finally {
    followLoading.value = false
  }
}

// convierte el estado de ocupación en texto para el usuario
function getStatusLabel(status) {
  if (status === 'GOOD') return 'Buen momento'
  if (status === 'MEDIUM') return 'Con espera'
  if (status === 'AVOID') return 'Mejor evitar'
  return 'Sin datos'
}

// calcula el estado a partir del porcentaje, igual que en el backend
function getStatusFromOccupancy(occupancyPercent) {
  if (occupancyPercent === null || occupancyPercent === undefined) return null
  if (occupancyPercent < 40) return 'GOOD'
  if (occupancyPercent < 70) return 'MEDIUM'
  return 'AVOID'
}

// clase CSS para el pill de estado según si es bueno, medio o malo
function getStatusClass(status) {
  if (status === 'GOOD') return 'status-pill--good'
  if (status === 'MEDIUM') return 'status-pill--medium'
  if (status === 'AVOID') return 'status-pill--avoid'
  return ''
}

// clase CSS para la barra de progreso de ocupación
function getOccupancyClass(occupancyPercent) {
  if (occupancyPercent === null || occupancyPercent === undefined) return 'bar-fill--empty'
  if (occupancyPercent < 40) return 'bar-fill--good'
  if (occupancyPercent < 70) return 'bar-fill--medium'
  return 'bar-fill--avoid'
}


// rellena el formulario de edición con los datos actuales del gym
function fillEditForm() {
  if (!gymDetail.value) return

  editForm.name = gymDetail.value.name || ''
  editForm.province_id = gymDetail.value.province_id || ''
  editForm.municipality_id = gymDetail.value.municipality_id || ''
  editForm.postal_code = gymDetail.value.postal_code || ''
  editForm.address = gymDetail.value.address || ''
  editForm.description = gymDetail.value.description || ''
  editForm.price_per_month = gymDetail.value.price_per_month || ''

  // montamos el horario combinando los datos de la API con el horario por defecto
  const apiSchedule = gymDetail.value.schedule ?? []
  const byDayType = Object.fromEntries(apiSchedule.map((s) => [s.day_type, s]))
  editForm.schedule = DAY_ORDER.map((d) => ({
    day_type: d,
    label: SCHEDULE_LABELS[d],
    opening_hour: byDayType[d]?.opening_hour ?? DEFAULT_SCHEDULE.find((r) => r.day_type === d)?.opening_hour ?? 7,
    closing_hour: byDayType[d]?.closing_hour ?? DEFAULT_SCHEDULE.find((r) => r.day_type === d)?.closing_hour ?? 22,
    is_closed: byDayType[d]?.is_closed ?? false,
  }))
}

// al cambiar provincia en el formulario de edición limpiamos y recargamos municipios
async function onProvinceChange() {
  editForm.municipality_id = ''
  gymsStore.resetMunicipalities()

  if (editForm.province_id) {
    await gymsStore.fetchMunicipalities(editForm.province_id)
  }
}

// guarda los cambios del gym y vuelve a la home si todo va bien
async function onSaveGym() {
  const result = await gymsStore.updateGym(route.params.slug, {
    name: editForm.name,
    province_id: editForm.province_id,
    municipality_id: editForm.municipality_id,
    postal_code: editForm.postal_code,
    address: editForm.address,
    description: editForm.description,
    price_per_month: editForm.price_per_month,
    // solo mandamos los campos que necesita el backend, sin las etiquetas
    schedule: editForm.schedule.map(({ day_type, opening_hour, closing_hour, is_closed }) => ({
      day_type,
      opening_hour,
      closing_hour,
      is_closed,
    })),
  })

  if (result.isOk) {
    toastStore.show('Cambios guardados correctamente')
    router.push('/home')
  } else {
    toastStore.show('Error al guardar los cambios', 'error')
  }
}

// publica el anuncio y limpia el formulario si todo va bien
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
    toastStore.show('Publicación creada correctamente')
  } else {
    toastStore.show('Error al crear la publicación', 'error')
  }
}

// cuando carga el detalle del gym rellenamos el form y cargamos municipios si puede editar
watch(gymDetail, async (value) => {
  if (!value) return

  fillEditForm()

  if (canEdit.value && value.province_id) {
    await gymsStore.fetchMunicipalities(value.province_id)
  }
})

onMounted(async () => {
  // cargamos el detalle del gym que viene en la URL
  await gymsStore.fetchGymDetail(route.params.slug)
  await gymsStore.fetchProvinces()

  // solo cargamos myGym si el usuario puede gestionar gyms
  if (
    userStore.user?.is_superuser ||
    (userStore.user?.rol === 'GIMNASIO' && userStore.user?.estado_gym === 'APROBADO')
  ) {
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

.follow-btn {
  margin-left: auto;
  padding: 6px 14px;
  border: 1.5px solid #6b7280;
  border-radius: 999px;
  background: transparent;
  color: #374151;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.15s;
}

.follow-btn:hover {
  border-color: #111827;
  color: #111827;
}

.follow-btn--following {
  background: #111827;
  border-color: #111827;
  color: white;
}

.follow-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

.cover-wrapper {
  position: relative;
  width: 100%;
  margin-bottom: 20px;
}

.cover-image {
  width: 100%;
  aspect-ratio: 16 / 6;
  object-fit: cover;
  object-position: center;
  border-radius: 16px;
  display: block;
}

.cover-placeholder {
  width: 100%;
  aspect-ratio: 16 / 6;
  border-radius: 16px;
  background: #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  font-size: 0.95rem;
}

.cover-change-btn {
  position: absolute;
  bottom: 12px;
  right: 12px;
  background: rgba(0, 0, 0, 0.65);
  color: white;
  padding: 7px 16px;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  backdrop-filter: blur(4px);
  transition: background 0.15s;
}

.cover-change-btn:hover {
  background: rgba(0, 0, 0, 0.85);
}

.description {
  color: #4b5563;
  margin-bottom: 24px;
  line-height: 1.6;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
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

.stat-card--tomorrow {
  border: 1px solid #d1fae5;
  background: linear-gradient(180deg, #f0fdf4 0%, #ecfdf5 100%);
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
  margin: 0;
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

.schedule-view {
  display: flex;
  flex-direction: column;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
}

.schedule-view-row {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 18px;
  border-top: 1px solid #e5e7eb;
  transition: background 0.15s;
}

.schedule-view-row:first-child {
  border-top: none;
}

.schedule-view-row--today {
  background: #f0fdf4;
}

.schedule-view-row--closed {
  background: #f9fafb;
}

.schedule-view-row--holiday {
  border-top: 2px solid #e5e7eb;
  background: #fefce8;
}

.schedule-view-day {
  width: 100px;
  font-weight: 600;
  color: #111827;
  flex-shrink: 0;
}

.schedule-view-hours {
  color: #374151;
  flex: 1;
}

.schedule-view-hours--closed {
  color: #9ca3af;
  font-style: italic;
}

.section-label {
  font-weight: 600;
  color: #111827;
  font-size: 1rem;
}

.section-hint {
  color: #6b7280;
  font-size: 0.9rem;
  margin: 0;
}

.schedule-table {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  overflow: hidden;
}

.schedule-header {
  display: grid;
  grid-template-columns: 110px 80px 1fr 1fr;
  gap: 12px;
  padding: 10px 16px;
  background: #f3f4f6;
  font-weight: 600;
  font-size: 0.85rem;
  color: #374151;
}

.schedule-row {
  display: grid;
  grid-template-columns: 110px 80px 1fr 1fr;
  gap: 12px;
  padding: 10px 16px;
  align-items: center;
  border-top: 1px solid #e5e7eb;
  transition: background 0.15s;
}

.schedule-row--closed {
  background: #f9fafb;
  opacity: 0.7;
}

.schedule-day {
  font-weight: 500;
  color: #111827;
}

.schedule-checkbox {
  display: flex;
  justify-content: center;
}

.schedule-checkbox input {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

select:disabled {
  background: #f3f4f6;
  color: #9ca3af;
  cursor: not-allowed;
}


.danger-zone {
  margin-top: 36px;
  border: 1px solid #fecaca;
  border-radius: 12px;
  padding: 20px 24px;
  background: #fff5f5;
}

.danger-zone h2 {
  margin: 0 0 6px;
  color: #991b1b;
  font-size: 1rem;
}

.danger-zone p {
  color: #6b7280;
  font-size: 0.9rem;
  margin: 0 0 14px;
}

.btn-delete {
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  font-weight: 600;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-delete:hover {
  background: #dc2626;
}

.btn-delete:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .detail-box {
    padding: 22px;
  }

  .stats-grid,
  .form {
    grid-template-columns: 1fr;
  }

  .stat-card--tomorrow,
  .stat-card--highlight {
    border-top: none;
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