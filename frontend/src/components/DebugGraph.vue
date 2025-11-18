<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { VueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'

// Import required CSS
import '@vue-flow/core/dist/style.css'
import '@vue-flow/controls/dist/style.css'
import '@vue-flow/minimap/dist/style.css'

/* -------------------------------------------------------
   TYPES
------------------------------------------------------- */
interface GraphNode {
  id: string
  data: { label: string }
  position: { x: number; y: number }
  parentNode?: string
  extent?: 'parent'
  style?: Record<string, any>
}

interface GraphEdge {
  id: string
  source: string
  target: string
}

interface TreeNode {
  id: string
  label: string
  children: Map<string, TreeNode>
  depth: number
}

const props = defineProps<{
  layers?: string[]
  highlightId?: string
}>()

const nodes = ref<GraphNode[]>([])
const edges = ref<GraphEdge[]>([])

/* -------------------------------------------------------
   BUILD TREE STRUCTURE FROM PATHS
------------------------------------------------------- */
function buildTree(paths: string[]): TreeNode {
  const root: TreeNode = {
    id: '',
    label: 'root',
    children: new Map(),
    depth: 0
  }

  for (const path of paths) {
    if (!path) continue
    
    const parts = path.split('.')
    let current = root

    for (let i = 0; i < parts.length; i++) {
      const part = parts[i]
      const pathSoFar = parts.slice(0, i + 1).join('.')

      if (!current.children.has(part)) {
        current.children.set(part, {
          id: pathSoFar,
          label: part,
          children: new Map(),
          depth: i + 1
        })
      }

      current = current.children.get(part)!
    }
  }

  return root
}

/* -------------------------------------------------------
   LAYOUT CALCULATION
------------------------------------------------------- */
function calculatePositions(node: TreeNode, xOffset = 0, yOffset = 0): { 
  nodes: GraphNode[]
  edges: GraphEdge[]
  width: number 
} {
  const allNodes: GraphNode[] = []
  const allEdges: GraphEdge[] = []

  const NODE_WIDTH = 180
  const NODE_HEIGHT = 50
  const X_SPACING = 100
  const Y_SPACING = 80

  // Skip the root node itself
  if (node.depth > 0) {
    const graphNode: GraphNode = {
      id: node.id,
      data: { label: node.label },
      position: { x: xOffset, y: yOffset },
      style: {
        backgroundColor: '#d9eaff',
        border: '2px solid #4a90e2',
        width: `${NODE_WIDTH}px`,
        height: `${NODE_HEIGHT}px`,
        borderRadius: '8px',
        padding: '8px',
        fontSize: '13px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontWeight: '500'
      }
    }
    allNodes.push(graphNode)
  }

  // Process children
  if (node.children.size > 0) {
    let currentX = xOffset
    const childY = yOffset + Y_SPACING

    const childArray = Array.from(node.children.values())

    for (const child of childArray) {
      const result = calculatePositions(child, currentX, childY)
      
      allNodes.push(...result.nodes)
      allEdges.push(...result.edges)

      // Create edge from parent to child
      if (node.depth > 0) {
        allEdges.push({
          id: `${node.id}-${child.id}`,
          source: node.id,
          target: child.id
        })
      }

      currentX += result.width + X_SPACING
    }
  }

  const totalWidth = node.children.size > 0 
    ? Array.from(node.children.values()).reduce((sum, child) => {
        const result = calculatePositions(child, 0, 0)
        return sum + result.width + X_SPACING
      }, 0) - X_SPACING
    : NODE_WIDTH

  return { nodes: allNodes, edges: allEdges, width: totalWidth }
}

/* -------------------------------------------------------
   CONVERT PATHS TO GRAPH
------------------------------------------------------- */
function pathsToGraph(paths: string[]): { nodes: GraphNode[], edges: GraphEdge[] } {
  const tree = buildTree(paths)
  const result = calculatePositions(tree)
  
  return {
    nodes: result.nodes,
    edges: result.edges
  }
}

// Sample data for testing
const sampleLayers = [
  "",
  "model",
  "model.embed_tokens",
  "model.layers",
  "model.layers.0",
  "model.layers.0.self_attn",
  "model.layers.0.self_attn.q_proj",
  "model.layers.0.self_attn.k_proj",
  "model.layers.0.mlp",
  "model.layers.0.mlp.gate_proj",
  "model.layers.1",
  "model.layers.1.self_attn",
  "model.layers.1.mlp"
]

const graphData = computed(() => {
   console.log('hgh',props.layers)
  const layerList = props.layers || sampleLayers
  const graph = pathsToGraph(layerList)
  
  return {
    nodes: graph.nodes.map((node) => ({
      ...node,
      style: {
        ...node.style,
        backgroundColor: node.id === props.highlightId ? '#ffe27a' : node.style?.backgroundColor,
        border: node.id === props.highlightId ? '2px solid #f59e0b' : node.style?.border
      }
    })),
    edges: graph.edges
  }
})

watch(
  () => graphData.value,
  (data) => {
    nodes.value = data.nodes
    edges.value = data.edges
    console.log('Loaded nodes:', nodes.value.length, 'edges:', edges.value.length)
  },
  { immediate: true }
)
</script>

<template>
  <div class="vue-flow-wrapper">
    <VueFlow
      :nodes="nodes"
      :edges="edges"
      :fit-view-on-init="true"
      :min-zoom="0.1"
      :max-zoom="4"
    >
      <MiniMap />
      <Controls />
      <Background pattern-color="#aaa" :gap="10" />
    </VueFlow>
  </div>
</template>

<style scoped>
.vue-flow-wrapper {
  width: 100%;
  height: 600px;
  border: 1px solid #ccc;
  background: #fafafa;
}
</style>