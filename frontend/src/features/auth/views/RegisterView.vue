<template>
  <div class="auth-container">
    <form @submit.prevent="onSubmit" class="auth-box">
      <h2 class="title">Crear cuenta</h2>

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
          data-field="email"
          editor-type="dxTextBox"
          :editor-options="{
            stylingMode: 'filled',
            placeholder: 'Email'
          }"
        >
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

        <DxItem
          data-field="rol"
          editor-type="dxSelectBox"
          :editor-options="{
            items: roles,
            valueExpr: 'value',
            displayExpr: 'label',
            stylingMode: 'filled',
            placeholder: 'Tipo de cuenta'
          }"
        >
          <DxRequiredRule message="Selecciona un tipo de cuenta" />
          <DxLabel :visible="false" />
        </DxItem>

        <DxButtonItem>
          <DxButtonOptions
            width="100%"
            type="default"
            :use-submit-behavior="true"
            text="Registrarse"
          />
        </DxButtonItem>
      </DxForm>

      <p v-if="message" :class="isError ? 'error' : 'success'">
        {{ message }}
      </p>

      <div class="link">
        <router-link to="/login">Ya tengo cuenta</router-link>
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
  DxButtonOptions,
} from 'devextreme-vue/form'

const router = useRouter()
const userStore = useUserStore()

const roles = [
  { value: 'NORMAL', label: 'Usuario normal' },
  { value: 'GIMNASIO', label: 'Solicitar cuenta de gimnasio' },
]

const formData = ref({
  username: '',
  email: '',
  password: '',
  rol: 'NORMAL',
})

const loading = ref(false)
const message = ref('')
const isError = ref(false)

async function onSubmit() {
  loading.value = true
  message.value = ''
  isError.value = false

  const result = await userStore.register(
    formData.value.username,
    formData.value.password,
    formData.value.email,
    formData.value.rol
  )

  loading.value = false

  if (result.isOk) {
    if (formData.value.rol === 'GIMNASIO') {
      message.value = 'Solicitud de cuenta gimnasio enviada. Un administrador debe aprobarla.'
    } else {
      message.value = 'Usuario creado correctamente'
    }

    setTimeout(() => router.push('/login'), 1500)
  } else {
    isError.value = true
    message.value = 'Error al registrar'
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

.success {
  color: green;
  margin-top: 10px;
}

.link {
  margin-top: 15px;
  text-align: center;
}
</style>