<template>
  <form class="book-form" @submit.prevent="submitForm">
    <label>
      <span>Название</span>
      <input v-model.trim="form.title" required placeholder="Например, 1984" />
    </label>

    <div class="form-grid">
      <label>
        <span>Год издания</span>
        <input v-model.number="form.year" type="number" min="0" max="2100" placeholder="1949" />
      </label>
      <label>
        <span>ISBN</span>
        <input v-model.trim="form.isbn" placeholder="978-..." />
      </label>
    </div>

    <label>
      <span>Автор</span>
      <select v-model="form.author_ids" multiple>
        <option v-for="author in authors" :key="getId(author)" :value="getId(author)">
          {{ author.author_name || author.name }}
        </option>
      </select>
      <small>Можно выбрать несколько авторов через Ctrl / Cmd.</small>
    </label>

    <label>
      <span>Жанр</span>
      <select v-model="form.genre_ids" multiple>
        <option v-for="genre in genres" :key="getId(genre)" :value="getId(genre)">
          {{ genre.genre_name || genre.name }}
        </option>
      </select>
    </label>

    <label>
      <span>Издательство</span>
      <select v-model="form.publisher_id">
        <option value="">Не выбрано</option>
        <option v-for="publisher in publishers" :key="getId(publisher)" :value="getId(publisher)">
          {{ publisher.publisher_name || publisher.name }}
        </option>
      </select>
    </label>

    <div class="form-actions">
      <AppButton variant="ghost" type="button" @click="$emit('cancel')">Отмена</AppButton>
      <AppButton type="submit">{{ submitText }}</AppButton>
    </div>
  </form>
</template>

<script setup>
import { reactive, watch } from 'vue';
import AppButton from './AppButton.vue';
import { normalizeId } from '../api/libraryApi';

const props = defineProps({
  book: { type: Object, default: null },
  authors: { type: Array, default: () => [] },
  genres: { type: Array, default: () => [] },
  publishers: { type: Array, default: () => [] },
  submitText: { type: String, default: 'Сохранить' },
});

const emit = defineEmits(['submit', 'cancel']);

const form = reactive({
  title: '',
  year: '',
  isbn: '',
  author_ids: [],
  genre_ids: [],
  publisher_id: '',
});

const getId = (item) => normalizeId(item);
const idsFrom = (value) => {
  if (!Array.isArray(value)) return [];
  return value.map((item) => (typeof item === 'string' ? item : normalizeId(item))).filter(Boolean);
};

watch(
  () => props.book,
  (book) => {
    form.title = book?.title || '';
    form.year = book?.year || '';
    form.isbn = book?.isbn || '';
    form.author_ids = idsFrom(book?.authors || book?.author_ids);
    form.genre_ids = idsFrom(book?.genres || book?.genre_ids);
    const publisher = book?.publisher || book?.publisher_id;
    form.publisher_id = typeof publisher === 'string' ? publisher : normalizeId(publisher);
  },
  { immediate: true },
);

const submitForm = () => {
  emit('submit', {
    title: form.title,
    year: form.year ? Number(form.year) : null,
    isbn: form.isbn || null,
    author_ids: form.author_ids,
    genre_ids: form.genre_ids,
    publisher_id: form.publisher_id || null,
  });
};
</script>
