<template>
  <section class="max-w-6xl mx-auto">
    <h2 class="text-2xl font-bold text-white mb-2 text-center">中考词汇联想记忆卡片</h2>
    <p class="text-gray-400 text-sm text-center mb-4">
      深圳中考考纲词汇 · 共 {{ nodeCount }} 个词条节点 · 点击节点查看详情 · 拖拽布局
    </p>

    <!-- 工具栏 -->
    <div class="flex flex-wrap gap-2 justify-center mb-3 items-center">
      <div class="flex flex-wrap gap-1.5 justify-center">
        <button @click="toggleBatch('all')" :class="['pill', { active: activeBatches.has('all') }]">全部</button>
        <button v-for="b in batchList" :key="b.key" @click="toggleBatch(b.key)" :class="['pill', { active: activeBatches.has(b.key) }]" :style="{ '--c': b.color }">{{ b.label }}<span class="ml-1 opacity-60">{{ b.count }}</span></button>
      </div>
      <div class="w-px h-6 bg-slate-600 mx-2"></div>
      <button @click="centerGraph" class="btn-sm" title="重置视图">⟲ 重置</button>
      <button @click="reheat" class="btn-sm" title="重新布局">↻ 重排</button>
      <span class="text-xs text-gray-500 ml-2">仿真中 {{ simNodeIds.size }} / {{ nodeCount }} 节点</span>
    </div>

    <!-- 搜索框 -->
    <div class="max-w-xl mx-auto mb-4 relative">
      <input v-model="search" placeholder="搜索单词…" class="w-full px-4 py-2 pl-9 rounded-lg bg-slate-700 text-white placeholder-gray-400 border border-slate-600 focus:border-amber-500 focus:outline-none transition text-sm" />
      <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-xs">🔍</span>
      <button v-if="search" @click="search = ''" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white text-xs">✕</button>
      <div v-if="search" class="text-center text-gray-500 text-xs mt-1">{{ filteredNodes.length }} 个匹配</div>
    </div>

    <!-- 星形图 + 详情面板 -->
    <div class="flex gap-4 items-start">
      <div class="flex-1 relative" style="min-height:520px">
        <svg ref="svgRef" class="w-full h-[520px] rounded-xl" style="background:rgba(15,23,42,.6)"></svg>
        <div class="absolute bottom-3 left-3 flex gap-4 text-xs text-gray-400 bg-slate-800/80 rounded-lg px-3 py-1.5 pointer-events-none">
          <span>● 主词条</span>
          <span>○ 词族词</span>
          <span class="text-amber-400">→ 词族关联</span>
        </div>
      </div>

      <div v-if="selectedNode" class="w-72 flex-shrink-0 overflow-y-auto max-h-[600px]">
        <DetailCard :node="selectedNode" :connected="connectedNodes" :clustered="isClustered" :clusters="clusterData" :clusteredGroups="clusteredGroups" @speak="speak" @select-node="selectNode" @close="clearSelection" @toggle-cluster="toggleCluster" />
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, watch, provide } from 'vue'
import * as d3 from 'd3'
import DetailCard from './DetailCard.vue'

const NODE_RULES = {
  main: { radius: 18, label: '主词条' },
  family: { radius: 10, label: '词族词' }
}
const BATCH_COLORS = {
  'A-B': '#fbbf24', 'C': '#60a5fa', 'D-M': '#a78bfa',
  'N-R': '#34d399', 'S': '#f87171', 'T': '#f472b6',
  'U': '#fbbf24', 'V': '#60a5fa', 'W': '#a78bfa',
  'Y': '#34d399', 'Z': '#f87171',
}

// ========== 虚拟仿真常量 ==========
const MAX_SIM_NODES = 800  // 仿真中最多节点数
// =================================

const svgRef = ref(null)
const search = ref('')
const activeBatches = ref(new Set(['all']))
const selectedNode = ref(null)
const connectedNodes = ref(new Set())

