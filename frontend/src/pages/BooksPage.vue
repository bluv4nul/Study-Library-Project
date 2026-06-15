<template>
  <div>
    <PageHeader
      eyebrow="Коллекция"
      title="Электронная библиотека"
      description="Добавляйте, редактируйте, фильтруйте и сортируйте книги в едином минималистичном интерфейсе."
    >
      <template #actions>
        <AppButton @click="openCreateModal">+ Новая книга</AppButton>
      </template>
    </PageHeader>

    <section class="toolbar glass-panel">
      <label class="search-field">
        <span>Поиск</span>
        <input v-model.trim="filters.search" placeholder="Название, автор, ISBN..." @keyup.enter="loadBooks" />
      </label>
      <label>
        <span>Автор</span>
        <select v-model="filters.author_id">
          <option value="">Все</option>
          <option v-for="author in authors" :key="getId(author)" :value="getId(author)">{{ author.author_name || author.name }}</option>
        </select>
      </label>
      <label>
        <span>Жанр</span>
        <select v-model="filters.genre_id">
          <option value="">Все</option>
          <option v-for="genre in genres" :key="getId(genre)" :value="getId(genre)">{{ genre.genre_name || genre.name }}</option>
        </select>
      </label>
      <label>
        <span>Сортировка</span>
        <select v-model="filters.sort">
          <option value="title">Название</option>
          <option value="year">Год</option>
          <option value="isbn">ISBN</option>
        </select>
      </label>
      <label>
        <span>Порядок</span>
        <select v-model="filters.order">
          <option value="asc">По возрастанию</option>
          <option value="desc">По убыванию</option>
        </select>
      </label>
      <AppButton variant="ghost" @click="resetFilters">Сбросить</AppButton>
    </section>

    <p v-if="error" class="alert">{{ error }}</p>

    <section v-if="isLoading" class="state-card glass-panel">Загружаю книги...</section>
    <section v-else-if="books.length === 0" class="state-card glass-panel">
      <h2>Книг пока нет</h2>
      <p>Создайте первую книгу или измените параметры фильтрации.</p>
    </section>
    <section v-else class="books-grid">
      <BookCard v-for="book in books" :key="getId(book)" :book="book" @edit="openEditModal" @remove="removeBook" />
    </section>

    <div class="pagination glass-panel">
      <button :disabled="filters.page <= 1" @click="changePage(filters.page - 1)">← Назад</button>
      <span>Страница {{ filters.page }}</span>
      <button :disabled="books.length < filters.limit" @click="changePage(filters.page + 1)">Вперёд →</button>
    </div>

    <BaseModal v-model="isModalOpen" :title="editingBook ? 'Редактировать книгу' : 'Добавить книгу'" subtitle="Форма книги">
      <BookForm
        :book="editingBook"
        :authors="authors"
        :genres="genres"
        :publishers="publishers"
        :submit-text="editingBook ? 'Сохранить изменения' : 'Создать книгу'"
        @submit="saveBook"
        @cancel="isModalOpen = false"
      />
    </BaseModal>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue';
import AppButton from '../components/AppButton.vue';
import BaseModal from '../components/BaseModal.vue';
import BookCard from '../components/BookCard.vue';
import BookForm from '../components/BookForm.vue';
import PageHeader from '../components/PageHeader.vue';
import { libraryApi, normalizeId } from '../api/libraryApi';

const books = ref([]);
const authors = ref([]);
const genres = ref([]);
const publishers = ref([]);
const isLoading = ref(false);
const isModalOpen = ref(false);
const editingBook = ref(null);
const error = ref('');

const filters = reactive({
  search: '',
  author_id: '',
  genre_id: '',
  sort: 'title',
  order: 'asc',
  page: 1,
  limit: 12,
});

const getId = (item) => normalizeId(item);

const cleanParams = () => Object.fromEntries(Object.entries(filters).filter(([, value]) => value !== '' && value !== null));

const loadBooks = async () => {
  isLoading.value = true;
  error.value = '';
  try {
    const result = await libraryApi.getBooks(cleanParams());
    books.value = result.items;
  } catch (err) {
    error.value = 'Не удалось загрузить книги. Проверьте, запущен ли backend на порту 3000.';
  } finally {
    isLoading.value = false;
  }
};

const loadDictionaries = async () => {
  try {
    const [authorsData, genresData, publishersData] = await Promise.all([
      libraryApi.getAuthors(),
      libraryApi.getGenres(),
      libraryApi.getPublishers(),
    ]);
    authors.value = authorsData.items;
    genres.value = genresData.items;
    publishers.value = publishersData.items;
  } catch (err) {
    error.value = 'Справочники авторов, жанров и издательств не загрузились.';
  }
};

const openCreateModal = () => {
  editingBook.value = null;
  isModalOpen.value = true;
};

const openEditModal = (book) => {
  editingBook.value = book;
  isModalOpen.value = true;
};

const saveBook = async (payload) => {
  try {
    if (editingBook.value) {
      await libraryApi.updateBook(getId(editingBook.value), payload);
    } else {
      await libraryApi.createBook(payload);
    }
    isModalOpen.value = false;
    await loadBooks();
  } catch (err) {
    error.value = 'Не удалось сохранить книгу. Проверьте обязательные поля и уникальность ISBN.';
  }
};

const removeBook = async (book) => {
  const title = book.title || 'эту книгу';
  if (!confirm(`Удалить «${title}» из библиотеки?`)) return;
  try {
    await libraryApi.deleteBook(getId(book));
    await loadBooks();
  } catch (err) {
    error.value = 'Не удалось удалить книгу.';
  }
};

const resetFilters = () => {
  filters.search = '';
  filters.author_id = '';
  filters.genre_id = '';
  filters.sort = 'title';
  filters.order = 'asc';
  filters.page = 1;
  loadBooks();
};

const changePage = (page) => {
  filters.page = page;
  loadBooks();
};

watch(() => [filters.author_id, filters.genre_id, filters.sort, filters.order], () => {
  filters.page = 1;
  loadBooks();
});

onMounted(async () => {
  await loadDictionaries();
  await loadBooks();
});
</script>
