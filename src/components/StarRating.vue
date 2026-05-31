<script setup lang="ts">
defineProps<{
  rating: number;
  max?: number;
  size?: 'sm' | 'md' | 'lg';
}>();

const sizeClass = {
  sm: 'text-sm',
  md: 'text-lg',
  lg: 'text-2xl',
};
</script>

<template>
  <span
    class="stars inline-flex gap-0.5"
    :class="sizeClass[size || 'md']"
    :aria-label="`${rating}/5 星`"
  >
    <span v-for="i in (max || 5)" :key="i" class="transition-transform hover:scale-125">
      {{ i <= rating ? '★' : i - rating <= 0.5 ? '⭑' : '☆' }}
    </span>
  </span>
</template>
