<template>
  <v-container>
    <v-card>
      <v-card-title>Личный кабинет</v-card-title>
      <v-card-text>
        <p>Email: {{ user.email }}</p>
        <p>Ключ активации: {{ user.activation_key || 'Нет ключа' }}</p>
        <v-btn color="primary" @click="refreshKey">Обновить ключ</v-btn>
        <v-divider class="my-4" />
        <v-text-field v-model="oldPassword" label="Старый пароль" type="password" />
        <v-text-field v-model="newPassword" label="Новый пароль" type="password" />
        <v-btn color="success" @click="changePassword">Сменить пароль</v-btn>
        <v-btn color="error" @click="logout" class="ml-4">Выйти</v-btn>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from '../axios'

const user = ref({ email: '', activation_key: null })
const oldPassword = ref('')
const newPassword = ref('')
const router = useRouter()

const fetchProfile = async () => {
  try {
    const res = await axios.get('/api/profile/')
    user.value = res.data
  } catch (err) {
    console.error(err)
  }
}

const refreshKey = async () => {
  try {
    await axios.post('/api/refresh-key/')
    await fetchProfile()
    alert('Новый ключ отправлен на почту')
  } catch (err) {
    alert('Ошибка обновления ключа')
  }
}

const changePassword = async () => {
  try {
    await axios.patch('/api/change-password/', {
      old_password: oldPassword.value,
      new_password: newPassword.value
    })
    alert('Пароль изменён')
    oldPassword.value = ''
    newPassword.value = ''
  } catch (err) {
    alert('Неверный старый пароль')
  }
}

const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  router.push('/login')
}

onMounted(fetchProfile)
</script>