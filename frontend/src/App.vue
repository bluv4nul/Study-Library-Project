<template>
  <div class="app-shell">
    <header class="topbar glass-panel">
      <RouterLink class="brand" to="/books" aria-label="ElectroLibrary">
        <span class="brand-icon">⌘</span>
        <span>
          <strong>ElectroLibrary</strong>
          <small>умная электронная библиотека</small>
        </span>
      </RouterLink>

      <nav class="nav-links">
        <RouterLink to="/books">Книги</RouterLink>
        <RouterLink to="/about">О проекте</RouterLink>
      </nav>
    </header>

    <main class="page-container">
      <RouterView />
    </main>
  </div>
</template>
