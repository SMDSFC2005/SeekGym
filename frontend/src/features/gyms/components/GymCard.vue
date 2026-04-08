<script setup>
import GymStatusBadge from './GymStatusBadge.vue'

defineProps({
  gym: {
    type: Object,
    required: true,
  },
})
</script>

<template>
  <article class="gym-card">
    <div class="gym-card__header">
      <div>
        <h3>{{ gym.name }}</h3>
        <p>{{ gym.municipality }} · {{ gym.postal_code }}</p>
      </div>

      <GymStatusBadge :status="gym.current_status" />
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