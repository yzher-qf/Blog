<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  rating: number;  // 10 分制，显示时换算为 5 星
  max?: number;
  size?: 'sm' | 'md' | 'lg';
}>();

const displayRating = computed(() => props.rating / 2);

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
    :aria-label="`${rating}/10`"
  >
    <span v-for="i in (max || 5)" :key="i" class="relative inline-block transition-transform hover:scale-125">
      <!-- 空星底 -->
      <span class="text-warm-200">★</span>
      <!-- 实心覆盖 -->
      <span
        class="absolute inset-0 overflow-hidden text-yellow-500"
        :style="{
          width: i <= displayRating ? '100%' : i - displayRating < 1 ? `${(1 - (i - displayRating)) * 100}%` : '0%'
        }"
      >★</span>
    </span>
  </span>
</template>
