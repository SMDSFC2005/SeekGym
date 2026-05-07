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
    <div class="gym-card__header">
      <div>
        <h3>{{ gym.name }}</h3>
        <p>{{ gym.municipality }} · {{ gym.postal_code }}</p>
      </div>

      <div class="gym-card__header-right">
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

    <div class="gym-card__meta">
      <span>{{ gym.rating }}</span>
      <span>{{ gym.price_per_month }} €/mes</span>
    </div>

    <p class="gym-card__address">{{ gym.address }}</p>

    <div class="gym-card__stats">
      <div>
        <strong>Ocupación actual</strong>
        <p>
          {{ gym.current_occupancy !== null ? gym.current_occupancy + '%' : '—' }}
        </p>
      </div>

      <div>
        <strong>Mejor hora hoy</strong>
        <p>{{ gym.best_time_today ? gym.best_time_today.label : '—' }}</p>
      </div>
    </div>

    <router-link :to="`/gyms/${gym.slug}`" class="gym-card__link">
      Ver detalles
    </router-link>
  </article>
</template>

<style scoped>
.gym-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 1rem;
}

.gym-card__header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
}

.gym-card__header h3 {
  margin: 0;
}

.gym-card__header p {
  margin: 0.25rem 0 0;
  color: #6b7280;
}

.gym-card__header-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.follow-btn {
  width: 30px;
  height: 30px;
  border-radius: 999px;
  border: 1.5px solid #d1d5db;
  background: white;
  color: #6b7280;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
  padding: 0;
  line-height: 1;
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
  opacity: 0.5;
  cursor: not-allowed;
}

.gym-card__meta {
  display: flex;
  gap: 1rem;
  margin-top: 0.8rem;
  color: #374151;
  font-size: 0.95rem;
}

.gym-card__address {
  margin-top: 0.8rem;
  color: #4b5563;
}

.gym-card__stats {
  margin-top: 1rem;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.gym-card__stats strong {
  display: block;
  font-size: 0.9rem;
  color: #374151;
}

.gym-card__stats p {
  margin: 0.35rem 0 0;
  font-size: 1.15rem;
  font-weight: 700;
}

.gym-card__link {
  display: inline-block;
  margin-top: 1rem;
  color: #111827;
  font-weight: 600;
  text-decoration: none;
}

.gym-card__link:hover {
  text-decoration: underline;
}
</style>
