<template>
  <div>
    <PageHeader
      eyebrow="Справочники"
      title="Жанры"
      description="Управление жанрами библиотеки: добавляйте, редактируйте и удаляйте жанры."
    >
      <template #actions>
        <AppButton @click="openCreateModal">+ Новый жанр</AppButton>
      </template>
    </PageHeader>

    <section class="toolbar glass-panel">
      <label class="search-field">
        <span>Поиск</span>
        <input v-model.trim="filters.search" placeholder="Название жанра..." @keyup.enter="loadGenres" />
      </label>
      <label>
        <span>Сортировка</span>
        <select v-model="filters.sort">
          <option value="genre_name">Название</option>
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

    <section v-if="isLoading" class="state-card glass-panel">Загружаю жанры...</section>
    <section v-else-if="genres.length === 0" class="state-card glass-panel">
      <h2>Жанров пока нет</h2>
      <p>Добавьте первый жанр или измените параметры фильтрации.</p>
    </section>
    <section v-else class="entities-table glass-panel">
      <table>
        <thead>
          <tr>
            <th>Название</th>
            <th style="text-align: center">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="genre in genres" :key="getId(genre)">
            <td>{{ genre.genre_name }}</td>
            <td class="actions">
              <AppButton variant="ghost" size="small" @click="openEditModal(genre)">Изменить</AppButton>
              <AppButton variant="ghost" size="small" @click="removeGenre(genre)">Удалить</AppButton>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <div class="pagination glass-panel">
      <button :disabled="filters.page <= 1" @click="changePage(filters.page - 1)">← Назад</button>
      <span>Страница {{ filters.page }}</span>
      <button :disabled="genres.length < filters.limit" @click="changePage(filters.page + 1)">Вперёд →</button>
    </div>

    <BaseModal v-model="isModalOpen" :title="editingGenre ? 'Редактировать жанр' : 'Добавить жанр'" subtitle="Форма жанра">
      <GenreForm
        :genre="editingGenre"
        :submit-text="editingGenre ? 'Сохранить изменения' : 'Создать жанр'"
        @submit="saveGenre"
        @cancel="isModalOpen = false"
      />
    </BaseModal>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue';
import AppButton from '../components/AppButton.vue';
import BaseModal from '../components/BaseModal.vue';
import GenreForm from '../components/GenreForm.vue';
import PageHeader from '../components/PageHeader.vue';
import { libraryApi, normalizeId } from '../api/libraryApi';

const genres = ref([]);
const isLoading = ref(false);
const isModalOpen = ref(false);
const editingGenre = ref(null);
const error = ref('');

const filters = reactive({
  search: '',
  sort: 'genre_name',
  order: 'asc',
  page: 1,
  limit: 20,
});

const getId = (item) => normalizeId(item);

const loadGenres = async () => {
  isLoading.value = true;
  error.value = '';
  try {
    const result = await libraryApi.getGenres({
      q: filters.search || undefined,
      sort: filters.sort,
      order: filters.order,
      page: filters.page,
      limit: filters.limit,
    });
    genres.value = result.items;
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка при загрузке жанров';
  } finally {
    isLoading.value = false;
  }
};

const openCreateModal = () => {
  editingGenre.value = null;
  isModalOpen.value = true;
};

const openEditModal = (genre) => {
  editingGenre.value = genre;
  isModalOpen.value = true;
};

const saveGenre = async (data) => {
  try {
    if (editingGenre.value) {
      await libraryApi.updateGenre(getId(editingGenre.value), data);
    } else {
      await libraryApi.createGenre(data);
    }
    isModalOpen.value = false;
    await loadGenres();
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка при сохранении жанра';
  }
};

const removeGenre = async (genre) => {
  if (!confirm(`Удалить жанр "${genre.genre_name}"?`)) return;
  try {
    await libraryApi.deleteGenre(getId(genre));
    await loadGenres();
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка при удалении жанра';
  }
};

const resetFilters = () => {
  filters.search = '';
  filters.sort = 'genre_name';
  filters.order = 'asc';
  filters.page = 1;
  loadGenres();
};

const changePage = (newPage) => {
  filters.page = newPage;
  loadGenres();
};

onMounted(() => {
  loadGenres();
});
</script>

<style scoped>
.toolbar {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  flex-wrap: wrap;
  align-items: flex-end;
}

.search-field {
  flex: 1;
  min-width: 200px;
}

label {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

span {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-secondary);
}

input,
select {
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  font-size: 1rem;
  font-family: inherit;
}

input:focus,
select:focus {
  outline: none;
  border-color: var(--accent-color);
}

.alert {
  color: #e74c3c;
  margin-bottom: 1rem;
  padding: 1rem;
  background: rgba(231, 76, 60, 0.1);
  border-radius: 0.5rem;
}

.state-card {
  padding: 3rem;
  text-align: center;
  margin-bottom: 2rem;
}

.state-card h2 {
  margin-bottom: 0.5rem;
}

.state-card p {
  color: var(--text-secondary);
}

.entities-table {
  margin-bottom: 2rem;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  border-bottom: 2px solid var(--border-color);
}

th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--text-secondary);
}

td {
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

td.actions {
  text-align: right;
}

.pagination {
  display: flex;
  gap: 1rem;
  justify-content: center;
  align-items: center;
  padding: 1.5rem;
}

button {
  padding: 0.5rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  background: transparent;
  cursor: pointer;
  font-family: inherit;
}

button:hover:not(:disabled) {
  background: var(--hover-bg);
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
