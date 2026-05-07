<template>
  <div class="page-container">
    <div class="page-box">
      <div class="top-bar">
        <button class="back-btn" @click="router.push('/home')">← Volver</button>
      </div>

      <h1 class="title">Solicitudes de cuenta de gimnasio</h1>

      <p v-if="loading" class="info">Cargando solicitudes...</p>
      <p v-else-if="!requests.length" class="info">No hay solicitudes pendientes.</p>

      <div v-else class="requests-list">
        <div v-for="req in requests" :key="req.id" class="request-card">
          <div class="request-info">
            <strong>{{ req.username }}</strong>
            <span class="request-email">{{ req.email || 'Sin email' }}</span>
            <span class="request-date">Solicitud: {{ formatDate(req.creado_en) }}</span>
          </div>

          <div class="request-actions">
            <button class="btn-approve" :disabled="loadingId === req.id" @click="approve(req.id)">
              Aprobar
            </button>
            <button class="btn-reject" :disabled="loadingId === req.id" @click="reject(req.id)">
              Rechazar
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getGymRequestsService, approveGymRequestService, rejectGymRequestService } from '../services/adminService'
import { useNotificationsStore } from '@/stores/notificationsStore'

const router = useRouter()
const notificationsStore = useNotificationsStore()

const requests = ref([])
const loading = ref(true)
const loadingId = ref(null)

async function load() {
  loading.value = true
  const response = await getGymRequestsService()
  if (response?.status === 200) {
    requests.value = response.data
  }
  loading.value = false
}

async function approve(id) {
  loadingId.value = id
  const response = await approveGymRequestService(id)
  if (response?.status === 200) {
    requests.value = requests.value.filter((r) => r.id !== id)
    notificationsStore.pendingRequests = Math.max(0, notificationsStore.pendingRequests - 1)
  }
  loadingId.value = null
}

async function reject(id) {
  loadingId.value = id
  const response = await rejectGymRequestService(id)
  if (response?.status === 200) {
    requests.value = requests.value.filter((r) => r.id !== id)
    notificationsStore.pendingRequests = Math.max(0, notificationsStore.pendingRequests - 1)
  }
  loadingId.value = null
}

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric' })
}

onMounted(load)
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #f9fafb;
  padding: 40px 20px;
}

.page-box {
  max-width: 800px;
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
  margin-bottom: 24px;
}

.info {
  color: #6b7280;
}

.requests-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.request-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 16px 20px;
  flex-wrap: wrap;
}

.request-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.request-email {
  color: #6b7280;
  font-size: 0.9rem;
}

.request-date {
  color: #9ca3af;
  font-size: 0.85rem;
}

.request-actions {
  display: flex;
  gap: 10px;
}

.btn-approve,
.btn-reject {
  padding: 8px 18px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-approve {
  background: #22c55e;
  color: white;
}

.btn-reject {
  background: #ef4444;
  color: white;
}

.btn-approve:disabled,
.btn-reject:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
