<template>
  <div class="auth-container">
    <form @submit.prevent="onSubmit" class="auth-box">
      
      <h2 class="title">Iniciar sesión</h2>

      <DxForm :form-data="formData" :disabled="loading">
        
        <DxItem
          data-field="username"
          editor-type="dxTextBox"
          :editor-options="{
            stylingMode: 'filled',
            placeholder: 'Usuario'
          }"
        >
          <DxRequiredRule message="El usuario es obligatorio" />
          <DxLabel :visible="false" />
        </DxItem>

        <DxItem
          data-field="password"
          editor-type="dxTextBox"
          :editor-options="{
            stylingMode: 'filled',
            placeholder: 'Contraseña',
            mode: 'password'
          }"
        >
          <DxRequiredRule message="La contraseña es obligatoria" />
          <DxLabel :visible="false" />
        </DxItem>

        <DxButtonItem>
          <DxButtonOptions
            width="100%"
            type="default"
            :use-submit-behavior="true"
          >
          </DxButtonOptions>
        </DxButtonItem>

      </DxForm>

      <p v-if="error" class="error">{{ error }}</p>

      <div class="link">
        <router-link to="/register">Crear cuenta</router-link>
      </div>

    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/userStore'

import DxForm, {
  DxItem,
  DxRequiredRule,
  DxLabel,
  DxButtonItem,
  DxButtonOptions
} from 'devextreme-vue/form'

const router = useRouter()
const userStore = useUserStore()

const formData = ref({
  username: '',
  password: ''
})

const loading = ref(false)
const error = ref('')

async function onSubmit() {
  loading.value = true
  error.value = ''

  const result = await userStore.login(
    formData.value.username,
    formData.value.password
  )

  loading.value = false

  if (result.isOk) {
    router.push('/')
  } else {
    error.value = result.message
  }
}
</script>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f9fafb;
}

.auth-box {
  width: 360px;
  padding: 32px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05);
}

.title {
  text-align: center;
  margin-bottom: 20px;
}

.error {
  color: red;
  margin-top: 10px;
}

.link {
  margin-top: 15px;
  text-align: center;
}
</style>