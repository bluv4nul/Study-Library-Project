<template>
  <div>
    <PageHeader
      eyebrow="Справочники"
      title="Издательства"
      description="Управление издательствами библиотеки: добавляйте, редактируйте и удаляйте издательства."
    >
      <template #actions>
        <AppButton @click="openCreateModal">+ Новое издательство</AppButton>
      </template>
    </PageHeader>

    <section class="toolbar glass-panel">
      <label class="search-field">
        <span>Поиск</span>
        <input v-model.trim="filters.search" placeholder="Название, город, email..." @keyup.enter="loadPublishers" />
      </label>
      <label>
        <span>Сортировка</span>
        <select v-model="filters.sort">
          <option value="publisher_name">Название</option>
          <option value="publisher_city">Город</option>
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

    <section v-if="isLoading" class="state-card glass-panel">Загружаю издательства...</section>
    <section v-else-if="publishers.length === 0" class="state-card glass-panel">
      <h2>Издательств пока нет</h2>
      <p>Добавьте первое издательство или измените параметры фильтрации.</p>
    </section>
    <section v-else class="entities-table glass-panel">
      <table>
        <thead>
          <tr>
            <th>Название</th>
            <th>Город</th>
            <th>Email</th>
            <th>Веб-сайт</th>
            <th style="text-align: center">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="publisher in publishers" :key="getId(publisher)">
            <td>{{ publisher.publisher_name }}</td>
            <td>{{ publisher.publisher_city || '—' }}</td>
            <td>{{ publisher.email || '—' }}</td>
            <td>
              <a v-if="publisher.publisher_website" :href="publisher.publisher_website" target="_blank" rel="noopener">
                Ссылка
              </a>
              <span v-else>—</span>
            </td>
            <td class="actions">
              <AppButton variant="ghost" size="small" @click="openEditModal(publisher)">Изменить</AppButton>
              <AppButton variant="ghost" size="small" @click="removePublisher(publisher)">Удалить</AppButton>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <div class="pagination glass-panel">
      <button :disabled="filters.page <= 1" @click="changePage(filters.page - 1)">← Назад</button>
      <span>Страница {{ filters.page }}</span>
      <button :disabled="publishers.length < filters.limit" @click="changePage(filters.page + 1)">Вперёд →</button>
    </div>

    <BaseModal v-model="isModalOpen" :title="editingPublisher ? 'Редактировать издательство' : 'Добавить издательство'" subtitle="Форма издательства">
      <PublisherForm
        :publisher="editingPublisher"
        :submit-text="editingPublisher ? 'Сохранить изменения' : 'Создать издательство'"
        @submit="savePublisher"
        @cancel="isModalOpen = false"
      />
    </BaseModal>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue';
import AppButton from '../components/AppButton.vue';
import BaseModal from '../components/BaseModal.vue';
import PageHeader from '../components/PageHeader.vue';
import PublisherForm from '../components/PublisherForm.vue';
import { libraryApi, normalizeId } from '../api/libraryApi';

const publishers = ref([]);
const isLoading = ref(false);
const isModalOpen = ref(false);
const editingPublisher = ref(null);
const error = ref('');

const filters = reactive({
  search: '',
  sort: 'publisher_name',
  order: 'asc',
  page: 1,
  limit: 20,
});

const getId = (item) => normalizeId(item);

const loadPublishers = async () => {
  isLoading.value = true;
  error.value = '';
  try {
    const result = await libraryApi.getPublishers({
      q: filters.search || undefined,
      sort: filters.sort,
      order: filters.order,
      page: filters.page,
      limit: filters.limit,
    });
    publishers.value = result.items;
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка при загрузке издательств';
  } finally {
    isLoading.value = false;
  }
};

const openCreateModal = () => {
  editingPublisher.value = null;
  isModalOpen.value = true;
};

const openEditModal = (publisher) => {
  editingPublisher.value = publisher;
  isModalOpen.value = true;
};

const savePublisher = async (data) => {
  try {
    if (editingPublisher.value) {
      await libraryApi.updatePublisher(getId(editingPublisher.value), data);
    } else {
      await libraryApi.createPublisher(data);
    }
    isModalOpen.value = false;
    await loadPublishers();
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка при сохранении издательства';
  }
};

const removePublisher = async (publisher) => {
  if (!confirm(`Удалить издательство "${publisher.publisher_name}"?`)) return;
  try {
    await libraryApi.deletePublisher(getId(publisher));
    await loadPublishers();
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка при удалении издательства';
  }
};

const resetFilters = () => {
  filters.search = '';
  filters.sort = 'publisher_name';
  filters.order = 'asc';
  filters.page = 1;
  loadPublishers();
};

const changePage = (newPage) => {
  filters.page = newPage;
  loadPublishers();
};

onMounted(() => {
  loadPublishers();
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
