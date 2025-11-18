<script setup lang="ts">
import { ref } from 'vue'
import DebugGraph from './components/DebugGraph.vue'
import TimeSlider from './components/TimeSlider.vue'
import ResponseWindow from './components/ResponseWindow.vue'
import PromptInput from './components/PromptInput.vue'
import ModelControlPanel from './components/ModelControlPanel.vue'
import { BackendClient } from './backend_client'

// Reactive state
const graphJson = ref<Record<string, any> | null>(null)
const response = ref<string>('')
const currentTime = ref<number>(0)
const model = ref<string>('default-model')
const layers = ref<string[]>([])

const client = new BackendClient("https://bistered-gaylord-contorted.ngrok-free.dev");

// Handlers
function sendPrompt(prompt: string) { console.log('Send prompt:', prompt) }
function updateTime(time: number) { currentTime.value = time }
function hookLayer(layerName: string) { console.log('Hook layer:', layerName) }
function unhookLayer(layerName: string) { console.log('Unhook layer:', layerName) }
function changeModel(newModel: string) { model.value = newModel }

// Async fetch
async function loadModelGraph() {
  const load_resp = await client.loadModel("Qwen/Qwen2.5-1.5B-Instruct");
  console.log(load_resp)

  const architecture = await client.getModelArchitecture("Qwen/Qwen2.5-1.5B-Instruct")
  console.log("Architecture layers:", architecture.layers)

  // Assign to reactive ref AFTER fetching
  graphJson.value = architecture.layers
}

// Call async function
loadModelGraph()
</script>

<template>
  <div class="app-container">
    <!-- Left panel -->
    <div class="left-panel">
      <TimeSlider :currentTime="currentTime" @updateTime="updateTime" />
      <!-- Only render DebugGraph when graphJson is ready -->
      <DebugGraph v-if="graphJson" :graphJson="graphJson" :highlightStep="currentTime" />
      <ResponseWindow :response="response" />
      <PromptInput @submitPrompt="sendPrompt" />
    </div>

    <!-- Right panel -->
    <div class="right-panel">
      <ModelControlPanel
        :model="model"
        :layers="layers"
        @hookLayer="hookLayer"
        @unhookLayer="unhookLayer"
        @changeModel="changeModel"
      />
    </div>
  </div>
</template>
