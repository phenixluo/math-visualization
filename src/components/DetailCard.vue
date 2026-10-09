<template>
  <div class="bg-slate-800 rounded-xl p-4 border-l-4 shadow-lg"
       :style="{ borderLeftColor: batchColor(node.batch) }">
    <!-- 关闭按钮 -->
    <div class="flex justify-end">
      <button @click="$emit('close')" class="text-gray-500 hover:text-white text-lg leading-none">&times;</button>
    </div>

    <!-- 主信息 -->
    <div class="flex items-baseline gap-2 mt-2">
      <span class="text-xl font-bold text-white">{{ node.label }}</span>
      <button @click="speak(node.label)" class="text-xs text-gray-400 hover:text-amber-400 transition" title="听发音">🔊</button>
      <span v-if="node.phonetic && node.phonetic.trim()" class="text-blue-300 text-sm font-mono ml-auto">{{ node.phonetic }}</span>
    </div>
    <p v-if="node.meaning && node.meaning.trim()" class="text-gray-300 text-sm mt-1.5">{{ node.meaning }}</p>
    <p v-if="node.example && node.example.trim()" class="text-green-300/90 text-sm mt-2 bg-green-400/8 border-l-2 border-green-400/50 pl-2 py-1 rounded-r">
      {{ node.example }}
    </p>
    <p v-if="node.mnemonic" class="text-amber-300/90 text-sm mt-2 bg-amber-400/8 border-l-2 border-amber-400/50 pl-2 py-1 rounded-r">
      💡 {{ node.mnemonic }}
    </p>

    <!-- 批次标签 -->
    <div class="mt-2 flex gap-1 flex-wrap">
      <span class="text-xs rounded px-1.5 py-0.5" :style="{ background: batchColor(node.batch)+'22', color: batchColor(node.batch), border: `1px solid ${batchColor(node.batch)}44` }">
        {{ node.batch }}
      </span>
      <span v-if="node.type === 'family'" class="text-xs rounded px-1.5 py-0.5 bg-blue-500/20 text-blue-300 border border-blue-500/30">词族词</span>
    </div>

    <!-- 所属词根提示（词族词显示） -->
    <div v-if="node.type === 'family'" class="mt-2 pt-2 border-t border-slate-700">
      <div class="text-xs text-gray-500">所属词根：</div>
      <div v-for="id in connectedIdsList" :key="id"
           class="inline-flex items-center gap-1 mt-1 text-xs px-2 py-0.5 rounded bg-amber-400/15 text-amber-300 border border-amber-400/30 cursor-pointer hover:bg-amber-400/25 transition"
           @click="$emit('selectNode', nodesById.get(id))">
        <span>{{ nodesById.get(id)?.label }}</span>
        <span v-if="nodesById.get(id)?.phonetic" class="text-blue-300/70">{{ nodesById.get(id)?.phonetic }}</span>
      </div>
    </div>

    <!-- 词族子节点 -->
    <div v-if="clustered && clusters.length > 0" class="mt-3 pt-3 border-t border-slate-700">
      <div class="text-xs text-gray-500 mb-1.5">词族拓展（聚类显示）：</div>
      <div class="space-y-1">
        <div v-for="cluster in clusters" :key="cluster.id" class="border rounded bg-slate-700/30 p-2">
          <div class="flex items-center justify-between mb-1">
            <div class="flex items-center gap-2">
              <button @click.stop="$emit('toggle-cluster', cluster.id)"
                      class="text-xs text-gray-400 hover:text-white">
                {{ (clusteredGroups && clusteredGroups.get(cluster.id)) ? '▼' : '▶' }}
              </button>
              <span class="text-xs rounded px-1.5 py-0.5" :style="{ background: cluster.color+'22', color: cluster.color, border: `1px solid ${cluster.color}44` }">
                {{ cluster.label }}
              </span>
              <span class="text-xs text-gray-400">{{ cluster.count }} 个词</span>
            </div>
            <button @click.stop="speakCluster(cluster)"
                    class="text-xs text-gray-400 hover:text-amber-400">🔊</button>
          </div>
          <!-- 展开的内容 -->
          <div v-if="clusteredGroups && clusteredGroups.get(cluster.id)" class="mt-2 space-y-1">
            <div v-for="id in cluster.nodeIds" :key="id"
                 class="flex items-center gap-2 text-sm py-1 px-2 rounded bg-slate-700/50 hover:bg-slate-700 transition cursor-pointer"
                 @click="$emit('selectNode', nodesById.get(id))">
              <button @click.stop="speak(nodesById.get(id)?.label)"
                      class="text-xs text-gray-400 hover:text-amber-400">🔊</button>
              <span class="text-amber-300 font-semibold">{{ nodesById.get(id)?.label }}</span>
              <span v-if="nodesById.get(id)?.phonetic && nodesById.get(id)?.phonetic.trim()" class="text-blue-300/70 text-xs font-mono">{{ nodesById.get(id)?.phonetic }}</span>
              <span v-if="nodesById.get(id)?.meaning && nodesById.get(id)?.meaning.trim()" class="text-gray-400 text-xs ml-auto">{{ nodesById.get(id)?.meaning }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 传统显示模式（未聚类时） -->
    <div v-else-if="connected?.size > 0" class="mt-3 pt-3 border-t border-slate-700">
      <div class="text-xs text-gray-500 mb-1.5">词族拓展：</div>
      <div class="space-y-1.5">
        <div v-for="id in connected" :key="id" class="flex items-center gap-2 text-sm py-1 px-2 rounded bg-slate-700/50 hover:bg-slate-700 transition cursor-pointer"
             @click="$emit('selectNode', nodesById.get(id))">
          <button @click.stop="speak(nodesById.get(id)?.label)" class="text-xs text-gray-400 hover:text-amber-400">🔊</button>
          <span class="text-amber-300 font-semibold">{{ nodesById.get(id)?.label }}</span>
          <span v-if="nodesById.get(id)?.phonetic && nodesById.get(id)?.phonetic.trim()" class="text-blue-300/70 text-xs font-mono">{{ nodesById.get(id)?.phonetic }}</span>
          <span v-if="nodesById.get(id)?.meaning && nodesById.get(id)?.meaning.trim()" class="text-gray-400 text-xs ml-auto">{{ nodesById.get(id)?.meaning }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { inject, computed } from 'vue'

const props = defineProps({
  node: Object,
  connected: Set,
  clustered: Boolean,
  clusters: Array
})
defineEmits(['speak', 'close', 'selectNode', 'toggle-cluster'])

// 从父组件注入全局节点 Map
const nodesById = inject('nodesById')

// 反向映射：从 clusteredGroups 中获取状态
const clusteredGroups = inject('clusteredGroups') || new Map()

// 词族词的所属根词列表（找父主节点）
const connectedIdsList = computed(() => {
  if (!props.node || props.node.type !== 'family') return []
  const result = []
  // connected 包含当前选中节点的所有家族节点ID
  // 需要找到这些节点的父主节点ID
  const connectedArr = Array.from(props.connected || [])
  for (const id of connectedArr) {
    const n = nodesById.value?.get(id)
    if (n && n.type === 'main' && !result.includes(id)) {
      result.push(id)
    }
  }
  return result
})

function batchColor(batch) {
  return { 'A-B': '#fbbf24', 'C': '#60a5fa', 'D-M': '#a78bfa',
           'N-R': '#34d399', 'S': '#f87171', 'T': '#f472b6',
           'U': '#fbbf24', 'V': '#60a5fa', 'W': '#a78bfa',
           'Y': '#34d399', 'Z': '#f87171' }[batch] || '#fbbf24'
}

function speakCluster(cluster) {
  if (!('speechSynthesis' in window)) return
  window.speechSynthesis.cancel()
  const words = cluster.nodeIds
    .map(id => nodesById.get(id)?.label)
    .filter(Boolean)
    .join(', ')
  const u = new SpeechSynthesisUtterance(words.replace(/[^a-zA-Z\s-]/g, ' ').trim())
  u.lang = 'en-US'
  u.rate = 0.85
  window.speechSynthesis.speak(u)
}
</script>