<script setup lang="ts">
import { ref } from 'vue'

const prompt = ref('')
const emit = defineEmits<{
  (e: 'submitPrompt', prompt: string): void
}>()

function submit() {
  if (prompt.value.trim()) {
    emit('submitPrompt', prompt.value)
    prompt.value = ''
  }
}
</script>

<template>
  <form @submit.prevent="submit">
    <input
      type="text"
      v-model="prompt"
      placeholder="Type your prompt"
      style="width: 100%; padding: 0.5rem;"
    />
    <button type="submit" style="margin-top: 0.5rem;">Send</button>
  </form>
</template>
