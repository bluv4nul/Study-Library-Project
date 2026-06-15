<template>
  <form class="publisher-form" @submit.prevent="submitForm">
    <label>
      <span>Название издательства *</span>
      <input v-model.trim="form.publisher_name" required placeholder="Например, Penguin Books" />
    </label>

    <label>
      <span>Город</span>
      <input v-model.trim="form.publisher_city" placeholder="Например, London" />
    </label>

    <label>
      <span>Email</span>
      <input v-model.trim="form.email" type="email" placeholder="contact@publisher.com" />
    </label>

    <label>
      <span>Веб-сайт</span>
      <input v-model.trim="form.publisher_website" placeholder="https://www.publisher.com" />
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
  publisher: { type: Object, default: null },
  submitText: { type: String, default: 'Сохранить' },
});

const emit = defineEmits(['submit', 'cancel']);

const form = reactive({
  publisher_name: '',
  publisher_city: '',
  email: '',
  publisher_website: '',
});

watch(
  () => props.publisher,
  (publisher) => {
    if (publisher) {
      form.publisher_name = publisher.publisher_name || '';
      form.publisher_city = publisher.publisher_city || '';
      form.email = publisher.email || '';
      form.publisher_website = publisher.publisher_website || '';
    } else {
      form.publisher_name = '';
      form.publisher_city = '';
      form.email = '';
      form.publisher_website = '';
    }
  },
  { immediate: true },
);

const submitForm = () => {
  emit('submit', {
    publisher_name: form.publisher_name,
    publisher_city: form.publisher_city || null,
    email: form.email || null,
    publisher_website: form.publisher_website || null,
  });
};
</script>

<style scoped>
.publisher-form {
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
