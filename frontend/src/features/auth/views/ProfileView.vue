<template>
  <div class="profile-container">
    <div class="profile-box">
      <button class="back-btn" @click="router.push('/home')">← Volver</button>

      <div class="profile-header">
        <div class="avatar-wrapper" @click="photoInput.click()">
          <img v-if="photoUrl" :src="photoUrl" class="avatar-img" alt="Foto de perfil" />
          <div v-else class="avatar">{{ avatarLetter }}</div>
          <div class="avatar-overlay">
            {{ uploading ? '...' : 'Cambiar' }}
          </div>
          <input
            ref="photoInput"
            type="file"
            accept="image/*"
            class="file-input-hidden"
            @change="onPhotoChange"
          />
        </div>

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
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/userStore'
import { useToastStore } from '@/stores/toastStore'
import { uploadProfilePhotoService } from '../services/authService'

const router = useRouter()
const userStore = useUserStore()
const toastStore = useToastStore()
const user = userStore.user

const photoInput = ref(null)
const uploading = ref(false)
// pillamos la foto actual del usuario si tiene, si no null
const photoUrl = ref(user?.profile_photo_url || null)

// cuando el usuario selecciona una imagen nueva la subimos al backend
async function onPhotoChange(e) {
  const file = e.target.files[0]
  if (!file) return
  uploading.value = true
  const res = await uploadProfilePhotoService(file)
  uploading.value = false
  // limpiamos el input para que se pueda volver a seleccionar la misma foto
  photoInput.value.value = ''
  if (res?.status === 200) {
    photoUrl.value = res.data.profile_photo_url
    userStore.user.profile_photo_url = res.data.profile_photo_url
    toastStore.show('Foto actualizada correctamente')
  } else {
    toastStore.show('Error al subir la foto', 'error')
  }
}

// la inicial del usuario para el avatar de fallback
const avatarLetter = computed(() => user?.username?.[0]?.toUpperCase() ?? '?')

// texto del badge de rol: Admin, Gym o nada
const roleLabel = computed(() => {
  if (user?.is_superuser) return 'Admin'
  if (user?.rol === 'GIMNASIO') return 'Gym'
  return null
})

// clase CSS del badge según el rol
const roleBadgeClass = computed(() => {
  if (user?.is_superuser) return 'role-badge--admin'
  if (user?.rol === 'GIMNASIO') return 'role-badge--gym'
  return ''
})

// texto legible del estado de solicitud de gym
const estadoLabel = computed(() => {
  const map = {
    PENDIENTE: 'Pendiente de aprobación',
    APROBADO: 'Aprobado',
    RECHAZADO: 'Rechazado',
    NONE: '-',
  }
  return map[user?.estado_gym] ?? '-'
})

// clase CSS del badge del estado para poner el color adecuado
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

.avatar-wrapper {
  position: relative;
  width: 72px;
  height: 72px;
  border-radius: 50%;
  cursor: pointer;
  flex-shrink: 0;
}

.avatar-wrapper:hover .avatar-overlay {
  opacity: 1;
}

.avatar-img {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  object-fit: cover;
  display: block;
}

.avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: #111827;
  color: white;
  font-size: 1.8rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-overlay {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  font-size: 0.72rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.15s;
}

.file-input-hidden {
  display: none;
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
