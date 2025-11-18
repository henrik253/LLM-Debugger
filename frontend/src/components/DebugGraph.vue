<script setup lang="ts">
import { ref, watch } from 'vue'
import { VueFlow } from '@vue-flow/core'

interface GraphNode {
  id: string
  data: { label: string }
  position: { x: number; y: number }
  parentNode?: string
  extent?: string
  style?: {
    backgroundColor?: string
    width?: string
    height?: string
  }
}

interface GraphEdge {
  id: string
  source: string
  target: string
}

interface GraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

function jsonToNestedGraph(
  data: Record<string, any>,
  parentId: string | null = null,
  depth = 0,
  relativeX = 0,
  relativeY = 0
): GraphData {
  const nodes: GraphNode[] = []
  const edges: GraphEdge[] = []

  // Spacing configuration
  const childXOffset = 20 // X offset for children inside parent
  const childYOffset = 60 // Y offset for first child
  const siblingYSpacing = 80 // Spacing between sibling nodes

  let currentY = relativeY

  Object.entries(data).forEach(([key, value]) => {
    const nodeId = parentId ? `${parentId}.${key}` : key
    const isObject = value && typeof value === 'object' && !Array.isArray(value)
    
    // Stop recursion if we find parameters.weight
    const shouldStopRecursion = 
      isObject &&
      value.parameters &&
      typeof value.parameters === 'object' &&
      value.parameters.weight !== undefined

    // Determine if this node should be a parent container
    const hasChildren = isObject && !shouldStopRecursion

    // Create the node
    const node: GraphNode = {
      id: nodeId,
      data: { 
        label: isObject && value.type ? value.type : key 
      },
      position: { x: relativeX, y: currentY },
    }

    // Set parent relationship if this is a child node
    if (parentId) {
      node.parentNode = parentId
      node.extent = 'parent'
    }
    var estimatedHeight = 0.0 
    var estimatedWidth = 0.0
    // Style parent nodes as containers
    if (hasChildren) {
      // Calculate approximate size based on children count
      const childCount = Object.keys(value).length
      estimatedHeight = Math.max(200, childCount * 100)
      estimatedWidth = depth === 0 ? 400 : 350
      
      node.style = {
        backgroundColor: `rgba(16, 185, 129, ${0.3 - depth * 0.05})`,
        width: `${estimatedWidth}px`,
        height: `${estimatedHeight}px`,
      }
    }

    nodes.push(node)

    // Create edge from parent to this node
    if (parentId) {
      edges.push({
        id: `e-${parentId}-${nodeId}`,
        source: parentId,
        target: nodeId,
      })
    }

    // Recursively process children
    if (hasChildren) {
      const childGraph = jsonToNestedGraph(
        value,
        nodeId,
        depth + 1,
        childXOffset, // Children start at offset X inside parent
        childYOffset  // Children start at offset Y inside parent
      )
      
      nodes.push(...childGraph.nodes)
      edges.push(...childGraph.edges)

      // Calculate height needed for this parent based on children
      const childrenHeight = childGraph.nodes
        .filter(n => n.parentNode === nodeId)
        .reduce((max, n) => Math.max(max, n.position.y), 0)
      
      currentY += Math.max(estimatedHeight, childrenHeight + 100)
    } else {
      // Leaf node - just add spacing for next sibling
      currentY += siblingYSpacing
    }
  })

  return { nodes, edges }
}



// Props: can pass nested JSON directly as graphJson
const props = defineProps<{
  graphJson?: Record<string, any>
  highlightStep?: number
}>()

const nodes = ref<GraphNode[]>([])
const edges = ref<GraphEdge[]>([])

// Watch the JSON and convert to graph
watch(
  () => props.graphJson,
  (json) => {
    if (!json) return
    console.log('ffffff',json.model.layers)
    const graph = jsonToNestedGraph(json.model.layers)
    nodes.value = graph.nodes.map((node) => ({
      ...node,
      style: { backgroundColor: props.highlightStep === node.step ? 'yellow' : 'lightblue' }
    }))
    edges.value = graph.edges
  },
  { immediate: true, deep: true }
)
</script>

<template>
  <vue-flow style="height: 500px; border: 1px solid #ccc;" :nodes="nodes" :edges="edges" />
</template>
