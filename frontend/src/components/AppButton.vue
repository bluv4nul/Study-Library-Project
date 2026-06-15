<template>
  <button class="app-button" :class="[`app-button--${variant}`]" :type="type">
    <slot />
  </button>
</template>

<script setup>
defineProps({
  variant: { type: String, default: 'primary' },
  type: { type: String, default: 'button' },
});
</script>
