<template>
  <div class="home-container">
    <div class="home-box">
      <div class="top-bar">
        <div class="top-bar__actions">
          <button
            v-if="canCreateGym"
            class="action-button"
            @click="goToCreateGym"
          >
            Crear mi gimnasio
          </button>

          <button
            v-if="canCreateGym && myGym"
            class="action-button"
            @click="goToMyGym"
          >
            Gestionar mi gimnasio
          </button>

          <button class="logout-button" @click="onLogout">
            Cerrar sesión
          </button>
        </div>
      </div>

      <h2 class="title">¿Cuándo entrenar sin esperar máquinas?</h2>
      <p class="subtitle">
        Consulta el estado actual de tu gym y descubre cuál es la mejor hora de hoy para entrenar.
      </p>

      <GymFilters
        :province-id="filters.province_id"
        :municipality-id="filters.municipality_id"
        :postal-code="filters.postal_code"
        :provinces="provinces"
        :municipalities="municipalities"
        :postal-codes="postalCodes"
        @province-change="onProvinceChange"
        @municipality-change="onMunicipalityChange"
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
import { computed, reactive, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { useGymsStore } from '../store/gymStore'
import { useUserStore } from '../../auth/store/userStore'
import GymFilters from '../components/GymFilters.vue'
import GymCard from '../components/GymCard.vue'

const router = useRouter()
const userStore = useUserStore()
const gymsStore = useGymsStore()

const {
  gyms,
  loading,
  error,
  currentFilters,
  provinces,
  municipalities,
  postalCodes,
  myGym,
} = storeToRefs(gymsStore)

const filters = reactive({
  province_id: '',
  municipality_id: '',
  postal_code: '',
})

const canCreateGym = computed(() => {
  return (
    userStore.user &&
    userStore.user.rol === 'GIMNASIO' &&
    userStore.user.estado_gym === 'APROBADO'
  )
})

function onLogout() {
  userStore.logout()
  router.push('/login')
}

function goToCreateGym() {
  router.push('/gyms/create')
}

function goToMyGym() {
  if (myGym.value?.slug) {
    router.push(`/gyms/${myGym.value.slug}`)
  }
}

async function onProvinceChange(payload) {
  filters.province_id = payload.province_id
  filters.municipality_id = ''
  filters.postal_code = ''

  gymsStore.resetMunicipalities()
  gymsStore.resetPostalCodes()

  if (filters.province_id) {
    await gymsStore.fetchMunicipalities(filters.province_id)
  }
}

async function onMunicipalityChange(payload) {
  filters.province_id = payload.province_id
  filters.municipality_id = payload.municipality_id
  filters.postal_code = ''

  gymsStore.resetPostalCodes()

  if (filters.province_id) {
    await gymsStore.fetchPostalCodes({
      province_id: filters.province_id,
      municipality_id: filters.municipality_id,
    })
  }
}

async function onApplyFilters(newFilters) {
  filters.province_id = newFilters.province_id
  filters.municipality_id = newFilters.municipality_id
  filters.postal_code = newFilters.postal_code

  await gymsStore.fetchHomeGyms({
    province_id: filters.province_id,
    municipality_id: filters.municipality_id,
    postal_code: filters.postal_code,
  })
}

onMounted(async () => {
  filters.province_id = currentFilters.value.province_id || ''
  filters.municipality_id = currentFilters.value.municipality_id || ''
  filters.postal_code = currentFilters.value.postal_code || ''

  await gymsStore.fetchProvinces()

  if (filters.province_id) {
    await gymsStore.fetchMunicipalities(filters.province_id)
  }

  if (filters.province_id) {
    await gymsStore.fetchPostalCodes({
      province_id: filters.province_id,
      municipality_id: filters.municipality_id,
    })
  }

  if (canCreateGym.value) {
    await gymsStore.fetchMyGym()
  }

  await gymsStore.fetchHomeGyms({
    province_id: filters.province_id,
    municipality_id: filters.municipality_id,
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

.top-bar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 16px;
}

.top-bar__actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.logout-button,
.action-button {
  padding: 8px 14px;
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  font-size: 0.9rem;
}

.logout-button {
  background: #111827;
}

.action-button {
  background: #f97316;
}
</style>