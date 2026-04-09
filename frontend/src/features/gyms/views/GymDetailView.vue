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
            <strong>
              {{ gymDetail.current_occupancy !== null ? gymDetail.current_occupancy + '%' : '—' }}
            </strong>
            <p>{{ getStatusLabel(gymDetail.current_status) }}</p>
          </div>

          <div class="stat-card">
            <span class="stat-label">Mejor hora hoy</span>
            <strong>{{ gymDetail.best_time_today ? gymDetail.best_time_today.label : '—' }}</strong>
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
              <span>{{ item.occupancy_percent !== null ? item.occupancy_percent + '%' : '—' }}</span>
              <span>{{ getStatusLabel(item.status) }}</span>
            </div>
          </div>
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
import { useGymsStore } from '@/stores/gymStore'
import { useUserStore } from '@/stores/userStore'

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

.cover-image {
  width: 100%;
  max-height: 360px;
  object-fit: cover;
  border-radius: 12px;
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

.timeline-section,
.manage-section {
  margin-top: 32px;
}

.timeline-section h2,
.manage-section h2 {
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

.announcements-list {
  display: grid;
  gap: 12px;
}

.announcement-card {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 16px;
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
  border-radius: 10px;
  border: 1px solid #d1d5db;
}

.actions {
  grid-column: 1 / -1;
}

button {
  background: #111827;
  color: white;
  cursor: pointer;
}

.info-message {
  color: #4b5563;
}

.error {
  color: red;
}

@media (max-width: 768px) {
  .stats-grid,
  .form {
    grid-template-columns: 1fr;
  }

  .timeline-row {
    grid-template-columns: 1fr;
  }
}
</style>