const CLUSTER_THRESHOLD = 10
const clusteredGroups = ref(new Map())
const isClustered = ref(false)
const clusterData = ref([])

const nodesById = ref(new Map())
provide('nodesById', nodesById)
provide('clusteredGroups', clusteredGroups)

let svg, g, simulation, zoom, nodeGroup, linkGroup
const allNodes = ref([])
const allEdges = ref([])
const nodeCount = ref(0)

// 当前在 D3 simulation 中的节点 ID 集合
const simNodeIds = ref(new Set())
// 当前在 D3 simulation 中的节点/边数组（用于 tick 渲染）
const simNodes = ref([])
const simEdges = ref([])

const filteredNodes = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return allNodes.value
  // 模糊匹配：label 包含搜索词，或搜索词包含 label（仅长词），或意思包含搜索词
  return allNodes.value.filter(n => {
    const label = n.label.toLowerCase()
    const meaning = n.meaning ? n.meaning.toLowerCase() : ''
    return label.includes(q) || (label.length >= 3 && q.includes(label)) || meaning.includes(q)
  })
})

const visibleNodes = computed(() => {
  if (!search.value.trim()) {
    return allNodes.value.filter(n => activeBatches.value.has('all') || activeBatches.value.has(n.batch))
  }
  return filteredNodes.value
})

const baseVisibleEdges = computed(() => {
  const ids = new Set(visibleNodes.value.map(n => n.id))
  return allEdges.value.filter(e => {
    const sid = (e.source?.id !== undefined) ? String(e.source.id) : String(e.source)
    const tid = (e.target?.id !== undefined) ? String(e.target.id) : String(e.target)
    return ids.has(sid) && ids.has(tid)
  })
})

const batchList = computed(() => {
  const counts = {}
  allNodes.value.forEach(n => { if (n.type === 'main') counts[n.batch] = (counts[n.batch] || 0) + 1 })
  return Object.entries(BATCH_COLORS).map(([key, color]) => ({
    key, label: key, color, count: counts[key] || 0
  })).filter(b => b.count > 0)
})

// 邻接表（加载时构建，O(1) 查询）
const adjacencyMap = ref(new Map())

// 获取某个节点的连接节点 ID 集合
function getConnectedIds(nodeId) {
  return adjacencyMap.value.get(nodeId) || new Set()
}

// ========== 核心：构建/重建仿真子集 ==========
function buildSimSubset() {
  const q = search.value.trim().toLowerCase()

  // 如果没有搜索词且没有选中节点，返回空数组（仿真池保持空）
  if (!q && !selectedNode.value) return []

  let candidates

  if (q) {
    // 搜索模式：先找到匹配的 main 节点，再把它们的直连词族节点一并纳入
    const matchedMainIds = new Set(filteredNodes.value.map(n => String(n.id)))
    const relatedIds = new Set(matchedMainIds)
    // 扩展：把每个匹配主词条的邻居（词族词）也加进来
    for (const eid of matchedMainIds) {
      getConnectedIds(eid).forEach(id => relatedIds.add(id))
    }
    candidates = allNodes.value.filter(n => relatedIds.has(String(n.id)))
  } else {
    // 选中节点但无搜索词：只加载选中节点及其直连邻居，不要全部节点
    const selId = String(selectedNode.value.id)
    const relatedIds = new Set([selId])
    getConnectedIds(selId).forEach(id => relatedIds.add(id))
    candidates = allNodes.value.filter(n => relatedIds.has(String(n.id)))
  }

  // 如果选中了节点，始终包含它及其直连邻居
  let requiredIds = new Set()
  if (selectedNode.value) {
    const selId = String(selectedNode.value.id)
    requiredIds.add(selId)
    getConnectedIds(selId).forEach(id => requiredIds.add(id))
  }

  // 排序：required > main > family
  const sorted = [...candidates].sort((a, b) => {
    const aReq = requiredIds.has(String(a.id)) ? 1 : 0
    const bReq = requiredIds.has(String(b.id)) ? 1 : 0
    if (aReq !== bReq) return bReq - aReq
    if (a.type !== b.type) return a.type === 'main' ? -1 : 1
    return String(a.id).localeCompare(String(b.id))
  })

  return sorted.slice(0, MAX_SIM_NODES)
}

