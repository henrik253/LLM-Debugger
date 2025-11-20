<script setup lang="ts">
import { ref, watch } from 'vue'
import { BackendClient } from '@/backend_client';

const props = defineProps<{
  model: string
  layers: string[]
  currentNode: string
  architecture: Record<string, any>,
  model_output: string, 
  modelOutputTokens: string, 
}>()

const client = BackendClient.getInstance()

const emit = defineEmits<{
  (e: 'hookLayer', layer: string): void
  (e: 'unhookLayer', layer: string): void
  (e: 'changeModel', model: string): void
}>()

const localModel = ref(props.model)
const showModelDropdown = ref(false)

// Timestep slider state
const timestepValue = ref(0)
const timestepMax = ref(100) // You can adjust this based on your needs


const maxNewTokensValue = ref<number | null>(null)

async function handleSetMaxNewTokens() {
  if (maxNewTokensValue.value === null || isNaN(maxNewTokensValue.value)) {
    alert("Please enter a valid number")
    return
  }

  try {
    await client.setMaxNewTokens(props.model, maxNewTokensValue.value)
  } catch (err) {
    console.error("Error setting max new tokens:", err)
    alert("Failed to set max new tokens")
  }
}

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

// Layer data storage
const layerData = ref<{
  biases: number[] | null
  avg_weights: number[] | null
  std_weights: number[] | null
  activations: number[] | null
  layerInfo: any
}>({
  biases: null,
  avg_weights: null,
  std_weights: null,
  activations: null,
  layerInfo: null
})

const currentLayerId = ref<string>('')
const neuronIndex = ref<number>(0)
const biasValue = ref<number>(0)

// Chart options
const biasesOption = ref<any>(null)
const avgWeightsOption = ref<any>(null)
const stdWeightsOption = ref<any>(null)
const activationsOption = ref<any>(null)

async function handleTimestepChange() {
  try {
    await client.setTimestep(props.model, timestepValue.value)
    console.log("Sent timestep update:", timestepValue.value)

    // reload layer data if a layer is selected
    if (currentLayerId.value && layerData.value.layerInfo) {
      await handle_layer(layerData.value.layerInfo, currentLayerId.value)
    }
  } catch (err) {
    console.error("Error setting timestep:", err)
  }
  handle_layer(currentLayerInformation,currentLayer)
}

// Watch for data changes and update chart options
watch(() => layerData.value.biases, (data) => {
  if (data && data.length > 0) {
    biasesOption.value = {
      title: { text: 'Layer Biases', textStyle: { fontSize: 14 } },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: data.map((_, i) => i) },
      yAxis: { type: 'value' },
      series: [{ type: 'line', data, showSymbol: false, sampling: 'lttb' }]
    }
  } else {
    biasesOption.value = null
  }
})

watch(() => layerData.value.avg_weights, (data) => {
  if (data && data.length > 0) {
    avgWeightsOption.value = {
      title: { text: 'Average Weights', textStyle: { fontSize: 14 } },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: data.map((_, i) => i) },
      yAxis: { type: 'value' },
      series: [{ type: 'line', data, showSymbol: false, sampling: 'lttb' }]
    }
  } else {
    avgWeightsOption.value = null
  }
})

watch(() => layerData.value.std_weights, (data) => {
  if (data && data.length > 0) {
    stdWeightsOption.value = {
      title: { text: 'Standard Deviation Weights', textStyle: { fontSize: 14 } },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: data.map((_, i) => i) },
      yAxis: { type: 'value' },
      series: [{ type: 'line', data, showSymbol: false, sampling: 'lttb' }]
    }
  } else {
    stdWeightsOption.value = null
  }
})

watch(
  () => props.model_output,
  (newVal, oldVal) => {
    console.log("model_output changed:", oldVal, "→", newVal)
    console.log(newVal.length)
    onModelOutputChanged(newVal)
  }
)

function onModelOutputChanged(output: string) {
  timestepMax.value = output.split(' ').length
}

