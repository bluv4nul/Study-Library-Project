<template>
  <div>
    <PageHeader
      eyebrow="О проекте"
      title="ElectroLibrary"
      description="Командный учебный проект: электронная библиотека с Vue 3, FastAPI, MongoDB и Docker."
    />

    <section class="about-grid">
      <article class="glass-panel info-card">
        <h2>Что делает фронтенд</h2>
        <p>Отображает список книг, позволяет создавать, редактировать и удалять записи, использовать фильтры, сортировку, страницы и отдельную карточку книги.</p>
      </article>
      <article class="glass-panel info-card">
        <h2>Стек</h2>
        <p>Vue 3, Vite, Vue Router, Axios, компонентный подход, слоты и минималистичный Apple-like интерфейс.</p>
      </article>
      <article class="glass-panel info-card">
        <h2>Интеграция</h2>
        <p>Клиент работает с backend API по адресу /api и готов к запуску отдельно или внутри Docker Compose.</p>
      </article>
    </section>
  </div>
</template>

<script setup>
import PageHeader from '../components/PageHeader.vue';
</script>
