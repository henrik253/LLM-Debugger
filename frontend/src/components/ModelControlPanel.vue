<script setup lang="ts">
import { ref, watch } from 'vue'
import { BackendClient } from '@/backend_client';
const props = defineProps<{
  model: string
  layers: string[]
  currentNode: string
  architecture: Record<string, any>
}>()

const client = BackendClient.getInstance()

const emit = defineEmits<{
  (e: 'hookLayer', layer: string): void
  (e: 'unhookLayer', layer: string): void
  (e: 'changeModel', model: string): void
}>()

const localModel = ref(props.model)
const showModelDropdown = ref(false)

// Example model names
const exampleModels = [
  'Qwen/Qwen2.5-1.5B-Instruct',
  'meta-llama/Llama-3.2-1B',
  'google/gemma-2-2b',
  'microsoft/phi-2',
  'mistralai/Mistral-7B-v0.1'
]

// Keep local model synced
watch(() => props.model, (val) => (localModel.value = val))

// Call a function when currentNode changes
watch(
  () => props.currentNode,
  (newVal, oldVal) => {
    console.log("currentNode changed:", oldVal, "→", newVal)
    handleCurrentNodeChange(newVal)
  }
)

async function handle_layer(layer : any,node : string){
  
  
  if(layer.parameters.bias){
    console.log(layer.parameters.bias)
  }

  if(layer.parameters.weight){
    console.log(layer.parameters.weight)
    // display layer.parameters.weight.num_params
    // display layer.parameters.weight.shape is a array with all the dimension 
    
  }

  const biases = await client.getLayerBiases(props.model,node)
  console.log(biases)
  const avg_weights = await client.getLayerInputAvgs(props.model,layer)
  console.log(avg_weights)
  const std_weights = await client.getLayerInputStds(props.model,layer)
  console.log(std_weights)
  const activations = await client.getLayerActivations(props.model,layer)
  console.log(activations)


}

// Function that runs whenever currentNode changes
function handleCurrentNodeChange(node: string) {
  console.log("Handling new currentNode:", node)
  //console.log(props.architecture)
  const path = props.currentNode.split('.') 
  console.log(path)
  let currentLayer = props.architecture.layers

  for(const key of path){
    currentLayer = currentLayer[key]
  }
  handle_layer(currentLayer,node)
}

function selectModel(model: string) {
  localModel.value = model
  emit('changeModel', model)
  showModelDropdown.value = false
}
</script>

<template>
  <div class="control-panel">
    <!-- Model Name Heading -->
    <div class="model-heading">
      <h2>{{ model }}</h2>
    </div>

    <!-- Model Selection Input -->
    <div class="model-selector">
      <label>Select Model:</label>
      <div class="dropdown-container">
          <input 
          type="text" 
          :value="localModel" 
          @focus="showModelDropdown = true"
          @blur="() => setTimeout(() => showModelDropdown = false, 200)"
          placeholder="Click to select a model"
          readonly
        />
        <div v-if="showModelDropdown" class="dropdown-menu">
          <div 
            v-for="modelName in exampleModels" 
            :key="modelName"
            class="dropdown-item"
            @click="selectModel(modelName)"
          >
            {{ modelName }}
          </div>
        </div>
        <!-- Add model params here under architectureJson.total_params-->
      </div>
    </div>

    <!-- Current Node Heading -->
    <div class="current-node">
      <h3>Current Node:</h3>
      <p class="node-name">{{ currentNode || 'None selected' }}</p>
    </div>

    <!-- Rest of your control panel content -->
  </div>
</template>

<style scoped>
.control-panel {
  padding: 16px;
}

.model-heading {
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid #e0e0e0;
}

.model-heading h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.model-selector {
  margin-bottom: 24px;
}

.model-selector label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
}

.dropdown-container {
  position: relative;
}

.dropdown-container input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  background-color: white;
  box-sizing: border-box;
}

.dropdown-container input:focus {
  outline: none;
  border-color: #4a90e2;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 4px;
  background: white;
  border: 1px solid #ccc;
  border-radius: 6px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
}

.dropdown-item {
  padding: 10px 12px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.dropdown-item:hover {
  background-color: #f5f5f5;
}

.current-node {
  margin-bottom: 24px;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.current-node h3 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.node-name {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #333;
  font-family: monospace;
}
</style>