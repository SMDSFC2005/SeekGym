<template>
  <div class="page-container">
    <div class="page-box">
      <div class="top-bar">
        <button class="back-btn" @click="router.push('/home')">← Volver</button>
      </div>

      <h1 class="title">Crear gimnasio</h1>

      <p v-if="saveError" class="error">{{ saveError }}</p>

      <form class="form" @submit.prevent="onSubmit">
        <div class="field">
          <label>Nombre</label>
          <input v-model="form.name" type="text" required />
        </div>

        <div class="field">
          <label>Provincia</label>
          <select v-model="form.province_id" required @change="onProvinceChange">
            <option value="">Selecciona</option>
            <option v-for="province in provinces" :key="province.id" :value="province.id">
              {{ province.name }}
            </option>
          </select>
        </div>

        <div class="field">
          <label>Municipio</label>
          <select v-model="form.municipality_id" required :disabled="!form.province_id">
            <option value="">Selecciona</option>
            <option v-for="municipality in municipalities" :key="municipality.id" :value="municipality.id">
              {{ municipality.name }}
            </option>
          </select>
        </div>

        <div class="field">
          <label>Código postal</label>
          <input v-model="form.postal_code" type="text" required />
        </div>

        <div class="field">
          <label>Dirección</label>
          <input v-model="form.address" type="text" required />
        </div>

        <div class="field">
          <label>Precio mensual</label>
          <input v-model="form.price_per_month" type="number" step="0.01" min="0" required />
        </div>

        <!-- Imagen -->
        <div class="field field--full">
          <label>Imagen del gimnasio</label>
          <div class="image-upload-area" @click="fileInput.click()">
            <img v-if="imagePreview" :src="imagePreview" class="image-preview" alt="Preview" />
            <div v-else class="image-placeholder">
              <span class="image-placeholder-icon">🖼</span>
              <span>Haz clic para seleccionar una imagen</span>
            </div>
          </div>
          <input
            ref="fileInput"
            type="file"
            accept="image/*"
            class="file-input-hidden"
            @change="onImageSelect"
          />
          <p v-if="imageFile" class="image-filename">{{ imageFile.name }}</p>
        </div>

        <div class="field field--full">
          <label>Descripción</label>
          <textarea v-model="form.description" rows="4"></textarea>
        </div>

        <!-- Horario -->
        <div class="field field--full">
          <label class="section-label">Horario</label>
          <p class="section-hint">Indica los horarios de apertura de tu gimnasio. Los festivos tienen su propia franja.</p>

          <div class="schedule-table">
            <div class="schedule-header">
              <span>Día</span>
              <span>Cerrado</span>
              <span>Abre</span>
              <span>Cierra</span>
            </div>

            <div
              v-for="row in form.schedule"
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
            {{ saveLoading ? 'Guardando...' : 'Crear gimnasio' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useGymsStore } from '../store/gymStore'
import { uploadGymImageService } from '../services/gymsService'

const router = useRouter()
const gymsStore = useGymsStore()

const { provinces, municipalities, saveLoading, saveError } = storeToRefs(gymsStore)

// listas de horas para los selectores de apertura y cierre
const hours = Array.from({ length: 24 }, (_, i) => i)
const closingHours = Array.from({ length: 24 }, (_, i) => i + 1)

// formatea horas con cero delante: 7 → "07"
function pad(h) {
  return String(h).padStart(2, '0')
}

// horario predefinido razonable para un gym español
const DEFAULT_SCHEDULE = [
  { day_type: 'MON', label: 'Lunes',     opening_hour: 7,  closing_hour: 22, is_closed: false },
  { day_type: 'TUE', label: 'Martes',    opening_hour: 7,  closing_hour: 22, is_closed: false },
  { day_type: 'WED', label: 'Miércoles', opening_hour: 7,  closing_hour: 22, is_closed: false },
  { day_type: 'THU', label: 'Jueves',    opening_hour: 7,  closing_hour: 22, is_closed: false },
  { day_type: 'FRI', label: 'Viernes',   opening_hour: 7,  closing_hour: 22, is_closed: false },
  { day_type: 'SAT', label: 'Sábado',    opening_hour: 9,  closing_hour: 20, is_closed: false },
  { day_type: 'SUN', label: 'Domingo',   opening_hour: 10, closing_hour: 16, is_closed: false },
  { day_type: 'HOL', label: 'Festivos',  opening_hour: 10, closing_hour: 14, is_closed: false },
]

// datos del formulario de creación del gym
const form = reactive({
  name: '',
  province_id: '',
  municipality_id: '',
  postal_code: '',
  address: '',
  description: '',
  price_per_month: '',
  schedule: DEFAULT_SCHEDULE.map((r) => ({ ...r })),
})

const fileInput = ref(null)
const imageFile = ref(null)
const imagePreview = ref(null)

// cuando el usuario selecciona una imagen generamos una preview local
function onImageSelect(e) {
  const file = e.target.files[0]
  if (!file) return
  imageFile.value = file
  imagePreview.value = URL.createObjectURL(file)
}

// al cambiar de provincia reseteamos el municipio y cargamos los nuevos
async function onProvinceChange() {
  form.municipality_id = ''
  gymsStore.resetMunicipalities()
  if (form.province_id) {
    await gymsStore.fetchMunicipalities(form.province_id)
  }
}

// envía el formulario, crea el gym y sube la imagen si hay una seleccionada
async function onSubmit() {
  const result = await gymsStore.createGym({
    name: form.name,
    province_id: form.province_id,
    municipality_id: form.municipality_id,
    postal_code: form.postal_code,
    address: form.address,
    description: form.description,
    price_per_month: form.price_per_month,
    // quitamos las etiquetas, el backend solo necesita estos campos
    schedule: form.schedule.map(({ day_type, opening_hour, closing_hour, is_closed }) => ({
      day_type,
      opening_hour,
      closing_hour,
      is_closed,
    })),
  })

  if (result.isOk) {
    // si hay imagen la subimos justo después de crear el gym
    if (imageFile.value) {
      await uploadGymImageService(result.data.slug, imageFile.value)
    }
    router.push(`/gyms/${result.data.slug}`)
  }
}

// cargamos las provincias al montar para tener el selector listo
onMounted(async () => {
  await gymsStore.fetchProvinces()
})
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #f9fafb;
  padding: 40px 20px;
}

.page-box {
  max-width: 900px;
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
  margin-bottom: 20px;
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

.image-upload-area {
  width: 100%;
  height: 200px;
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 0.15s;
}

.image-upload-area:hover {
  border-color: #9ca3af;
}

.image-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #9ca3af;
  font-size: 0.9rem;
}

.image-placeholder-icon {
  font-size: 2rem;
}

.file-input-hidden {
  display: none;
}

.image-filename {
  color: #6b7280;
  font-size: 0.85rem;
  margin: 0;
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

input,
select,
textarea,
button {
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid #d1d5db;
  font: inherit;
}

select:disabled {
  background: #f3f4f6;
  color: #9ca3af;
  cursor: not-allowed;
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
  width: 100%;
  padding: 14px;
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.error {
  color: red;
  margin-bottom: 16px;
}

@media (max-width: 768px) {
  .form {
    grid-template-columns: 1fr;
  }

  .schedule-header,
  .schedule-row {
    grid-template-columns: 1fr 60px 1fr 1fr;
  }
}
</style>
