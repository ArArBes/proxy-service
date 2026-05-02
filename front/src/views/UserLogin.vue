<template>
  <v-container>
    <v-card>
      <v-card-title>Вход</v-card-title>
      <v-card-text>
        <v-text-field v-model="email" label="Email" />
        <v-text-field v-model="password" label="Пароль" type="password" />
      </v-card-text>
      <v-card-actions>
        <v-btn color="primary" @click="login">Войти</v-btn>
        <v-btn text to="/register">Нет аккаунта?</v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from '../axios'

const email = ref('')
const password = ref('')
const router = useRouter()

const login = async () => {
  try {
    const res = await axios.post('/api/login/', { email: email.value, password: password.value })
    localStorage.setItem('access_token', res.data.access_token)
    localStorage.setItem('refresh_token', res.data.refresh_token)
    router.push('/profile')
  } catch (err) {
    alert('Ошибка входа')
  }
}
</script>