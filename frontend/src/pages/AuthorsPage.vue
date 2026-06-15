<template>
  <div>
    <PageHeader
      eyebrow="Справочники"
      title="Авторы"
      description="Управление авторами библиотеки: добавляйте, редактируйте и удаляйте авторов."
    >
      <template #actions>
        <AppButton @click="openCreateModal">+ Новый автор</AppButton>
      </template>
    </PageHeader>

    <section class="toolbar glass-panel">
      <label class="search-field">
        <span>Поиск</span>
        <input v-model.trim="filters.search" placeholder="Имя, никнейм, email..." @keyup.enter="loadAuthors" />
      </label>
      <label>
        <span>Сортировка</span>
        <select v-model="filters.sort">
          <option value="author_name">Имя</option>
          <option value="email">Email</option>
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

    <section v-if="isLoading" class="state-card glass-panel">Загружаю авторов...</section>
    <section v-else-if="authors.length === 0" class="state-card glass-panel">
      <h2>Авторов пока нет</h2>
      <p>Добавьте первого автора или измените параметры фильтрации.</p>
    </section>
    <section v-else class="entities-table glass-panel">
      <table>
        <thead>
          <tr>
            <th>Имя</th>
            <th>Никнейм</th>
            <th>Email</th>
            <th>Социальные сети</th>
            <th style="text-align: center">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="author in authors" :key="getId(author)">
            <td>{{ author.author_name }}</td>
            <td>{{ author.author_nickname || '—' }}</td>
            <td>{{ author.email || '—' }}</td>
            <td>
              <a v-if="author.social_media_link" :href="author.social_media_link" target="_blank" rel="noopener">
                Ссылка
              </a>
              <span v-else>—</span>
            </td>
            <td class="actions">
              <AppButton variant="ghost" size="small" @click="openEditModal(author)">Изменить</AppButton>
              <AppButton variant="ghost" size="small" @click="removeAuthor(author)">Удалить</AppButton>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <div class="pagination glass-panel">
      <button :disabled="filters.page <= 1" @click="changePage(filters.page - 1)">← Назад</button>
      <span>Страница {{ filters.page }}</span>
      <button :disabled="authors.length < filters.limit" @click="changePage(filters.page + 1)">Вперёд →</button>
    </div>

    <BaseModal v-model="isModalOpen" :title="editingAuthor ? 'Редактировать автора' : 'Добавить автора'" subtitle="Форма автора">
      <AuthorForm
        :author="editingAuthor"
        :submit-text="editingAuthor ? 'Сохранить изменения' : 'Создать автора'"
        @submit="saveAuthor"
        @cancel="isModalOpen = false"
      />
    </BaseModal>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue';
import AppButton from '../components/AppButton.vue';
import AuthorForm from '../components/AuthorForm.vue';
import BaseModal from '../components/BaseModal.vue';
import PageHeader from '../components/PageHeader.vue';
import { libraryApi, normalizeId } from '../api/libraryApi';

const authors = ref([]);
const isLoading = ref(false);
const isModalOpen = ref(false);
const editingAuthor = ref(null);
const error = ref('');

const filters = reactive({
  search: '',
  sort: 'author_name',
  order: 'asc',
  page: 1,
  limit: 20,
});

const getId = (item) => normalizeId(item);

const loadAuthors = async () => {
  isLoading.value = true;
  error.value = '';
  try {
    const result = await libraryApi.getAuthors({
      q: filters.search || undefined,
      sort: filters.sort,
      order: filters.order,
      page: filters.page,
      limit: filters.limit,
    });
    authors.value = result.items;
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка при загрузке авторов';
  } finally {
    isLoading.value = false;
  }
};

const openCreateModal = () => {
  editingAuthor.value = null;
  isModalOpen.value = true;
};

const openEditModal = (author) => {
  editingAuthor.value = author;
  isModalOpen.value = true;
};

const saveAuthor = async (data) => {
  try {
    if (editingAuthor.value) {
      await libraryApi.updateAuthor(getId(editingAuthor.value), data);
    } else {
      await libraryApi.createAuthor(data);
    }
    isModalOpen.value = false;
    await loadAuthors();
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка при сохранении автора';
  }
};

const removeAuthor = async (author) => {
  if (!confirm(`Удалить автора "${author.author_name}"?`)) return;
  try {
    await libraryApi.deleteAuthor(getId(author));
    await loadAuthors();
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка при удалении автора';
  }
};

const resetFilters = () => {
  filters.search = '';
  filters.sort = 'author_name';
  filters.order = 'asc';
  filters.page = 1;
  loadAuthors();
};

const changePage = (newPage) => {
  filters.page = newPage;
  loadAuthors();
};

onMounted(() => {
  loadAuthors();
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

a {
  color: var(--accent-color);
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
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
