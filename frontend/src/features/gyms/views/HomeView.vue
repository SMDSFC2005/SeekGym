<template>
  <div class="home-container">
    <div class="home-box">
      <div class="top-bar">
        <div class="top-bar__actions">
          <button
            v-if="userStore.user"
            class="action-button action-button--secondary"
            @click="router.push('/perfil')"
          >
            Mi perfil
          </button>

          <button
            v-if="userStore.user"
            class="action-button action-button--secondary"
            @click="router.push('/gyms/seguidos')"
          >
            Mis seguidos
          </button>

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

          <!-- Notification bell -->
          <div class="notif-wrapper" v-if="userStore.user">
            <button class="notif-btn" @click="toggleNotifPanel">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
                <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
              </svg>
              <span v-if="notificationsStore.total > 0" class="notif-badge">
                {{ notificationsStore.total > 9 ? '9+' : notificationsStore.total }}
              </span>
            </button>

            <div v-if="showNotifPanel" class="notif-overlay" @click="showNotifPanel = false" />

            <div v-if="showNotifPanel" class="notif-panel">
              <template v-if="userStore.user.is_superuser">
                <p v-if="notificationsStore.pendingRequests > 0" class="notif-count">
                  {{ notificationsStore.pendingRequests }} solicitud(es) pendiente(s)
                </p>
                <p v-else class="notif-empty">No hay solicitudes pendientes</p>
                <button
                  class="notif-action-btn"
                  @click="router.push('/admin/solicitudes'); showNotifPanel = false"
                >
                  Ver solicitudes
                </button>
              </template>

              <template v-else>
                <div v-if="!notificationsStore.unreadAnnouncements.length" class="notif-empty">
                  Sin notificaciones nuevas
                </div>
                <template v-else>
                  <div
                    v-for="ann in notificationsStore.unreadAnnouncements"
                    :key="ann.gym_slug + ann.title + ann.created_at"
                    class="notif-item"
                    @click="router.push(`/gyms/${ann.gym_slug}`); showNotifPanel = false"
                  >
                    <strong class="notif-item-gym">{{ ann.gym_name }}</strong>
                    <span class="notif-item-title">{{ ann.title }}</span>
                  </div>
                  <button class="notif-action-btn" @click="notificationsStore.markRead(); showNotifPanel = false">
                    Marcar como leído
                  </button>
                </template>
              </template>
            </div>
          </div>

          <button class="logout-button" @click="onLogout">
            Cerrar sesión
          </button>
        </div>
      </div>

      <h2 class="title">¿Cuándo entrenar sin esperar máquinas?</h2>
      <p class="subtitle">
        Consulta el estado actual de tu gym y descubre cuál es la mejor hora de hoy para entrenar.
      </p>

      <div class="search-bar">
        <input
          v-model="searchInput"
          type="text"
          placeholder="Buscar gimnasio por nombre..."
          class="search-input"
        />
      </div>

      <GymFilters
        :province-id="filters.province_id"
        :municipality-id="filters.municipality_id"
        :provinces="provinces"
        :municipalities="municipalities"
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
import { computed, reactive, onMounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { useGymsStore } from '../store/gymStore'
import { useUserStore } from '../../auth/store/userStore'
import { useNotificationsStore } from '@/stores/notificationsStore'
import GymFilters from '../components/GymFilters.vue'
import GymCard from '../components/GymCard.vue'

const router = useRouter()
const userStore = useUserStore()
const gymsStore = useGymsStore()
const notificationsStore = useNotificationsStore()

// controla si se ve el panel de notificaciones
const showNotifPanel = ref(false)

const {
  gyms,
  loading,
  error,
  currentFilters,
  provinces,
  municipalities,
  myGym,
} = storeToRefs(gymsStore)

// filtros activos de provincia y municipio
const filters = reactive({
  province_id: '',
  municipality_id: '',
})

const searchInput = ref('')
let searchDebounce = null

// buscamos al escribir con un debounce de 300ms para no spamear la API
watch(searchInput, (value) => {
  clearTimeout(searchDebounce)
  searchDebounce = setTimeout(() => {
    gymsStore.fetchHomeGyms({
      province_id: filters.province_id,
      municipality_id: filters.municipality_id,
      search: value.trim(),
    })
  }, 300)
})

// solo pueden crear gym los usuarios con rol GIMNASIO aprobado o el superuser
const canCreateGym = computed(() => {
  if (!userStore.user) return false
  if (userStore.user.is_superuser) return true
  return userStore.user.rol === 'GIMNASIO' && userStore.user.estado_gym === 'APROBADO'
})

// abre o cierra el panel de notificaciones
function toggleNotifPanel() {
  showNotifPanel.value = !showNotifPanel.value
}

function onLogout() {
  userStore.logout()
  router.push('/login')
}

function goToCreateGym() {
  router.push('/gyms/create')
}

// navega al detalle del gym del usuario si tiene uno
function goToMyGym() {
  if (myGym.value?.slug) {
    router.push(`/gyms/${myGym.value.slug}`)
  }
}

// al cambiar de provincia limpiamos el municipio y cargamos los nuevos
async function onProvinceChange(payload) {
  filters.province_id = payload.province_id
  filters.municipality_id = ''

  gymsStore.resetMunicipalities()

  if (filters.province_id) {
    await gymsStore.fetchMunicipalities(filters.province_id)
  }
}

async function onMunicipalityChange(payload) {
  filters.province_id = payload.province_id
  filters.municipality_id = payload.municipality_id
}

// aplica los filtros seleccionados y recarga los gyms
async function onApplyFilters(newFilters) {
  filters.province_id = newFilters.province_id
  filters.municipality_id = newFilters.municipality_id

  await gymsStore.fetchHomeGyms({
    province_id: filters.province_id,
    municipality_id: filters.municipality_id,
  })
}

onMounted(async () => {
  // restauramos los filtros que tenía el store al volver a la home
  filters.province_id = currentFilters.value.province_id || ''
  filters.municipality_id = currentFilters.value.municipality_id || ''

  await gymsStore.fetchProvinces()

  if (filters.province_id) {
    await gymsStore.fetchMunicipalities(filters.province_id)
  }

  // solo cargamos myGym si el usuario puede gestionar gyms
  if (canCreateGym.value) {
    await gymsStore.fetchMyGym()
  }

  await gymsStore.fetchHomeGyms({
    province_id: filters.province_id,
    municipality_id: filters.municipality_id,
  })

  // cargamos las notificaciones al entrar en la home
  await notificationsStore.fetch()
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
  margin-bottom: 20px;
}

.search-bar {
  margin-bottom: 16px;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 12px;
  font-size: 1rem;
  box-sizing: border-box;
  outline: none;
}

.search-input:focus {
  border-color: #9ca3af;
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
  align-items: center;
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

.action-button--secondary {
  background: #6b7280;
}

/* Notification bell */
.notif-wrapper {
  position: relative;
}

.notif-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 8px 10px;
  cursor: pointer;
  color: #374151;
}

.notif-btn:hover {
  background: #e5e7eb;
}

.notif-badge {
  position: absolute;
  top: -6px;
  right: -6px;
  background: #ef4444;
  color: white;
  font-size: 0.7rem;
  font-weight: 700;
  min-width: 18px;
  height: 18px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
}

.notif-overlay {
  position: fixed;
  inset: 0;
  z-index: 99;
}

.notif-panel {
  position: absolute;
  right: 0;
  top: calc(100% + 8px);
  width: 280px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12);
  z-index: 100;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.notif-count {
  color: #111827;
  font-weight: 600;
  font-size: 0.95rem;
  margin: 0;
}

.notif-empty {
  color: #6b7280;
  font-size: 0.9rem;
  margin: 0;
}

.notif-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
}

.notif-item:hover {
  background: #f9fafb;
}

.notif-item-gym {
  font-size: 0.85rem;
  color: #111827;
}

.notif-item-title {
  font-size: 0.82rem;
  color: #6b7280;
}

.notif-action-btn {
  background: #111827;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  text-align: center;
}

.notif-action-btn:hover {
  background: #1f2937;
}
</style>
