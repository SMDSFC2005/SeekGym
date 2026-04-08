<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({
  provinceId: {
    type: [String, Number],
    default: '',
  },
  municipalityId: {
    type: [String, Number],
    default: '',
  },
  postalCode: {
    type: String,
    default: '',
  },
  provinces: {
    type: Array,
    default: () => [],
  },
  municipalities: {
    type: Array,
    default: () => [],
  },
  postalCodes: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits([
  'apply',
  'province-change',
  'municipality-change',
])

const form = reactive({
  province_id: props.provinceId || '',
  municipality_id: props.municipalityId || '',
  postal_code: props.postalCode || '',
})

watch(
  () => [props.provinceId, props.municipalityId, props.postalCode],
  ([provinceId, municipalityId, postalCode]) => {
    form.province_id = provinceId || ''
    form.municipality_id = municipalityId || ''
    form.postal_code = postalCode || ''
  }
)

function onProvinceChange() {
  form.municipality_id = ''
  form.postal_code = ''

  emit('province-change', {
    province_id: form.province_id,
  })
}

function onMunicipalityChange() {
  form.postal_code = ''

  emit('municipality-change', {
    province_id: form.province_id,
    municipality_id: form.municipality_id,
  })
}

function submit() {
  emit('apply', {
    province_id: form.province_id,
    municipality_id: form.municipality_id,
    postal_code: form.postal_code,
  })
}
</script>

<template>
  <form class="filters" @submit.prevent="submit">
    <div>
      <label for="province">Provincia</label>
      <select
        id="province"
        v-model="form.province_id"
        @change="onProvinceChange"
      >
        <option value="">Todas</option>
        <option
          v-for="province in provinces"
          :key="province.id"
          :value="province.id"
        >
          {{ province.name }}
        </option>
      </select>
    </div>

    <div>
      <label for="municipality">Municipio</label>
      <select
        id="municipality"
        v-model="form.municipality_id"
        :disabled="!form.province_id"
        @change="onMunicipalityChange"
      >
        <option value="">Todos</option>
        <option
          v-for="municipality in municipalities"
          :key="municipality.id"
          :value="municipality.id"
        >
          {{ municipality.name }}
        </option>
      </select>
    </div>

    <div>
      <label for="postal_code">Código postal</label>
      <select
        id="postal_code"
        v-model="form.postal_code"
        :disabled="!form.municipality_id"
      >
        <option value="">Todos</option>
        <option
          v-for="item in postalCodes"
          :key="item.postal_code"
          :value="item.postal_code"
        >
          {{ item.postal_code }}
        </option>
      </select>
    </div>

    <button type="submit">Aplicar</button>
  </form>
</template>

<style scoped>
.filters {
  display: grid;
  grid-template-columns: 1fr 1fr 220px auto;
  gap: 1rem;
  align-items: end;
  margin-bottom: 1.5rem;
}

.filters label {
  display: block;
  margin-bottom: 0.35rem;
  font-weight: 600;
}

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

.filters button:disabled,
.filters select:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .filters {
    grid-template-columns: 1fr;
  }
}
</style>