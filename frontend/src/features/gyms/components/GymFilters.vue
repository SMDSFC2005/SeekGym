<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({
  city: {
    type: String,
    default: 'Sevilla',
  },
  postalCode: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['apply'])

const form = reactive({
  city: props.city,
  postal_code: props.postalCode,
})

watch(
  () => [props.city, props.postalCode],
  ([city, postalCode]) => {
    form.city = city || 'Sevilla'
    form.postal_code = postalCode || ''
  }
)

function submit() {
  emit('apply', {
    city: form.city,
    postal_code: form.postal_code,
  })
}
</script>

<template>
  <form class="filters" @submit.prevent="submit">
    <div>
      <label for="city">Ciudad</label>
      <input id="city" v-model="form.city" type="text" />
    </div>

    <div>
      <label for="postal_code">Código postal</label>
      <select id="postal_code" v-model="form.postal_code">
        <option value="">Todos</option>
        <option value="41020">41020</option>
        <option value="41019">41019</option>
      </select>
    </div>

    <button type="submit">Aplicar</button>
  </form>
</template>

<style scoped>
.filters {
  display: grid;
  grid-template-columns: 1fr 220px auto;
  gap: 1rem;
  align-items: end;
  margin-bottom: 1.5rem;
}

.filters label {
  display: block;
  margin-bottom: 0.35rem;
  font-weight: 600;
}

.filters input,
.filters select,
.filters button {
  width: 100%;
  padding: 0.75rem;
  border-radius: 12px;
  border: 1px solid #d1d5db;
}

.filters button {
  background: #111827;
  color: white;
  cursor: pointer;
}

@media (max-width: 768px) {
  .filters {
    grid-template-columns: 1fr;
  }
}
</style>