watch(() => layerData.value.activations, (data) => {
  if (data && data.length > 0) {
    // Handle deeply nested array structure - unwrap extra levels
    let unwrappedData = data;
    while (Array.isArray(unwrappedData) && unwrappedData.length === 1 && Array.isArray(unwrappedData[0])) {


      unwrappedData = unwrappedData[0];
    }


    if(timestepValue.value > 1){
      unwrappedData = unwrappedData[timestepValue.value]
    }

    if (unwrappedData && unwrappedData.length > 0) {
      activationsOption.value = {
        title: { text: 'Layer Activations', textStyle: { fontSize: 14 } },
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: unwrappedData.map((_, i) => i) },
        yAxis: { type: 'value' },
        series: [{ type: 'line', data: unwrappedData, showSymbol: false, sampling: 'lttb' }]
      }
    } else {
      activationsOption.value = null
    }
  } else {
    activationsOption.value = null
  }
})

// Call a function when currentNode changes
watch(
  () => props.currentNode,
  (newVal, oldVal) => {
    console.log("currentNode changed:", oldVal, "→", newVal)
    handleCurrentNodeChange(newVal)
  }
)

async function handle_layer(layer_information: any, layer_id: string) {
  currentLayerId.value = layer_id
  layerData.value.layerInfo = layer_information
  
  if (layer_information.parameters?.bias) {
    console.log(layer_information.parameters.bias)
  }

  if (layer_information.parameters?.weight) {
    console.log(layer_information.parameters.weight)
  }

  // Biases
  try {
    const biases = await client.getLayerBiases(props.model, layer_id)
    console.log('biases', biases)
    layerData.value.biases = Array.isArray(biases)
      ? biases
      : (biases?.biases || null)
  } catch (err) {
    console.error('biases error', err)
    layerData.value.biases = null
  }

  // Avg weights
  try {
    const avg_weights = await client.getLayerInputAvgs(props.model, layer_id)
    console.log('avg_weights', avg_weights)
    layerData.value.avg_weights = Array.isArray(avg_weights)
      ? avg_weights
      : (avg_weights?.input_avgs || null)
  } catch (err) {
    console.error('avg_weights error', err)
    layerData.value.avg_weights = null
  }

  // Std weights
  try {
    const std_weights = await client.getLayerInputStds(props.model, layer_id)
    console.log('weights', std_weights)
    layerData.value.std_weights = Array.isArray(std_weights)
      ? std_weights
      : (std_weights?.input_stds || null)
  } catch (err) {
    console.error('std_weights error', err)
    layerData.value.std_weights = null
  }

  // Activations
  try {
    const activations = await client.getLayerActivations(props.model, layer_id)
    console.log('activations', activations)
    layerData.value.activations = Array.isArray(activations)
      ? activations
      : (activations?.activations || null)
  } catch (err) {
    console.error('activations error', err)
    layerData.value.activations = null
  }
}

let currentLayerInformation = ''
let currentLayer = ''


// Function that runs whenever currentNode changes
function handleCurrentNodeChange(node: string) {
  console.log("Handling new currentNode:", node)
  
  if (!node) return
  
  const path = props.currentNode.split('.') 
  console.log(path)
  let currentLayer = props.architecture.layers

  for (const key of path) {
    currentLayer = currentLayer[key]
  }
  currentLayer = currentLayer
  currentLayerInformation = node 
  handle_layer(currentLayer, node)
}

function selectModel(model: string) {
  localModel.value = model
  emit('changeModel', model)
  showModelDropdown.value = false
}

