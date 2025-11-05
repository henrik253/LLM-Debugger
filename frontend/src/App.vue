<script setup>
import { ref, onMounted } from 'vue'

// Reactive variable to display backend message
const message = ref('Connecting to backend...')

// Replace this with your actual ngrok URL
const BACKEND_URL = 'https://bistered-gaylord-contorted.ngrok-free.dev/api'

onMounted(() => {
  let appendix = {headers:{
      "ngrok-skip-browser-warning": "69420",
    }
  }; 
  
  fetch(BACKEND_URL,appendix)
    .then(async res => {
      if (!res.ok) {
        throw new Error(`HTTP error! Status: ${res.status}`)
      }

      // Check that the response is actually JSON
      const contentType = res.headers.get("content-type")
      console.log(res)
      if (!contentType || !contentType.includes("application/json")) {
        throw new Error("c")
      }

      const data = await res.json()
      message.value = data.message
    })
    .catch(err => {
      // Show friendly message in the UI
      message.value = 'Connection failed 😢'
      // Log the full error for debugging
      console.error('Error connecting to backend:', err)
    })
})
</script>

<template>
  <div style="padding: 2rem; font-family: sans-serif;">
    <h1>FastAPI + Vue Connection Test</h1>
    <p>{{ message }}</p>
    <p><small>Check the console for detailed errors if connection fails.</small></p>
  </div>
</template>
