<template>
  <div class="min-h-screen">
    <!-- 顶层导航 -->
    <nav class="bg-white/10 backdrop-blur-md border-b border-white/20">
      <div class="max-w-7xl mx-auto px-4">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center space-x-2">
            <svg class="w-8 h-8 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
            <span class="text-xl font-bold text-white">可视化学习</span>
          </div>
          <div class="flex items-center space-x-1">
            <button
              v-for="tab in topTabs"
              :key="tab.id"
              @click="currentView = tab.id"
              :class="['nav-link text-white font-medium', currentView === tab.id ? 'active' : '']"
            >
              {{ tab.name }}
            </button>
          </div>
        </div>
      </div>
    </nav>

    <MathView v-if="currentView === 'math'" />
    <EnglishView v-else-if="currentView === 'english'" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import MathView from './views/MathView.vue'
import EnglishView from './views/EnglishView.vue'

const currentView = ref('math')

const topTabs = [
  { id: 'math', name: '数学' },
  { id: 'english', name: '英语' }
]
</script>
