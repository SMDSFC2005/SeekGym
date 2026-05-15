<script setup>
import { ref } from 'vue'
import { useUserStore } from '@/features/auth/store/userStore'
import { toggleFollowGymService } from '../services/gymsService'
import GymStatusBadge from './GymStatusBadge.vue'

const props = defineProps({
  gym: {
    type: Object,
    required: true,
  },
})

const userStore = useUserStore()
const isFollowing = ref(props.gym.is_following ?? false)
const followLoading = ref(false)

const canFollow = () => !!userStore.user

async function toggleFollow(e) {
  e.preventDefault()
  if (followLoading.value) return
  followLoading.value = true
  try {
    const response = await toggleFollowGymService(props.gym.slug)
    if (response?.status === 200 || response?.status === 201) {
      isFollowing.value = !isFollowing.value
    }
  } finally {
    followLoading.value = false
  }
}
</script>

<template>
  <article class="gym-card">
    <!-- Imagen / placeholder -->
    <div class="gym-card__image">
      <img v-if="gym.image_url" :src="gym.image_url" :alt="gym.name" class="gym-card__img" />
      <div v-else class="gym-card__img-placeholder">
        <span>{{ gym.name[0]?.toUpperCase() }}</span>
      </div>

      <div class="gym-card__image-overlay">
        <GymStatusBadge :status="gym.current_status" />
        <button
          v-if="canFollow()"
          class="follow-btn"
          :class="{ 'follow-btn--following': isFollowing }"
          :disabled="followLoading"
          @click="toggleFollow"
        >
          {{ isFollowing ? '✓' : '+' }}
        </button>
      </div>
    </div>

    <div class="gym-card__body">
      <div class="gym-card__header">
        <h3>{{ gym.name }}</h3>
        <p>{{ gym.municipality }} · {{ gym.postal_code }}</p>
      </div>

      <div class="gym-card__meta">
        <span>⭐ {{ gym.rating }}</span>
        <span>{{ gym.price_per_month }} €/mes</span>
      </div>

      <div class="gym-card__stats">
        <div>
          <strong>Ocupación actual</strong>
          <p>{{ gym.current_occupancy !== null ? gym.current_occupancy + '%' : '—' }}</p>
        </div>
        <div>
          <strong>Mejor hora hoy</strong>
          <p>{{ gym.best_time_today ? gym.best_time_today.label : '—' }}</p>
        </div>
      </div>

      <router-link :to="`/gyms/${gym.slug}`" class="gym-card__link">
        Ver detalles →
      </router-link>
    </div>
  </article>
</template>

<style scoped>
.gym-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  overflow: hidden;
  transition: box-shadow 0.15s;
}

.gym-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

/* Imagen */
.gym-card__image {
  position: relative;
  width: 100%;
  height: 160px;
}

.gym-card__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.gym-card__img-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.25);
}

.gym-card__image-overlay {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.follow-btn {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  border: none;
  background: rgba(255, 255, 255, 0.9);
  color: #374151;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
  padding: 0;
  line-height: 1;
  backdrop-filter: blur(4px);
}

.follow-btn:hover {
  background: white;
  color: #111827;
}

.follow-btn--following {
  background: #111827;
  color: white;
}

.follow-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Contenido */
.gym-card__body {
  padding: 1rem;
}

.gym-card__header h3 {
  margin: 0;
  font-size: 1.05rem;
  color: #111827;
}

.gym-card__header p {
  margin: 0.2rem 0 0;
  color: #6b7280;
  font-size: 0.88rem;
}

.gym-card__meta {
  display: flex;
  gap: 1rem;
  margin-top: 0.6rem;
  color: #374151;
  font-size: 0.9rem;
}

.gym-card__stats {
  margin-top: 0.8rem;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.8rem;
}

.gym-card__stats strong {
  display: block;
  font-size: 0.8rem;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.gym-card__stats p {
  margin: 0.2rem 0 0;
  font-size: 1rem;
  font-weight: 700;
  color: #111827;
}

.gym-card__link {
  display: inline-block;
  margin-top: 0.9rem;
  color: #111827;
  font-weight: 600;
  font-size: 0.9rem;
  text-decoration: none;
}

.gym-card__link:hover {
  text-decoration: underline;
}
</style>
