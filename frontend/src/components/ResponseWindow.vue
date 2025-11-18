<script setup lang="ts">
const props = defineProps<{
  response: string
}>()
</script>

<template>
  <div style="border:1px solid #ccc; padding:1rem; min-height:100px;">
    <pre>{{ response }}</pre>
  </div>
</template>
