// main.ts
import { createApp } from 'vue'
import App from './App.vue'
import { VueFlow } from '@vue-flow/core'   // <-- named import
import '@vue-flow/core/dist/style.css'
import ECharts from 'vue-echarts'
import { use } from "echarts/core"

import {
  CanvasRenderer
} from 'echarts/renderers'

import {
  LineChart,
  BarChart,
  ScatterChart
} from 'echarts/charts'

import {
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent,
  DatasetComponent
} from 'echarts/components'

// Register required components
use([
  CanvasRenderer,
  LineChart,
  BarChart,
  ScatterChart,
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent,
  DatasetComponent
])



const app = createApp(App)

app.component('v-chart', ECharts)
app.component('VueFlow', VueFlow)   // register globally if needed
app.mount('#app')



