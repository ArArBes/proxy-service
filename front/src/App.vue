<template>
  <v-app>
    <v-app-bar app color="primary" dark>
      <v-toolbar-title>Proxy Service</v-toolbar-title>
      <v-spacer />
      <v-btn text to="/login">Login</v-btn>
      <v-btn text to="/register">Register</v-btn>
    </v-app-bar>
    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>
