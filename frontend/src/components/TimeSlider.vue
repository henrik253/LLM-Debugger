<script setup lang="ts">
import { ref, defineEmits, defineProps, watch } from 'vue'

// Props
const props = defineProps<{
  min?: number
  max?: number
  step?: number
  modelValue?: number
}>()

// Emit event for v-model
const emit = defineEmits<{
  (e: 'update:modelValue', value: number): void
}>()

// Local state
const value = ref(props.modelValue ?? props.min ?? 0)

// Watch local value and emit changes
watch(value, (val) => {
  emit('update:modelValue', val)
})
</script>

<template>
  <div style="display: flex; flex-direction: column; gap: 0.25rem; width: 200px;">
    <input
      type="range"
      :min="props.min ?? 0"
      :max="props.max ?? 100"
      :step="props.step ?? 1"
      v-model="value"
    />
    <span>{{ value }}</span>
  </div>
</template>
