<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    default: null,
  },
})

const label = computed(() => {
  if (props.status === 'GOOD') return 'Buen momento'
  if (props.status === 'MEDIUM') return 'Con espera'
  if (props.status === 'AVOID') return 'Mejor evitar'
  return 'Sin datos'
})

const badgeClass = computed(() => {
  if (props.status === 'GOOD') return 'badge badge--good'
  if (props.status === 'MEDIUM') return 'badge badge--medium'
  if (props.status === 'AVOID') return 'badge badge--avoid'
  return 'badge'
})
</script>

<template>
  <span :class="badgeClass">{{ label }}</span>
</template>

<style scoped>
.badge {
  display: inline-block;
  padding: 0.4rem 0.75rem;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 600;
  background: #eeeeee;
}

.badge--good {
  background: #dcfce7;
  color: #166534;
}

.badge--medium {
  background: #fef3c7;
  color: #92400e;
}

.badge--avoid {
  background: #fee2e2;
  color: #991b1b;
}
</style>