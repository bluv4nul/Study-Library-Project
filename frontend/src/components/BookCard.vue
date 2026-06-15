<template>
  <article class="book-card glass-panel">
    <RouterLink class="book-main" :to="`/books/${bookId}`">
      <div class="book-cover">{{ coverLetter }}</div>
      <div>
        <h3>{{ book.title || 'Без названия' }}</h3>
        <p>{{ authorsText }}</p>
        <div class="meta-row">
          <span v-if="book.year">{{ book.year }}</span>
          <span v-if="publisherText">{{ publisherText }}</span>
          <span v-if="book.isbn">ISBN {{ book.isbn }}</span>
        </div>
        <div v-if="genresText" class="tag-row">
          <span v-for="genre in genresText" :key="genre">{{ genre }}</span>
        </div>
      </div>
    </RouterLink>

    <div class="book-actions">
      <button type="button" @click="$emit('edit', book)">Изменить</button>
      <button type="button" class="danger" @click="$emit('remove', book)">Удалить</button>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue';
import { normalizeId } from '../api/libraryApi';

const props = defineProps({ book: { type: Object, required: true } });
defineEmits(['edit', 'remove']);

const bookId = computed(() => normalizeId(props.book));
const coverLetter = computed(() => (props.book.title || 'E').trim().slice(0, 1).toUpperCase());

const authorsText = computed(() => {
  const authors = props.book.authors || props.book.author_ids || [];
  if (!Array.isArray(authors) || authors.length === 0) return 'Автор не указан';
  return authors.map((author) => author.author_name || author.name || author).join(', ');
});

const publisherText = computed(() => {
  const publisher = props.book.publisher || props.book.publisher_id;
  if (!publisher) return '';
  return publisher.publisher_name || publisher.name || publisher;
});

const genresText = computed(() => {
  const genres = props.book.genres || props.book.genre_ids || [];
  if (!Array.isArray(genres)) return [];
  return genres.map((genre) => genre.genre_name || genre.name || genre).filter(Boolean);
});
</script>
