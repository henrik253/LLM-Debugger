<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { VueFlow, useVueFlow, Handle, Position } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'

// Import required CSS
import '@vue-flow/core/dist/style.css'
import '@vue-flow/controls/dist/style.css'
import '@vue-flow/minimap/dist/style.css'
import type Graph from 'echarts/types/src/data/Graph.js'
import type Tree from 'echarts/types/src/data/Tree.js'





/* -------------------------------------------------------
   TYPES
------------------------------------------------------- */
interface GraphNode {
  id: string
  data: { label: string; hasChildren?: boolean; depth?: number }
  position: { x: number; y: number }
  parentNode?: string
  extent?: 'parent'
  style?: Record<string, any>
  hidden?: boolean
  zIndex?: number
  sourcePosition: string,
  targetPosition: string,
}

interface GraphEdge{
  id: string,
  source: string,
  target: string,
  type: string,
  sourcePosition: string, 
  targetPosition: string
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

const emit = defineEmits<{
  'node-selected': [path: string]
}>()

const nodes = ref<GraphNode[]>([])
const edges = ref<GraphEdge[]>([])

const expandedNodes = ref<Set<string>>(new Set())

const { fitView } = useVueFlow()

// Color palette for different depths
const DEPTH_COLORS = [
  'rgba(59, 130, 246, 0.15)',   // blue
  'rgba(139, 92, 246, 0.15)',   // purple
  'rgba(236, 72, 153, 0.15)',   // pink
  'rgba(249, 115, 22, 0.15)',   // orange
  'rgba(34, 197, 94, 0.15)',    // green
  'rgba(20, 184, 166, 0.15)',   // teal
]

const DEPTH_BORDERS = [
  '2px solid rgb(59, 130, 246)',
  '2px solid rgb(139, 92, 246)',
  '2px solid rgb(236, 72, 153)',
  '2px solid rgb(249, 115, 22)',
  '2px solid rgb(34, 197, 94)',
  '2px solid rgb(20, 184, 166)',
]

/* -------------------------------------------------------
   BUILD TREE STRUCTURE FROM PATHS
------------------------------------------------------- */
function buildTree(paths: string[]): TreeNode {
  const nodeMap = new Map<string, TreeNode>()
  
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
  
  const root: TreeNode = {
    id: '',
    label: 'root',
    children: [],
    depth: -1
  }
  
  for (const [path, node] of nodeMap) {
    const parts = path.split('.')
    
    if (parts.length === 1) {
      root.children.push(node)
    } else {
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
  parentId: string | undefined = undefined,
  ancestorsExpanded: boolean = true
): LayoutResult {
  const NODE_PADDING = 30 // Increased padding
  const CHILD_SPACING = 20
  const MIN_NODE_WIDTH = 180
  const MIN_NODE_HEIGHT = 70
  const COLLAPSED_HEIGHT = 70
  const HEADER_HEIGHT = 50 // Slightly larger header
  const TOP_MARGIN = 10 // Margin between header and children
  const BOTTOM_MARGIN = 10 // Margin for bottom border visibility
  
  const allNodes: GraphNode[] = []
  const hasChildren = node.children.length > 0
  const isExpanded = expandedNodes.value.has(node.id)
  const shouldShowChildren = ancestorsExpanded && isExpanded
  
  // Process children first to get their sizes
  const childResults: LayoutResult[] = []
  let currentX = NODE_PADDING
  
  for (const child of node.children) {
    const childResult = calculateNestedLayout(
      child, 
      node.id === '' ? undefined : node.id,
      shouldShowChildren
    )
    childResults.push(childResult)
    
    if (shouldShowChildren) {
      // Position child relative to parent (horizontally)
      childResult.nodes.forEach(n => {
        if (n.id === child.id) {
          n.position = { x: currentX, y: HEADER_HEIGHT + TOP_MARGIN }
          n.hidden = false
        }
      })
      
      currentX += childResult.width + CHILD_SPACING
    } else {
      // Mark all descendants as hidden - also remove their backgrounds
      childResult.nodes.forEach(n => {
        n.hidden = true
        if (n.style) {
          n.style.opacity = '0'
          n.style.pointerEvents = 'none'
        }
      })
    }
    
    allNodes.push(...childResult.nodes)
  }
  
  // Calculate this node's size based on children
  let nodeWidth = MIN_NODE_WIDTH
  let nodeHeight = shouldShowChildren ? MIN_NODE_HEIGHT : COLLAPSED_HEIGHT
  
  if (node.children.length > 0 && shouldShowChildren) {
    const maxChildHeight = Math.max(...childResults.map(r => r.height))
    nodeWidth = Math.max(nodeWidth, currentX + NODE_PADDING - CHILD_SPACING)
    nodeHeight = Math.max(nodeHeight, maxChildHeight + HEADER_HEIGHT + TOP_MARGIN + BOTTOM_MARGIN)
  }
  
  // Create this node (skip root)
  if (node.id !== '') {
    const depth = node.depth
    const colorIndex = depth % DEPTH_COLORS.length
    
    const graphNode: GraphNode = {
      id: node.id,
      data: { 
        label: node.label,
        hasChildren,
        depth
      },
      position: { x: 0, y: 0 },
      parentNode: parentId,
      extent: parentId ? 'parent' : undefined,
      hidden: !ancestorsExpanded && parentId !== undefined,
      sourcePosition: 'left',
      targetPosition: 'right',
      zIndex: hasChildren ? 10 : 1,
      style: {
        backgroundColor: shouldShowChildren && hasChildren 
          ? DEPTH_COLORS[colorIndex]
          : 'rgba(248, 250, 252, 0.95)',
        border: DEPTH_BORDERS[colorIndex],
        width: `${nodeWidth}px`,
        height: `${nodeHeight}px`,
        borderRadius: '10px',
        padding: '0',
        paddingBottom: shouldShowChildren && hasChildren ? '10px' : '0',
        fontSize: '14px',
        fontWeight: '500',
        cursor: hasChildren ? 'pointer' : 'default',
        transition: 'all 0.3s ease',
        overflow: 'visible',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
        backgroundClip: 'padding-box',
        boxSizing: 'border-box',
        opacity: (!ancestorsExpanded && parentId !== undefined) ? '0' : '1',
        pointerEvents: (!ancestorsExpanded && parentId !== undefined) ? 'none' : 'auto'
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
   ARRANGE TOP-LEVEL NODES VERTICALLY
------------------------------------------------------- */
function arrangeTopLevel(tree: TreeNode): { nodes: GraphNode[] } {
  const allNodes: GraphNode[] = []
  const TOP_LEVEL_SPACING = 60
  
  let currentY = 50
  
  for (const topNode of tree.children) {
    const result = calculateNestedLayout(topNode)
    
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

function arrangeEdges(root : Map<string, TreeNode>,edges : GraphEdge[]){

  if(root.children.length === undefined || root.children.length == 0)
    return null  

  let currentNode = root.id


  let lastNode = currentNode.id
  let firstNode = true 
  for( const child of root.children){
    const edge : GraphEdge = {
        id: currentNode + ' ' + child.id,
        source: currentNode,
        target: child.id,
        type: 'default',
        sourcePosition: firstNode ? 'left' : 'right', 
        targetPosition: firstNode? 'right' : 'left', 
    }
    edges.push(edge)
    firstNode = false
    lastNode = currentNode 
    currentNode = child.id
    arrangeEdges(child,edges)
  }
  
  const edge : GraphEdge = {
      id: currentNode + ' ' + lastNode,
      source: currentNode,
      target: lastNode,
      type: 'default',
      sourcePosition: 'left', 
        targetPosition: 'right', 
    }
    edges.push(edge)
}

function edgesForNestedGraph(paths: string[]): {edges : GraphEdge[]}{
  const tree = buildTree(paths)
  const edges : GraphEdge[] = []
  for(const child of tree.children)
    arrangeEdges(child,edges)
  

  return {edges : edges} 
}

const graphData = computed(() => {
  const layerList = props.layers
  const graph = pathsToNestedGraph(layerList)
  //const edgesData = edgesForNestedGraph(layerList)

  return {
   // edges : edgesData.edges,
    nodes: graph.nodes.map((node) => ({
      ...node,
      style: {
        ...node.style,
        backgroundColor: node.id === props.highlightId 
          ? 'rgba(255, 226, 122, 0.95)' 
          : node.style?.backgroundColor,
        border: node.id === props.highlightId 
          ? '3px solid #f59e0b' 
          : node.style?.border
      }
    }))
  }
})

watch(
  () => graphData.value,
  (data) => {
    nodes.value = data.nodes
    edges.value = data.edges
  },
  { immediate: true }
)

function onNodeClick(event: any) {
  const node = event.node
  
  // If it's a leaf node (no children), emit the path and log it
  if (!node.data.hasChildren) {
    const path = node.id
    emit('node-selected', path)
    return
  }
  
  // Otherwise, toggle expand/collapse for parent nodes
  if (node.data.hasChildren) {
    if (expandedNodes.value.has(node.id)) {
      expandedNodes.value.delete(node.id)
    } else {
      expandedNodes.value.add(node.id)
    }
    
    // Trigger re-layout
    const layerList = props.layers || sampleLayers
    const graph = pathsToNestedGraph(layerList)
    nodes.value = graph.nodes.map((n) => ({
      ...n,
      style: {
        ...n.style,
        backgroundColor: n.id === props.highlightId 
          ? 'rgba(255, 226, 122, 0.95)' 
          : n.style?.backgroundColor,
        border: n.id === props.highlightId 
          ? '3px solid #f59e0b' 
          : n.style?.border
      }
    }))
  }
}
</script>

<template>
  <div class="vue-flow-wrapper">
    <VueFlow
      :nodes="nodes"
      :edges="edges"
      :fit-view-on-init="true"
      :min-zoom="0.05"
      :max-zoom="2"
      elevate-edges-on-select
      @node-click="onNodeClick"
    >
      <template #node-default="{ data, id }">
        <div class="custom-node" :style="{ opacity: nodes.find(n => n.id === id)?.hidden ? 0 : 1 }">
          <div class="node-header">
            <span class="node-label">{{ data.label }}</span>
            <span v-if="data.hasChildren" class="expand-icon">
              {{ expandedNodes.has(id) ? '−' : '+' }}
            </span>
          </div>
        </div>
        
        <Handle type="source" :position="Position.Right" :id="'source-' + id" />

        <Handle type="target" :position="Position.Left" :id="'target-' + id" />
      </template>
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

.custom-node {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
  transition: opacity 0.3s ease;
}

.node-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 2px 16px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px 8px 0 0;
  position: relative;
  z-index: 100;
  min-height: 50px;
  backdrop-filter: blur(4px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}

.node-label {
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
}

.expand-icon {
  font-size: 20px;
  font-weight: bold;
  color: #3b82f6;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 4px;
  transition: all 0.2s ease;
  flex-shrink: 0;
  margin-left: 8px;
}

.expand-icon:hover {
  background: rgba(59, 130, 246, 0.2);
  transform: scale(1.1);
}
</style>