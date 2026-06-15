<template>
  <div>
    <RouterLink class="back-link" to="/books">← Назад к списку</RouterLink>

    <section v-if="isLoading" class="state-card glass-panel">Загружаю книгу...</section>
    <section v-else-if="error" class="state-card glass-panel">
      <h1>Книга не найдена</h1>
      <p>{{ error }}</p>
    </section>
    <section v-else class="details-card glass-panel">
      <div class="details-cover">{{ coverLetter }}</div>
      <div class="details-content">
        <p class="eyebrow">Карточка книги</p>
        <h1>{{ book.title }}</h1>
        <dl>
          <div>
            <dt>Авторы</dt>
            <dd>{{ authorsText }}</dd>
          </div>
          <div>
            <dt>Жанры</dt>
            <dd>{{ genresText }}</dd>
          </div>
          <div>
            <dt>Издательство</dt>
            <dd>{{ publisherText }}</dd>
          </div>
          <div>
            <dt>Год издания</dt>
            <dd>{{ book.year || 'Не указан' }}</dd>
          </div>
          <div>
            <dt>ISBN</dt>
            <dd>{{ book.isbn || 'Не указан' }}</dd>
          </div>
        </dl>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { libraryApi } from '../api/libraryApi';

const props = defineProps({ id: { type: String, required: true } });

const book = ref({});
const isLoading = ref(true);
const error = ref('');

const coverLetter = computed(() => (book.value.title || 'E').slice(0, 1).toUpperCase());
const authorsText = computed(() => {
  const authors = book.value.authors || book.value.author_ids || [];
  return Array.isArray(authors) && authors.length
    ? authors.map((author) => author.author_name || author.name || author).join(', ')
    : 'Не указаны';
});
const genresText = computed(() => {
  const genres = book.value.genres || book.value.genre_ids || [];
  return Array.isArray(genres) && genres.length
    ? genres.map((genre) => genre.genre_name || genre.name || genre).join(', ')
    : 'Не указаны';
});
const publisherText = computed(() => {
  const publisher = book.value.publisher || book.value.publisher_id;
  return publisher?.publisher_name || publisher?.name || publisher || 'Не указано';
});

onMounted(async () => {
  try {
    book.value = await libraryApi.getBook(props.id);
  } catch (err) {
    error.value = 'Проверьте корректность ссылки или наличие книги на сервере.';
  } finally {
    isLoading.value = false;
  }
});
</script>
