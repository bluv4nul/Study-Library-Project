<template>
  <form class="author-form" @submit.prevent="submitForm">
    <label>
      <span>Имя автора *</span>
      <input v-model.trim="form.author_name" required placeholder="Например, George Orwell" />
    </label>

    <label>
      <span>Никнейм</span>
      <input v-model.trim="form.author_nickname" placeholder="Например, Orwell" />
    </label>

    <label>
      <span>Email</span>
      <input v-model.trim="form.email" type="email" placeholder="author@mail.com" />
    </label>

    <label>
      <span>Социальные сети</span>
      <input v-model.trim="form.social_media_link" placeholder="https://twitter.com/..." />
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
  author: { type: Object, default: null },
  submitText: { type: String, default: 'Сохранить' },
});

const emit = defineEmits(['submit', 'cancel']);

const form = reactive({
  author_name: '',
  author_nickname: '',
  email: '',
  social_media_link: '',
});

watch(
  () => props.author,
  (author) => {
    if (author) {
      form.author_name = author.author_name || '';
      form.author_nickname = author.author_nickname || '';
      form.email = author.email || '';
      form.social_media_link = author.social_media_link || '';
    } else {
      form.author_name = '';
      form.author_nickname = '';
      form.email = '';
      form.social_media_link = '';
    }
  },
  { immediate: true },
);

const submitForm = () => {
  emit('submit', {
    author_name: form.author_name,
    author_nickname: form.author_nickname || null,
    email: form.email || null,
    social_media_link: form.social_media_link || null,
  });
};
</script>

<style scoped>
.author-form {
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
