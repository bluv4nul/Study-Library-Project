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
      <span>Авторы</span>
      <EntitySelect
        :items="authors"
        :model-value="form.author_ids"
        :is-multiple="true"
        placeholder="Найти или добавить автора..."
        @update:model-value="(v) => (form.author_ids = v)"
        @createNew="handleCreateAuthor"
      />
    </label>

    <label>
      <span>Жанры</span>
      <EntitySelect
        :items="genres"
        :model-value="form.genre_ids"
        :is-multiple="true"
        placeholder="Найти или добавить жанр..."
        @update:model-value="(v) => (form.genre_ids = v)"
        @createNew="handleCreateGenre"
      />
    </label>

    <label>
      <span>Издательство</span>
      <EntitySelect
        :items="publishers"
        :model-value="form.publisher_id"
        :is-multiple="false"
        placeholder="Найти или добавить издательство..."
        @update:model-value="(v) => (form.publisher_id = v)"
        @createNew="handleCreatePublisher"
      />
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
import EntitySelect from './EntitySelect.vue';
import { normalizeId } from '../api/libraryApi';

const props = defineProps({
  book: { type: Object, default: null },
  authors: { type: Array, default: () => [] },
  genres: { type: Array, default: () => [] },
  publishers: { type: Array, default: () => [] },
  submitText: { type: String, default: 'Сохранить' },
});

const emit = defineEmits(['submit', 'cancel', 'createAuthor', 'createGenre', 'createPublisher']);

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

const handleCreate = (eventName, name, onCreated) => {
  emit(eventName, {
    name,
    callback: (createdEntity) => {
      if (!createdEntity) return;
      onCreated(createdEntity);
    },
  });
};

const handleCreateAuthor = (name) => {
  handleCreate('createAuthor', name, (created) => {
    const id = normalizeId(created);
    if (id && !form.author_ids.includes(id)) {
      form.author_ids = [...form.author_ids, id];
    }
  });
};

const handleCreateGenre = (name) => {
  handleCreate('createGenre', name, (created) => {
    const id = normalizeId(created);
    if (id && !form.genre_ids.includes(id)) {
      form.genre_ids = [...form.genre_ids, id];
    }
  });
};

const handleCreatePublisher = (name) => {
  handleCreate('createPublisher', name, (created) => {
    const id = normalizeId(created);
    if (id) {
      form.publisher_id = id;
    }
  });
};
</script>
