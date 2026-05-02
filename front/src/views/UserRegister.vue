<template>
  <v-container>
    <v-card>
      <v-card-title>Регистрация</v-card-title>
      <v-card-text>
        <v-text-field v-model="email" label="Email" />
        <v-text-field v-model="password" label="Пароль" type="password" />
        <v-text-field v-model="confirmPassword" label="Подтвердите пароль" type="password" />
      </v-card-text>
      <v-card-actions>
        <v-btn color="primary" @click="register">Зарегистрироваться</v-btn>
        <v-btn text to="/login">Уже есть аккаунт?</v-btn>
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
const confirmPassword = ref('')
const router = useRouter()

const register = async () => {
  if (password.value !== confirmPassword.value) {
    alert('Пароли не совпадают')
    return
  }
  try {
    await axios.post('/api/register/', {
      email: email.value,
      password: password.value,
      confirm_password: confirmPassword.value
    })
    alert('Письмо с ключом отправлено на почту')
    router.push('/login')
  } catch (err) {
    alert('Ошибка регистрации')
  }
}
</script>