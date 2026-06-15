<template>
  <div class="entity-select">
    <div class="input-wrapper">
      <input
        v-model="searchQuery"
        type="text"
        :placeholder="placeholder"
        @keydown.enter="addNew"
        @focus="isOpen = true"
        @blur="setTimeout(() => (isOpen = false), 200)"
      />
      <button
        v-if="searchQuery.trim() && !isEntityExists"
        type="button"
        class="add-btn"
        @click="addNew"
        title="Добавить новый элемент"
      >
        + Новый
      </button>
    </div>

    <div v-if="isOpen && searchQuery" class="suggestions">
      <div v-if="filteredItems.length === 0" class="no-results">
        Введите название для создания нового
      </div>
      <button
        v-for="item in filteredItems"
        :key="getId(item)"
        type="button"
        class="suggestion-item"
        @click="selectItem(item)"
      >
        {{ getLabel(item) }}
      </button>
    </div>

    <div v-if="isMultiple && modelValue.length > 0" class="selected-items">
      <div v-for="itemId in modelValue" :key="itemId" class="tag">
        {{ getItemLabel(itemId) }}
        <button type="button" @click="removeItem(itemId)" class="remove-btn">×</button>
      </div>
    </div>

    <div v-if="!isMultiple && selectedOption" class="selected-items single">
      <div class="tag">
        {{ getLabel(selectedOption) }}
        <button type="button" @click="removeItem(getId(selectedOption))" class="remove-btn">×</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { normalizeId } from '../api/libraryApi';

const props = defineProps({
  items: { type: Array, required: true },
  modelValue: { type: [Array, String], required: true },
  isMultiple: { type: Boolean, default: false },
  labelField: { type: String, default: 'name' },
  placeholder: { type: String, default: 'Начните вводить...' },
});

const emit = defineEmits(['update:modelValue', 'createNew']);

const searchQuery = ref('');
const isOpen = ref(false);

const getId = (item) => normalizeId(item);
const getLabel = (item) => {
  const label = item.author_name || item.genre_name || item.publisher_name || item.name || '';
  return label;
};

const getItemLabel = (itemId) => {
  const item = props.items.find((i) => getId(i) === itemId);
  return item ? getLabel(item) : itemId;
};

const filteredItems = computed(() => {
  if (!searchQuery.value) return [];
  const q = searchQuery.value.toLowerCase();
  return props.items.filter((item) => getLabel(item).toLowerCase().includes(q));
});

const selectedOption = computed(() => {
  if (props.isMultiple || !props.modelValue) return null;
  return props.items.find((item) => getId(item) === props.modelValue) || null;
});

const isEntityExists = computed(() => {
  return filteredItems.value.length > 0;
});


const selectItem = (item) => {
  const itemId = getId(item);
  if (props.isMultiple) {
    const current = Array.isArray(props.modelValue) ? props.modelValue : [];
    if (!current.includes(itemId)) {
      emit('update:modelValue', [...current, itemId]);
    }
  } else {
    emit('update:modelValue', itemId);
  }
  searchQuery.value = '';
  isOpen.value = false;
};

const removeItem = (itemId) => {
  if (props.isMultiple) {
    const current = Array.isArray(props.modelValue) ? props.modelValue : [];
    emit('update:modelValue', current.filter((id) => id !== itemId));
  } else {
    emit('update:modelValue', '');
  }
};

const addNew = () => {
  if (searchQuery.value.trim() && !isEntityExists.value) {
    emit('createNew', searchQuery.value.trim());
    searchQuery.value = '';
  }
};
</script>

<style scoped>
.entity-select {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  position: relative;
}

.input-wrapper {
  display: flex;
  gap: 0.5rem;
  align-items: stretch;
  position: relative;
}

input {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  font-size: 1rem;
  font-family: inherit;
}

input:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 3px rgba(var(--accent-rgb), 0.1);
}

.add-btn {
  padding: 0.75rem 1rem;
    background: #007aff;
    color: white;
    border: none;
    border-radius: 0.5rem;
    cursor: pointer;
    font-weight: 600;
    font-family: inherit;
    white-space: nowrap;
    box-shadow: 0 10px 22px rgba(0,122,255,.18);
  }

  .add-btn:hover {
    opacity: 0.95;
.suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  max-height: 200px;
  overflow-y: auto;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 10;
  margin-top: 0.25rem;
}

.no-results {
  padding: 1rem;
  text-align: center;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.suggestion-item {
  display: block;
  width: 100%;
  padding: 0.75rem 1rem;
  text-align: left;
  background: transparent;
  border: none;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  font-family: inherit;
}

.suggestion-item:last-child {
  border-bottom: none;
}

.suggestion-item:hover {
  background: var(--hover-bg);
}

.selected-items {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: var(--accent-color);
  color: white;
  border-radius: 0.25rem;
  font-size: 0.875rem;
}

.remove-btn {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 1.25rem;
  line-height: 1;
  padding: 0;
  display: flex;
  align-items: center;
}

.remove-btn:hover {
  opacity: 0.8;
}
</style>