async function handleSetNeuronBias() {
  if (!currentLayerId.value) {
    alert('No layer selected')
    return
  }
  
  try {
    await client.setNeuronBias(props.model, currentLayerId.value, neuronIndex.value, biasValue.value)
    alert(`Neuron bias set successfully for neuron ${neuronIndex.value}`)
    // Refresh the data
    await handle_layer(layerData.value.layerInfo, currentLayerId.value)
  } catch (error) {
    console.error('Error setting neuron bias:', error)
    alert('Failed to set neuron bias')
  }
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
      </div>
    </div>

    <!-- Timestep Slider Section -->
    <div class="timestep-section">
      <label>Timestep:</label>
      <div class="slider-container">
        <input
          type="range"
          :min="0"
          :max="timestepMax"
          :step="1"
          v-model.number="timestepValue"
          @change="handleTimestepChange"
          class="timestep-slider"
        />
        <span class="timestep-value">{{ timestepValue }}</span>
      </div>
      <label>Max New Tokens:</label>
  <div class="input-group">
    <input
      type="number"
      v-model.number="maxNewTokensValue"
      min="1"
      placeholder="Enter max new tokens"
      style="flex: 1; padding: 8px; border-radius: 6px; border: 1px solid #ccc;"
    />
    <button 
      @click="handleSetMaxNewTokens"
      style="
        padding: 8px 12px;
        background-color: #4a90e2;
        color: white;
        border: none;
        border-radius: 6px;
        cursor: pointer;
      "
    >
      Set
    </button>
  </div>
    </div>

    <!-- Current Node Heading -->
    <div class="current-node">
      <h3>Current Node:</h3>
      <p class="node-name">{{ currentNode || 'None selected' }}</p>
    </div>

    <!-- Set Neuron Bias Section -->
    <div v-if="currentLayerId" class="neuron-bias-section">
      <h3>Set Neuron Bias</h3>
      <div class="input-group">
        <div class="input-field">
          <label>Neuron Index:</label>
          <input type="number" v-model.number="neuronIndex" min="0" />
        </div>
        <div class="input-field">
          <label>Bias Value:</label>
          <input type="number" v-model.number="biasValue" step="0.01" />
        </div>
      </div>
      <button @click="handleSetNeuronBias" class="set-bias-btn">Set Bias</button>
    </div>

    <!-- Charts Section -->
    <div class="charts-section">
      <v-chart 
        v-if="biasesOption" 
        :option="biasesOption" 
        style="height: 300px; width: 100%; margin-bottom: 20px;" 
      />
      <v-chart 
        v-if="avgWeightsOption" 
        :option="avgWeightsOption" 
        style="height: 300px; width: 100%; margin-bottom: 20px;" 
      />
      <v-chart 
        v-if="stdWeightsOption" 
        :option="stdWeightsOption" 
        style="height: 300px; width: 100%; margin-bottom: 20px;" 
      />
      <v-chart 
        v-if="activationsOption" 
        :option="activationsOption" 
        style="height: 300px; width: 100%; margin-bottom: 5px;" 
      />
    </div>
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

.timestep-section {
  margin-bottom: 24px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.timestep-section label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.slider-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.timestep-slider {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: #ddd;
  outline: none;
  -webkit-appearance: none;
}

.timestep-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #4a90e2;
  cursor: pointer;
  transition: background-color 0.2s;
}

.timestep-slider::-webkit-slider-thumb:hover {
  background: #357abd;
}

.timestep-slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #4a90e2;
  cursor: pointer;
  border: none;
  transition: background-color 0.2s;
}

.timestep-slider::-moz-range-thumb:hover {
  background: #357abd;
}

.timestep-value {
  min-width: 40px;
  text-align: center;
  font-size: 16px;
  font-weight: 600;
  color: #333;
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

.neuron-bias-section {
  margin-bottom: 24px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.neuron-bias-section h3 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.input-group {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.input-field {
  flex: 1;
}

.input-field label {
  display: block;
  margin-bottom: 4px;
  font-size: 12px;
  font-weight: 500;
  color: #555;
}

.input-field input {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.input-field input:focus {
  outline: none;
  border-color: #4a90e2;
}

.set-bias-btn {
  width: 100%;
  padding: 10px;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.set-bias-btn:hover {
  background-color: #357abd;
}

.set-bias-btn:active {
  background-color: #2a5d8f;
}

.charts-section {
  margin-top: 24px;
}
</style>