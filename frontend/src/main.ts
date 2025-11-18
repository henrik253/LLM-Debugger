// main.ts
import { createApp } from 'vue'
import App from './App.vue'
import { VueFlow } from '@vue-flow/core'   // <-- named import
import '@vue-flow/core/dist/style.css'

const app = createApp(App)
app.component('VueFlow', VueFlow)   // register globally if needed
app.mount('#app')



