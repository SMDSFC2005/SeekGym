<template>
  <div class="profile-container">
    <div class="profile-box">
      <button class="back-btn" @click="router.push('/home')">← Volver</button>

      <div class="profile-header">
        <div class="avatar">{{ avatarLetter }}</div>
        <div class="profile-title">
          <h2>{{ user.username }}</h2>
          <span v-if="roleLabel" :class="['role-badge', roleBadgeClass]">
            {{ roleLabel }}
          </span>
        </div>
      </div>

      <div class="profile-fields">
        <div class="field">
          <span class="field-label">Usuario</span>
          <span class="field-value">{{ user.username }}</span>
        </div>

        <div class="field" v-if="user.email">
          <span class="field-label">Email</span>
          <span class="field-value">{{ user.email }}</span>
        </div>

        <div class="field" v-if="user.rol === 'GIMNASIO' && !user.is_superuser">
          <span class="field-label">Estado de solicitud</span>
          <span :class="['estado-badge', estadoBadgeClass]">{{ estadoLabel }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/userStore'

const router = useRouter()
const userStore = useUserStore()
const user = userStore.user

const avatarLetter = computed(() => user?.username?.[0]?.toUpperCase() ?? '?')

const roleLabel = computed(() => {
  if (user?.is_superuser) return 'Admin'
  if (user?.rol === 'GIMNASIO') return 'Gym'
  return null
})

const roleBadgeClass = computed(() => {
  if (user?.is_superuser) return 'role-badge--admin'
  if (user?.rol === 'GIMNASIO') return 'role-badge--gym'
  return ''
})

const estadoLabel = computed(() => {
  const map = {
    PENDIENTE: 'Pendiente de aprobación',
    APROBADO: 'Aprobado',
    RECHAZADO: 'Rechazado',
    NONE: '-',
  }
  return map[user?.estado_gym] ?? '-'
})

const estadoBadgeClass = computed(() => {
  const map = {
    PENDIENTE: 'estado--pendiente',
    APROBADO: 'estado--aprobado',
    RECHAZADO: 'estado--rechazado',
  }
  return map[user?.estado_gym] ?? ''
})
</script>

<style scoped>
.profile-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  background: #f9fafb;
  padding: 40px 20px;
}

.profile-box {
  width: 100%;
  max-width: 520px;
  background: white;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
}

.back-btn {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  font-size: 0.9rem;
  padding: 0;
  margin-bottom: 24px;
  display: inline-block;
}

.back-btn:hover {
  color: #111827;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 32px;
}

.avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: #111827;
  color: white;
  font-size: 1.8rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.profile-title {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.profile-title h2 {
  margin: 0;
  font-size: 1.4rem;
  color: #111827;
}

.role-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 700;
  width: fit-content;
}

.role-badge--admin {
  background: #fef3c7;
  color: #92400e;
}

.role-badge--gym {
  background: #fff7ed;
  color: #c2410c;
}

.profile-fields {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 14px 16px;
  background: #f9fafb;
  border-radius: 10px;
}

.field-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.field-value {
  font-size: 1rem;
  color: #111827;
}

.estado-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 600;
  width: fit-content;
}

.estado--pendiente {
  background: #fef9c3;
  color: #854d0e;
}

.estado--aprobado {
  background: #dcfce7;
  color: #166534;
}

.estado--rechazado {
  background: #fee2e2;
  color: #991b1b;
}
</style>
