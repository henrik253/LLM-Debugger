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
  <form class="prompt-form" @submit.prevent="submit">
    <input
      class="prompt-input"
      type="text"
      v-model="prompt"
      placeholder="Type your prompt…"
    />
    <button class="send-btn" type="submit">Send</button>
  </form>
</template>

<style scoped>
.prompt-form {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  width: 100%;
  margin-top: 1rem;
}

.prompt-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid #d0d0d0;
  border-radius: 10px;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  background: #fafafa;
}

.prompt-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
  background: #ffffff;
}

.send-btn {
  padding: 0.65rem 1.2rem;
  border: none;
  border-radius: 10px;
  background: #3b82f6;
  color: white;
  font-size: 0.95rem;
  cursor: pointer;
  transition: background 0.2s ease, transform 0.1s ease;
}

.send-btn:hover {
  background: #2563eb;
}

.send-btn:active {
  transform: scale(0.96);
}
</style>
