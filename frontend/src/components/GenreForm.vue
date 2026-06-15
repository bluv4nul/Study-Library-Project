<template>
  <form class="genre-form" @submit.prevent="submitForm">
    <label>
      <span>Название жанра *</span>
      <input v-model.trim="form.genre_name" required placeholder="Например, Фантастика" />
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

const props = defineProps({
  genre: { type: Object, default: null },
  submitText: { type: String, default: 'Сохранить' },
});

const emit = defineEmits(['submit', 'cancel']);

const form = reactive({
  genre_name: '',
});

watch(
  () => props.genre,
  (genre) => {
    form.genre_name = genre?.genre_name || '';
  },
  { immediate: true },
);

const submitForm = () => {
  emit('submit', {
    genre_name: form.genre_name,
  });
};
</script>

<style scoped>
.genre-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

label {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

span {
  font-weight: 600;
  color: var(--text-primary);
}

input {
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

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1rem;
}
</style>
