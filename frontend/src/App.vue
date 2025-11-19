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
const architectureJson = ref<Record<string, any> | null>(null)
const response = ref<string>('')
const currentTime = ref<number>(0)
const model = ref<string>('Qwen/Qwen2.5-1.5B-Instruct')
const layers = ref<string[]>([])
const currentModel = ref<string>('')

const client = BackendClient.getInstance();


// Handlers
async function sendPrompt(prompt: string) { 
  const model_output = await client.generateOutput(model.value,prompt)
  response.value = model_output
}

function updateTime(time: number) { currentTime.value = time }
function hookLayer(layerName: string) { console.log('Hook layer:', layerName) }
function unhookLayer(layerName: string) { console.log('Unhook layer:', layerName) }
function changeModel(newModel: string) { model.value = newModel }

const selectedNode = ref('')

function handleSelectedNode(text: string){
  selectedNode.value = text;
}

// Async fetch
async function loadModelGraph(modelName : string) {
  const load_resp = await client.loadModel(modelName);

  const layers = await client.getLayerNames(modelName)
  const architecture = await client.getModelArchitecture(modelName)

  // Assign to reactive ref AFTER fetching
  graphJson.value = layers
  architectureJson.value = architecture
}

// Call async function
loadModelGraph("Qwen/Qwen2.5-1.5B-Instruct")
</script>

<template>
  <div class="app-container">
    <!-- Left panel -->
    <div class="left-panel">
      <TimeSlider :currentTime="currentTime" @updateTime="updateTime" />
      <!-- Only render DebugGraph when graphJson is ready -->
      <DebugGraph @node-selected="handleSelectedNode" v-if="graphJson" :layers="graphJson" :highlightStep="currentTime" />
      <ResponseWindow :response="response" />
      <PromptInput @submitPrompt="sendPrompt" />
    </div>

    <!-- Right panel -->
    <div class="right-panel">
      <ModelControlPanel
        :model="model"
        :layers="layers"
        :currentNode="selectedNode"
        :architecture="architectureJson"
        @hookLayer="hookLayer"
        @unhookLayer="unhookLayer"
        @changeModel="changeModel"
       
      />
    </div>
  </div>
</template>
<style scoped>
.app-container {
  display: flex;
  flex-direction: row;
  height: 100vh;            /* full height layout */
  width: 100%;
  overflow: hidden;
}

/* Left side takes remaining space */
.left-panel {
  flex: 1;                  /* <-- THIS prevents DebugGraph from taking all space */
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Right side has fixed width */
.right-panel {
  width: 350px;             /* adjust as needed */
  border-left: 1px solid #ccc;
  padding: 10px;
  box-sizing: border-box;
  overflow-y: auto;
}

/* Optional: give DebugGraph some constraints */
.left-panel > * {
  flex-shrink: 0;
}

/* If DebugGraph needs to grow instead of pushing others */
DebugGraph {
  flex: 1;
  min-height: 0;            /* critical for flex layouts */
}
</style>
