<template>
  <div class="auth-input">
    <label class="auth-input__label">{{ label }}</label>
    <input
      class="auth-input__control"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      @input="$emit('update:modelValue', $event.target.value)"
    />
  </div>
</template>

<script setup>
defineProps({
  label: String,
  modelValue: String,
  type: {
    type: String,
    default: 'text',
  },
  placeholder: {
    type: String,
    default: '',
  },
})

defineEmits(['update:modelValue'])
</script>

<style scoped>
.auth-input {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.auth-input__label {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.auth-input__control {
  height: 46px;
  border: 1px solid #d1d5db;
  border-radius: 12px;
  padding: 0 14px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.auth-input__control:focus {
  border-color: #f97316;
  box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.15);
}
</style>