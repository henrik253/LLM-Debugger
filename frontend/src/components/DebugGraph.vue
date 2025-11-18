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



interface TreeNode {
  id: string
  label: string
  children: TreeNode[]
  depth: number
}

const props = defineProps<{
  layers?: string[]
  highlightId?: string
}>()

const nodes = ref<GraphNode[]>([])

/* -------------------------------------------------------
   BUILD TREE STRUCTURE FROM PATHS
------------------------------------------------------- */
function buildTree(paths: string[]): TreeNode {
  const nodeMap = new Map<string, TreeNode>()
  
  // Create all nodes first
  for (const path of paths) {
    if (!path) continue
    
    const parts = path.split('.')
    
    for (let i = 0; i < parts.length; i++) {
      const currentPath = parts.slice(0, i + 1).join('.')
      
      if (!nodeMap.has(currentPath)) {
        nodeMap.set(currentPath, {
          id: currentPath,
          label: parts[i],
          children: [],
          depth: i
        })
      }
    }
  }
  
  // Build parent-child relationships
  const root: TreeNode = {
    id: '',
    label: 'root',
    children: [],
    depth: -1
  }
  
  for (const [path, node] of nodeMap) {
    const parts = path.split('.')
    
    if (parts.length === 1) {
      // Top level node
      root.children.push(node)
    } else {
      // Find parent
      const parentPath = parts.slice(0, -1).join('.')
      const parent = nodeMap.get(parentPath)
      if (parent) {
        parent.children.push(node)
      }
    }
  }
  
  return root
}

/* -------------------------------------------------------
   CALCULATE NESTED LAYOUT
------------------------------------------------------- */
interface LayoutResult {
  nodes: GraphNode[]
  width: number
  height: number
}

function calculateNestedLayout(
  node: TreeNode,
  parentId: string | undefined = undefined
): LayoutResult {
  const NODE_PADDING = 20
  const CHILD_SPACING = 15
  const MIN_NODE_WIDTH = 150
  const MIN_NODE_HEIGHT = 60
  
  const allNodes: GraphNode[] = []
  
  // Process children first to get their sizes
  const childResults: LayoutResult[] = []
  let currentX = NODE_PADDING + 10 // Small left padding
  
  for (const child of node.children) {
    const childResult = calculateNestedLayout(child, node.id === '' ? undefined : node.id)
    childResults.push(childResult)
    
    // Position child relative to parent (horizontally)
    childResult.nodes.forEach(n => {
      if (n.id === child.id) {
        n.position = { x: currentX, y: NODE_PADDING + 30 }
      }
    })
    
    allNodes.push(...childResult.nodes)
    
    currentX += childResult.width + CHILD_SPACING
  }
  
  // Calculate this node's size based on children
  let nodeWidth = MIN_NODE_WIDTH
  let nodeHeight = MIN_NODE_HEIGHT
  
  if (node.children.length > 0) {
    const maxChildHeight = Math.max(...childResults.map(r => r.height))
    nodeWidth = Math.max(nodeWidth, currentX + NODE_PADDING - CHILD_SPACING)
    nodeHeight = Math.max(nodeHeight, maxChildHeight + NODE_PADDING * 2 + 30)
  }
  
  // Create this node (skip root)
  if (node.id !== '') {
    const graphNode: GraphNode = {
      id: node.id,
      data: { label: node.label },
      position: { x: 0, y: 0 }, // Will be set by parent
      parentNode: parentId,
      extent: parentId ? 'parent' : undefined,
      style: {
        backgroundColor: 'rgba(217, 234, 255, 0.8)',
        border: '2px solid #4a90e2',
        width: `${nodeWidth}px`,
        height: `${nodeHeight}px`,
        borderRadius: '8px',
        padding: `${NODE_PADDING}px`,
        fontSize: '13px',
        fontWeight: '500'
      }
    }
    
    allNodes.push(graphNode)
  }
  
  return {
    nodes: allNodes,
    width: nodeWidth,
    height: nodeHeight
  }
}

/* -------------------------------------------------------
   ARRANGE TOP-LEVEL NODES HORIZONTALLY
------------------------------------------------------- */
function arrangeTopLevel(tree: TreeNode): { nodes: GraphNode[] } {
  const allNodes: GraphNode[] = []
  const TOP_LEVEL_SPACING = 50
  
  let currentY = 50
  
  for (const topNode of tree.children) {
    const result = calculateNestedLayout(topNode)
    
    // Position this top-level node (vertically stacked)
    result.nodes.forEach(n => {
      if (n.id === topNode.id) {
        n.position = { x: 50, y: currentY }
      }
    })
    
    allNodes.push(...result.nodes)
    
    currentY += result.height + TOP_LEVEL_SPACING
  }
  
  return { nodes: allNodes }
}

/* -------------------------------------------------------
   CONVERT PATHS TO NESTED GRAPH
------------------------------------------------------- */
function pathsToNestedGraph(paths: string[]): { nodes: GraphNode[] } {
  const tree = buildTree(paths)
  return arrangeTopLevel(tree)
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
  const layerList = props.layers || sampleLayers
  const graph = pathsToNestedGraph(layerList)
  
  return {
    nodes: graph.nodes.map((node) => ({
      ...node,
      style: {
        ...node.style,
        backgroundColor: node.id === props.highlightId 
          ? 'rgba(255, 226, 122, 0.9)' 
          : node.style?.backgroundColor,
        border: node.id === props.highlightId 
          ? '2px solid #f59e0b' 
          : node.style?.border
      }
    }))
  }
})

watch(
  () => graphData.value,
  (data) => {
    nodes.value = data.nodes
    console.log('Loaded nodes:', nodes.value.length)
  },
  { immediate: true }
)
</script>

<template>
  <div class="vue-flow-wrapper">
    <VueFlow
      :nodes="nodes"
      :fit-view-on-init="true"
      :min-zoom="0.05"
      :max-zoom="2"
      elevate-edges-on-select
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