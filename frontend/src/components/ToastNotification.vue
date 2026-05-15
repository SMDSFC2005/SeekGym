<template>
  <Transition name="toast">
    <div v-if="toastStore.visible" :class="['toast', `toast--${toastStore.type}`]" @click="toastStore.hide()">
      <span class="toast-icon">{{ toastStore.type === 'success' ? '✓' : '✕' }}</span>
      <span class="toast-message">{{ toastStore.message }}</span>
    </div>
  </Transition>
</template>

<script setup>
import { useToastStore } from '@/stores/toastStore'
const toastStore = useToastStore()
</script>

<style scoped>
.toast {
  position: fixed;
  bottom: 28px;
  right: 28px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 20px;
  border-radius: 12px;
  font-size: 0.95rem;
  font-weight: 600;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  cursor: pointer;
  z-index: 9999;
  max-width: 360px;
}

.toast--success {
  background: #111827;
  color: white;
}

.toast--error {
  background: #ef4444;
  color: white;
}

.toast-icon {
  font-size: 1rem;
  flex-shrink: 0;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.25s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(12px);
}
</style>
