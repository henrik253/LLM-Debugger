<script setup lang="ts">
const props = defineProps<{
  response: string
}>()
</script>

<template>
  <div class="response-box">
    <pre class="response-content">{{ response }}</pre>
  </div>
</template>

<style scoped>
.response-box {
  border: 1px solid #d0d0d0;
  padding: 1rem;
  border-radius: 8px;
  min-height: 120px;
  max-height: 300px;     /* 👈 makes it scroll */
  overflow-y: auto;      /* 👈 vertical scroll when needed */
  background: #fafafa;   /* light background */
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.response-content {
  white-space: pre-wrap; /* keep formatting but allow wrapping */
  word-break: break-word;
  font-family: "Fira Code", monospace;
  font-size: 0.9rem;
  line-height: 1.4;
  margin: 0;
}
</style>
