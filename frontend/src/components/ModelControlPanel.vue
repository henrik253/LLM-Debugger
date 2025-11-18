<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  model: string
  layers: string[]
}>()

const emit = defineEmits<{
  (e: 'hookLayer', layer: string): void
  (e: 'unhookLayer', layer: string): void
  (e: 'changeModel', model: string): void
}>()

const localModel = ref(props.model)

watch(() => props.model, (val) => (localModel.value = val))

function hook(layer: string) {
  emit('hookLayer', layer)
}

function unhook(layer: string) {
  emit('unhookLayer', layer)
}

function onModelChange() {
  emit('changeModel', localModel.value)
}
</script>

<template>
  <div>
    <h3>Model Control</h3>
    <label>Model:</label>
    <input type="text" v-model="localModel" @change="onModelChange" />

    <h4>Layers</h4>
    <ul>
      <li v-for="layer in layers" :key="layer">
        {{ layer }}
        <button @click="hook(layer)">Hook</button>
        <button @click="unhook(layer)">Unhook</button>
      </li>
    </ul>
  </div>
</template>
