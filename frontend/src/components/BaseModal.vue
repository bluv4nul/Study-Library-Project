<template>
  <Teleport to="body">
    <div v-if="modelValue" class="modal-backdrop" @click.self="$emit('update:modelValue', false)">
      <section class="modal-card glass-panel">
        <header class="modal-header">
          <div>
            <p v-if="subtitle" class="eyebrow">{{ subtitle }}</p>
            <h2>{{ title }}</h2>
          </div>
          <button class="icon-button" type="button" @click="$emit('update:modelValue', false)">×</button>
        </header>
        <slot />
      </section>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  modelValue: Boolean,
  title: { type: String, required: true },
  subtitle: String,
});

defineEmits(['update:modelValue']);
</script>
