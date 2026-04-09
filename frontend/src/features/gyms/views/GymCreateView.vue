<template>
  <div class="page-container">
    <div class="page-box">
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

        <div class="field">
          <label>Imagen (URL)</label>
          <input v-model="form.image_url" type="url" />
        </div>

        <div class="field field--full">
          <label>Descripción</label>
          <textarea v-model="form.description" rows="4"></textarea>
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
import { onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useGymsStore } from '../store/gymStore'

const router = useRouter()
const gymsStore = useGymsStore()

const { provinces, municipalities, saveLoading, saveError } = storeToRefs(gymsStore)

const form = reactive({
  name: '',
  province_id: '',
  municipality_id: '',
  postal_code: '',
  address: '',
  description: '',
  price_per_month: '',
  image_url: '',
})

async function onProvinceChange() {
  form.municipality_id = ''
  gymsStore.resetMunicipalities()

  if (form.province_id) {
    await gymsStore.fetchMunicipalities(form.province_id)
  }
}

async function onSubmit() {
  const result = await gymsStore.createGym({
    name: form.name,
    province_id: form.province_id,
    municipality_id: form.municipality_id,
    postal_code: form.postal_code,
    address: form.address,
    description: form.description,
    price_per_month: form.price_per_month,
    image_url: form.image_url,
  })

  if (result.isOk) {
    router.push(`/gyms/${result.data.slug}`)
  }
}

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

.error {
  color: red;
  margin-bottom: 16px;
}

@media (max-width: 768px) {
  .form {
    grid-template-columns: 1fr;
  }
}
</style>