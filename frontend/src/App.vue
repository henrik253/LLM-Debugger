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


const selectedNode = ref('')

function handleSelectedNode(text: string){
  selectedNode.value = text;
}

// Async fetch
async function loadModelGraph(modelName : string) {
  const load_resp = await client.loadModel(modelName);

  const layers = await client.getLayerNames(modelName)
  const architecture = await client.getModelArchitecture(modelName)

  
  graphJson.value = layers
  architectureJson.value = architecture
}


function changeModel(newModel: string) { 
  
  if(newModel == model.value)
    return 

  model.value = newModel 
  loadModelGraph(model.value)
}

// Call async function
loadModelGraph("Qwen/Qwen2.5-1.5B-Instruct")
</script>

<template>
  <div class="app-container">
    
    <!-- LEFT SIDE -->
    <div class="left-panel">

      <div class="debug-graph-wrapper">
        <DebugGraph 
          v-if="graphJson" 
          :layers="graphJson" 
          :highlightStep="currentTime"
          @node-selected="handleSelectedNode"
        />
      </div>

      <div class="response-window-wrapper">
        <ResponseWindow :response="response" />
      </div>

      <div class="prompt-wrapper">
        <PromptInput @submitPrompt="sendPrompt" />
      </div>

    </div>

    <!-- RIGHT SIDE -->
    <div class="right-panel">
      <ModelControlPanel
        :model="model"
        :layers="layers"
        :currentNode="selectedNode"
        :architecture="architectureJson"
        :model_output="response"
        @hookLayer="hookLayer"
        @unhookLayer="unhookLayer"
        @changeModel="changeModel"
      />
    </div>
  </div>
</template>

<style scoped>.app-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* LEFT PANEL */
.left-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* DebugGraph takes all remaining space */
.debug-graph-wrapper {
  flex: 1;
  min-height: 0;        /* 🟢 Critical: allows shrinking */
  overflow: auto;       /* 🟢 Makes DebugGraph scroll instead of pushing UI */
}

/* Response window scrolls inside but keeps a reasonable height */
.response-window-wrapper {
  max-height: 200px;
  overflow-y: auto;
  margin-top: 10px;
}

/* Prompt input stays at the bottom */
.prompt-wrapper {
  margin-top: 10px;
}

/* RIGHT PANEL */
.right-panel {
  width: 350px;
  border-left: 1px solid #ccc;
  padding: 10px;
  overflow-y: auto;
}

</style>