function applySimSubset(nodes) {
  const newIds = new Set(nodes.map(n => String(n.id)))
  const newEdges = allEdges.value.filter(e => {
    const sid = (e.source?.id !== undefined) ? String(e.source.id) : String(e.source)
    const tid = (e.target?.id !== undefined) ? String(e.target.id) : String(e.target)
    return newIds.has(sid) && newIds.has(tid)
  })

  simNodes.value = nodes
  simEdges.value = newEdges
  simNodeIds.value = newIds

  simulation.nodes(nodes)
  simulation.force('link').links(newEdges)
  simulation.alpha(0.6).restart()

  // 重建 DOM
  renderDom(nodes, newEdges)
}

function renderDom(nodes, edges) {
  // 节点
  const gSel = nodeGroup.selectAll('g').data(nodes, d => d.id)
  const enter = gSel.enter().append('g').attr('cursor', 'pointer')
    .call(d3.drag()
      .on('start', (e, d) => { if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y })
      .on('drag', (e, d) => { d.fx = e.x; d.fy = e.y })
      .on('end', (e, d) => { if (!e.active) simulation.alphaTarget(0); d.fx = null; d.fy = null })
    )
    .on('click', (e, d) => { e.stopPropagation(); selectNode(d) })
    .on('mouseenter', (e, d) => d3.select(e.currentTarget).select('circle').attr('stroke-width', 3))
    .on('mouseleave', (e, d) => d3.select(e.currentTarget).select('circle').attr('stroke-width', 1.5))

  enter.append('circle')
    .attr('r', d => NODE_RULES[d.type].radius)
    .attr('fill', d => BATCH_COLORS[d.batch] || '#fbbf24')
    .attr('stroke', '#1e293b')
    .attr('stroke-width', d => d.type === 'main' ? 2 : 1.5)

  // 英文单词
  enter.append('text')
    .text(d => d.label)
    .attr('x', d => d.type === 'family' ? 14 : 0)
    .attr('y', d => d.type === 'family' ? 3 : 5)
    .attr('text-anchor', d => d.type === 'family' ? 'start' : 'middle')
    .attr('fill', d => d.type === 'main' ? '#f1f5f9' : '#94a3b8')
    .attr('font-size', d => d.type === 'main' ? '13px' : '11px')
    .attr('font-weight', d => d.type === 'main' ? 600 : 400)
    .style('user-select', 'none').style('pointer-events', 'none')

  // 中文意思（仅在节点半径足够时显示）
  enter.append('text')
    .attr('class', 'node-meaning')
    .text(d => d.type === 'main' && d.meaning ? d.meaning : '')
    .attr('x', 0)
    .attr('y', d => NODE_RULES[d.type].radius + 13)
    .attr('text-anchor', 'middle')
    .attr('fill', '#94a3b8')
    .attr('font-size', d => d.type === 'main' ? '10px' : '0px')
    .attr('font-weight', 400)
    .style('user-select', 'none').style('pointer-events', 'none')

  gSel.exit().remove()

  // 边
  const lineSel = linkGroup.selectAll('line').data(edges, d => {
    const sid = (d.source?.id !== undefined) ? String(d.source.id) : String(d.source)
    const tid = (d.target?.id !== undefined) ? String(d.target.id) : String(d.target)
    return `${sid}-${tid}`
  })
  lineSel.enter().append('line')
    .attr('stroke', 'rgba(148,163,184,0.25)')
    .attr('stroke-width', 1.2)
  lineSel.exit().remove()
}

// ========== 筛选更新 ==========
function applyFilter() {
  const nodes = buildSimSubset()
  applySimSubset(nodes)
}

