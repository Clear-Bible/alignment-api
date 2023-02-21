<script setup>
import { RouterLink, RouterView } from "vue-router";
</script>

<template>
  <header class="main-header">
    <h1>Alignment Prototype</h1>
    <nav class="main-nav">
      <RouterLink to="/">Home</RouterLink>
      <RouterLink to="/about">About</RouterLink>
    </nav>
  </header>

  <RouterView />
</template>

<style scoped>
header.main-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

nav.main-nav {
  display: flex;
  gap: 8px;
}
</style>