function toggleBatch(key) {
  if (key === 'all') {
    activeBatches.value = new Set(['all'])
    batchList.value.forEach(b => activeBatches.value.add(b.key))
  } else {
    activeBatches.value.delete('all')
    if (activeBatches.value.has(key)) activeBatches.value.delete(key)
    else activeBatches.value.add(key)
  }
  if (activeBatches.value.size === 0) activeBatches.value = new Set(['all'])
  // 只在有搜索词时才更新仿真池，否则保持空
  if (search.value.trim()) applyFilter()
}

// 选中节点（含动态扩充分子集）
function selectNode(d) {
  selectedNode.value = d
  // 找父主词条，用于展开词族
  let mainId = null
  if (d.type === 'family') {
    const parentIds = Array.from(getConnectedIds(String(d.id)))
    const pid = parentIds.find(id => {
      const p = nodesById.value.get(id)
      return p && p.type === 'main'
    })
    if (pid) mainId = pid
  } else {
    mainId = String(d.id)
  }
  // 无论点击主词条还是词族词，都展开父节点的完整词族
  if (mainId) {
    const childIds = new Set(getConnectedIds(mainId))
    connectedNodes.value = childIds
    checkAndApplyClustering(mainId, Array.from(childIds))
    applyFilter()
  } else {
    connectedNodes.value = new Set()
    isClustered.value = false
    clusterData.value = []
    clusteredGroups.value.clear()
  }
}

function checkAndApplyClustering(mainNodeId, familyNodeIds) {
  isClustered.value = false
  clusterData.value = []
  clusteredGroups.value.clear()

  if (familyNodeIds.length > CLUSTER_THRESHOLD) {
    isClustered.value = true
    const batchesMap = new Map()
    familyNodeIds.forEach(nodeId => {
      const node = nodesById.value.get(nodeId)
      if (node && node.type === 'family') {
        if (!batchesMap.has(node.batch)) batchesMap.set(node.batch, [])
        batchesMap.get(node.batch).push(nodeId)
      }
    })
    clusterData.value = Array.from(batchesMap.entries()).map(([batch, nodeIds]) => ({
      id: `cluster-${batch}-${mainNodeId}`,
      batch, nodeIds,
      label: batch,
      color: BATCH_COLORS[batch] || '#fbbf24',
      count: nodeIds.length
    }))
    clusterData.value.forEach(c => clusteredGroups.value.set(c.id, false))
  }
}

function toggleCluster(clusterId) {
  const current = clusteredGroups.value.get(clusterId) || false
  clusteredGroups.value.set(clusterId, !current)
  if (!selectedNode.value) return
  const cluster = clusterData.value.find(c => c.id === clusterId)
  if (!cluster) return
  if (clusteredGroups.value.get(clusterId)) {
    cluster.nodeIds.forEach(id => connectedNodes.value.add(id))
  } else {
    cluster.nodeIds.forEach(id => connectedNodes.value.delete(id))
  }
}

function clearSelection() {
  selectedNode.value = null
  connectedNodes.value = new Set()
  isClustered.value = false
  clusterData.value = []
  clusteredGroups.value.clear()
  // 清除选择后，如果也有搜索词则重新过滤，否则清空仿真池
  if (search.value.trim()) applyFilter()
  else applySimSubset([])
}

function speak(text) {
  if (!('speechSynthesis' in window)) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text.replace(/[^a-zA-Z\s-]/g, ' ').trim())
  u.lang = 'en-US'; u.rate = 0.85
  window.speechSynthesis.speak(u)
}

function centerGraph() {
  if (!zoom || !svgRef.value) return
  const w = svgRef.value.clientWidth
  const h = svgRef.value.clientHeight
  zoom.translateTo(svg.select('g'), w / 2, h / 2)
}
function reheat() {
  if (simulation) simulation.alpha(0.8).restart()
}

// 搜索变化时也重新评估仿真子集
watch(search, () => applyFilter())

onMounted(async () => {
  const container = svgRef.value.parentElement
  const width = container.clientWidth
  const height = 520

  svg = d3.select(svgRef.value).attr('width', width).attr('height', height)
  g = svg.append('g')
  zoom = d3.zoom().scaleExtent([0.2, 4]).on('zoom', e => g.attr('transform', e.transform))
  svg.call(zoom)
  linkGroup = g.append('g').attr('class', 'links')
  nodeGroup = g.append('g').attr('class', 'nodes')

  simulation = d3.forceSimulation()
    .force('charge', d3.forceManyBody().strength(-8))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide(14))
    .force('link', d3.forceLink().distance(80))
    .alphaDecay(0.015)
    .velocityDecay(0.5)
    .on('tick', () => {
      if (linkGroup) {
        linkGroup.selectAll('line')
          .attr('x1', d => d.source?.x ?? 0).attr('y1', d => d.source?.y ?? 0)
          .attr('x2', d => d.target?.x ?? 0).attr('y2', d => d.target?.y ?? 0)
      }
      if (nodeGroup) {
        nodeGroup.selectAll('g')
          .attr('transform', d => `translate(${d.x ?? 0},${d.y ?? 0})`)
      }
    })

  // 加载字典 JSON
  const resp = await fetch('/vocab_cards.json')
  const data = await resp.json()

  // 准备节点和边数据（带随机初始位置）
  const preparedNodes = data.nodes.map(n => ({
    ...n,
    x: width / 2 + (Math.random() - 0.5) * 100,
    y: height / 2 + (Math.random() - 0.5) * 100
  }))
  const nodeByIdMap = new Map(preparedNodes.map(n => [String(n.id), n]))
  const preparedEdges = data.edges
    .map(e => ({
      source: nodeByIdMap.get(String(e.source)),
      target: nodeByIdMap.get(String(e.target)),
      label: e.label
    }))
    .filter(e => e.source && e.target)

  allNodes.value = preparedNodes
  allEdges.value = preparedEdges
  nodeCount.value = preparedNodes.length
  nodesById.value = nodeByIdMap

  // 构建邻接表（O(1) 查询，避免每次点击遍历全部边）
  const adj = new Map()
  for (const e of preparedEdges) {
    const sid = String(e.source.id)
    const tid = String(e.target.id)
    if (!adj.has(sid)) adj.set(sid, new Set())
    if (!adj.has(tid)) adj.set(tid, new Set())
    adj.get(sid).add(tid)
    adj.get(tid).add(sid)
  }
  adjacencyMap.value = adj

  provide('nodesById', nodesById)
  provide('clusteredGroups', clusteredGroups)

  // 初始不加载任何节点，等待搜索触发
})

window.addEventListener('resize', () => {
  const w = svgRef.value.parentElement.clientWidth
  svg.attr('width', w)
  simulation.force('center', d3.forceCenter(w / 2, 520))
  simulation.alpha(0.3).restart()
})
</script>

<style scoped>
.pill {
  padding: 4px 12px; border-radius: 9999px; font-size: 13px; font-weight: 500;
  background: rgba(255,255,255,0.06); color: #e2e8f0;
  border: 1px solid rgba(255,255,255,0.12); cursor: pointer; transition: all 0.2s;
}
.pill:hover { background: rgba(255,255,255,0.1) }
.pill.active {
  background: color-mix(in srgb, var(--c, #fbbf24) 25%, transparent);
  border-color: var(--c, #fbbf24); color: var(--c, #fbbf24);
}
.btn-sm {
  padding: 4px 10px; border-radius: 6px; font-size: 12px;
  background: rgba(255,255,255,0.06); color: #94a3b8;
  border: 1px solid rgba(255,255,255,0.1); cursor: pointer; transition: all 0.15s;
}
.btn-sm:hover { background: rgba(255,255,255,0.12); color: #e2e8f0 }
</style>
